# Assumptions and Decisions Log: Road Accident Hotspot Mapping
**Institution:** Anurag University | **Document ID:** BRD-RAH-001 | **Release:** 1.0 (Full Implementation)

This document records all architectural, algorithmic, domain and environment assumptions made in compliance with BRD-RAH-001 and `docs/SPEC.md`.

---

## 1. Regulatory & Operating Boundary (BR-01, BR-02)
- **Advisory Role Only:** The platform is strictly a geospatial decision-support system. It never modifies road physical geometry, dispatches police/emergency responders, or issues automated electronic citations/challans.
- **Human-in-the-Loop Validation:** All detected hotspots, calculated risk scores, and generated safety recommendations must be reviewed and confirmed by an authorized road safety analyst or authority official. Every AI-assisted insight is explicitly badged as `AI-generated · expert review needed`.

## 2. Privacy & Data Masking (BR-03, FR-12)
- **Pre-Storage Masking:** PII (Personally Identifiable Information) including Indian vehicle registration plates (e.g. `TS 09 AB 1234`, `AP-28-XY-9999`), phone numbers (10-digit Indian mobile formats), person names, and driver licence numbers are stripped or masked prior to database persistence and prior to any LLM prompt formulation.
- **Public Anonymization:** The public endpoint (`/api/v1/public/map`) serves only anonymized, spatially snapped (~500 m grid cells), count-banded aggregations (`10–19`, `20–29`, `30–39`, `40+`). No raw accident records, timestamps, vehicle particulars, or internal assignees are exposed to public viewers.

## 3. Geographic Context & Reference System
- **Default Geographic Center:** Anurag University / Hyderabad Metropolitan Region, Telangana (Center Lat: `17.4200`, Lon: `78.5800`), covering major arteries including National Highway 65 (NH-65), Outer Ring Road (ORR, Exit 12), Market Road, Bypass Road, and Old Town corridors.
- **Coordinate System:** WGS84 (`EPSG:4326`) for persistent storage and GeoJSON transmission; projected metric CRS (e.g. UTM Zone 44N / `EPSG:32644` or Web Mercator `EPSG:3857`) for metric buffer queries and DBSCAN spatial clustering with metric epsilon (`radius_m = 250 m`).
- **Geocoding:** Two-tier geocoding architecture with local persistent cache and synthetic offline fallback for demo road segments, backed by Nominatim / OpenStreetMap with rate limiting and confidence scoring (e.g., 78% for address-only queries).

## 4. Algorithms & Calculations (FR-04, FR-05, FR-07)
- **Spatial Clustering (DBSCAN):** Metric distance clustering on accident coordinates (`eps = radius_m`, default 250 m; `min_samples = min_accidents`, default 5). Centroids are calculated from cluster member points.
- **Insufficient Data Rule:** If the input dataset contains fewer than `min_accidents` records or no cluster satisfies the minimum threshold, the analysis returns `"No reliable hotspot can be determined from this data"` instead of generating hallucinated clusters.
- **Risk Scoring Formula:**
  $$\text{risk\_score} = 100 \times (0.45 \cdot \text{norm\_deaths} + 0.35 \cdot \text{norm\_frequency} + 0.20 \cdot \text{norm\_injuries})$$
  Normalized against max values in the analysis run. Severity weights: Fatal = 10, Grievous injury = 5, Minor injury = 2, Non-injury = 1.
  Default classification thresholds:
  - Critical: $\ge 80$
  - High: $60 - 79$
  - Medium: $40 - 59$
  - Low: $< 40$
- **Override Governance:** Overriding a risk level is restricted to `admin` and `safety_analyst`, requires a mandatory textual rationale, records an immutable entry in `audit_logs`, and dispatches an in-app notification.

## 5. Storage & Asynchronous Task Processing
- **Database:** PostgreSQL 16 + PostGIS extension as primary store. For environments running without direct Docker daemons during unit tests, an in-memory/SQLite with spatial mocks and SQLAlchemy abstraction ensures test suite independence.
- **Caching & Tasks:** Redis for session revocation, dashboard KPI caching, and background task queuing (RQ or FastAPI background tasks with Redis queue tracking).
- **Object Storage:** MinIO (local S3-compatible) for uploaded CSV/XLSX raw files and generated PDF/CSV reports, with local filesystem storage fallback if MinIO is offline.

## 6. Authentication & Roles (FR-01)
- **User Roles:** `admin`, `police_officer`, `safety_analyst`, `authority_official`, `public_viewer`.
- **Pending Approval Workflow:** Newly registered users start in `pending` status. Login returns an informative 403 message (`"Your account is waiting for approval"`) until an administrator explicitly approves the account in User Management.
- **Default Demo Accounts:**
  - `admin`: Dr. Kiran Rao (`admin@demo.in` / `AdminPass123!`)
  - `safety_analyst`: Asha Reddy (`asha@demo.in` / `DemoPass123!`)
  - `police_officer`: Ravi Kumar (`ravi@demo.in` / `DemoPass123!`), Imran Sheikh (`imran@demo.in` / `DemoPass123!`)
  - `authority_official`: Sana Fatima (`sana@demo.in` / `DemoPass123!`), Meera Iyer (`meera@demo.in` / `DemoPass123!`)
  - `deactivated`: Pooja Nair (`pooja@demo.in` / `DemoPass123!`)
  - `pending`: Vikram Singh, Anjali Verma, Harish Babu

## 7. AI Assistant & Recommendations (FR-07, FR-09)
- **Grounded Retrieval:** The LLM client (supporting Gemini, OpenAI, Claude, or a deterministic offline heuristic client) is provided only masked, aggregated database query results (parameterized tool-style retrieval).
- **Safety Citations:** Answers must reference specific hotspot identifiers (`H-0142`, `H-0087`) and time windows (`1 Dec 2025 – 23 Nov 2026`), display caveats for short sample periods, and decline out-of-scope inquiries.

## 8. Frontend & Design Token Fidelity (Part D & 13 Screens)
- **Design Tokens:** Asphalt `#1F2328`, Paper `#F2F3EF`, Card `#FFFFFF`, Line `#DADCD5`, Ink `#1D2125`, Muted `#6A7077`, Lane Accent `#F5B800`.
- **Typography:** Fira Sans with tabular numbers.
- **Layout:** 224 px Asphalt sidebar with yellow dashed lane marking line, 64 px top bar, 10 px radius cards, pill inputs and chips.
- **Reference Screens:** 13 pages matching `docs/Page_01_Landing.png` through `docs/Page_13_Public_Map.png`.
