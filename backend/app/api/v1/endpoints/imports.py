from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, require_roles
from app.models.user import User, UserRoleEnum
from app.models.accident import ImportBatch, ImportIssue
from app.services.import_service import import_service, generate_template_csv

router = APIRouter(prefix="/imports", tags=["Data Import"])

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB


@router.get("/template")
def download_template() -> Any:
    """
    Download the standard CSV import template v2 (FR-02).
    """
    csv_data = generate_template_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="accident_data_template_v2.csv"'},
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_import_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.ADMIN, UserRoleEnum.POLICE_OFFICER, UserRoleEnum.SAFETY_ANALYST])),
) -> Any:
    """
    Upload accident dataset (CSV or XLSX, <= 25 MB).
    Executes automated privacy masking, schema validation, and geocoding (FR-02, FR-03, FR-12).
    """
    if not (file.filename.endswith(".csv") or file.filename.endswith(".xlsx")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a .csv or .xlsx file.",
        )

    content_bytes = await file.read()
    if len(content_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 25 MB limit.",
        )

    try:
        batch = import_service.process_upload(
            db=db,
            filename=file.filename,
            content_bytes=content_bytes,
            user_id=current_user.id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

    return {
        "id": batch.id,
        "file_name": batch.file_name,
        "total_rows": batch.total_rows,
        "accepted_rows": batch.accepted_rows,
        "corrected_rows": batch.corrected_rows,
        "rejected_rows": batch.rejected_rows,
        "masked_counts": batch.masked_counts,
        "status": batch.status,
        "created_at": batch.created_at,
    }


@router.get("/{batch_id}")
def get_batch(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get import batch metadata and summary.
    """
    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")
    return {
        "id": batch.id,
        "file_name": batch.file_name,
        "total_rows": batch.total_rows,
        "accepted_rows": batch.accepted_rows,
        "corrected_rows": batch.corrected_rows,
        "rejected_rows": batch.rejected_rows,
        "masked_counts": batch.masked_counts,
        "status": batch.status,
        "created_at": batch.created_at,
    }


@router.get("/{batch_id}/issues")
def get_batch_issues(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all detected validation issues for the import batch.
    """
    issues = db.query(ImportIssue).filter(ImportIssue.batch_id == batch_id).order_by(ImportIssue.row_number.asc()).all()
    return [
        {
            "id": i.id,
            "row_number": i.row_number,
            "issue_type": i.issue_type,
            "field": i.field,
            "message": i.message,
            "suggested_fix": i.suggested_fix,
            "action": i.action,
            "resolved": i.resolved,
        }
        for i in issues
    ]


@router.patch("/{batch_id}/issues/{issue_id}")
def update_issue_action(
    batch_id: str,
    issue_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.ADMIN, UserRoleEnum.POLICE_OFFICER, UserRoleEnum.SAFETY_ANALYST])),
) -> Any:
    """
    Update review action for an issue (fix, skip, accept, done).
    """
    issue = db.query(ImportIssue).filter(ImportIssue.id == issue_id, ImportIssue.batch_id == batch_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    new_action = payload.get("action")
    if new_action:
        issue.action = new_action
    if "resolved" in payload:
        issue.resolved = payload["resolved"]

    db.commit()
    return {"message": "Issue action updated", "id": issue.id, "action": issue.action}


@router.post("/{batch_id}/commit")
def commit_import_batch(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.ADMIN, UserRoleEnum.POLICE_OFFICER, UserRoleEnum.SAFETY_ANALYST])),
) -> Any:
    """
    Commit validated records into persistent accident_records table.
    """
    try:
        committed_count = import_service.commit_batch(db=db, batch_id=batch_id, actor_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": f"Successfully committed {committed_count} accident records",
        "committed_records": committed_count,
        "batch_id": batch_id,
    }
