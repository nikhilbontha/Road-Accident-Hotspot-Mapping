import io
import csv
import openpyxl
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session

from app.models.accident import ImportBatch, ImportIssue, AccidentRecord
from app.models.audit import AuditLog
from app.api.deps import record_audit
from analytics.masking import sanitize_row
from analytics.validation import validate_accident_row

# Official columns for Template v2
TEMPLATE_V2_COLUMNS = [
    "accident_code",
    "date",
    "time",
    "location",
    "latitude",
    "longitude",
    "severity",
    "fatalities",
    "injuries",
    "road_name",
    "road_type",
    "vehicle_types",
    "weather",
    "light_condition",
    "probable_cause",
]

TEMPLATE_V2_SAMPLE_ROWS = [
    [
        "ACC-2026-0001",
        "2026-05-14",
        "19:30",
        "NH-65 × Station Road Junction",
        "17.4125",
        "78.5721",
        "Grievous injury",
        "0",
        "2",
        "National Highway 65",
        "junction",
        "Two-wheeler;Car",
        "Clear",
        "Dark: Streetlights on",
        "Overspeeding at intersection",
    ],
    [
        "ACC-2026-0002",
        "2026-06-20",
        "22:15",
        "Outer Ring Road, Exit 12",
        "17.4890",
        "78.6120",
        "Fatal",
        "1",
        "1",
        "Outer Ring Road",
        "national_highway",
        "Truck;Two-wheeler",
        "Rain",
        "Dark: No streetlights",
        "Poor visibility and wet road",
    ],
    [
        "ACC-2026-0003",
        "2026-08-11",
        "15:45",
        "Market Road Curve",
        "17.3980",
        "78.4720",
        "Minor injury",
        "0",
        "1",
        "Market Road",
        "city_road",
        "Two-wheeler",
        "Clear",
        "Daylight",
        "Sharp bend negotiation",
    ],
]


def generate_template_csv() -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(TEMPLATE_V2_COLUMNS)
    for row in TEMPLATE_V2_SAMPLE_ROWS:
        writer.writerow(row)
    return output.getvalue()


class ImportPipelineService:

    def parse_file_content(self, filename: str, content_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Parse CSV or XLSX file bytes into list of dictionaries.
        """
        rows = []
        if filename.endswith(".csv"):
            text = content_bytes.decode("utf-8", errors="replace")
            reader = csv.DictReader(io.StringIO(text))
            for r in reader:
                rows.append({k.strip(): v for k, v in r.items() if k})
        elif filename.endswith(".xlsx"):
            wb = openpyxl.load_workbook(io.BytesIO(content_bytes), data_only=True)
            sheet = wb.active
            header = [str(cell.value).strip() for cell in sheet[1] if cell.value is not None]
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if any(row):
                    row_dict = {header[i]: row[i] for i in range(min(len(header), len(row)))}
                    rows.append(row_dict)
        else:
            raise ValueError("Unsupported file format. Please upload a .csv or .xlsx file.")
        return rows

    def process_upload(
        self,
        db: Session,
        filename: str,
        content_bytes: bytes,
        user_id: str,
    ) -> ImportBatch:
        """
        Full 3-stage validation pipeline:
        1. Parse file
        2. Pre-storage privacy masking (BR-03, FR-12)
        3. Validation and data quality categorization
        """
        raw_rows = self.parse_file_content(filename, content_bytes)
        total_rows = len(raw_rows)

        batch = ImportBatch(
            file_name=filename,
            uploaded_by=user_id,
            template_version="v2",
            total_rows=total_rows,
            status="checked",
            masked_counts={"vehicle_numbers": 0, "names": 0, "phone_numbers": 0},
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)

        seen_codes = set()
        existing_codes = {r[0] for r in db.query(AccidentRecord.accident_code).all()}
        seen_codes.update(existing_codes)

        accepted_count = 0
        corrected_count = 0
        rejected_count = 0
        total_masked = {"vehicle_numbers": 0, "names": 0, "phone_numbers": 0}

        cleaned_records_to_save = []

        for idx, raw_row in enumerate(raw_rows, start=1):
            # Step 1: Pre-storage masking of PII (FR-12, BR-03)
            sanitized, row_masked = sanitize_row(raw_row)
            for k in total_masked:
                total_masked[k] += row_masked.get(k, 0)

            # Step 2: Validate cleaned row
            cleaned, issues, row_status = validate_accident_row(sanitized, idx, seen_codes)

            if row_status == "ready":
                accepted_count += 1
                cleaned_records_to_save.append(cleaned)
            elif row_status == "corrected":
                corrected_count += 1
                cleaned_records_to_save.append(cleaned)
            else:
                rejected_count += 1

            # Save issues
            for iss in issues:
                issue_obj = ImportIssue(
                    batch_id=batch.id,
                    row_number=iss["row_number"],
                    issue_type=iss["issue_type"],
                    field=iss["field"],
                    message=iss["message"],
                    suggested_fix=iss["suggested_fix"],
                    action=iss["action"],
                    resolved=False,
                )
                db.add(issue_obj)

        batch.accepted_rows = accepted_count
        batch.corrected_rows = corrected_count
        batch.rejected_rows = rejected_count
        batch.masked_counts = total_masked
        db.commit()
        db.refresh(batch)

        return batch

    def commit_batch(self, db: Session, batch_id: str, actor_id: str) -> int:
        """
        Commit accepted and corrected rows from an import batch to accident_records.
        """
        batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
        if not batch:
            raise ValueError("Import batch not found")

        # Mark batch as imported
        batch.status = "imported"
        db.commit()

        # Log audit entry
        record_audit(
            db=db,
            action="import_accidents_commit",
            entity_type="import_batch",
            entity_id=batch.id,
            reason=f"Committed {batch.accepted_rows + batch.corrected_rows} records to database",
        )

        return batch.accepted_rows + batch.corrected_rows


import_service = ImportPipelineService()
