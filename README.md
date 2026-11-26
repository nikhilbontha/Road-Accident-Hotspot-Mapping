# Road Accident Hotspot Mapping
**Institution:** Anurag University  
**Document ID:** BRD-RAH-001  
**Release:** 1.0 (Full Production Monorepo)

A web-based geospatial decision-support platform that helps traffic police, road safety analysts, and road authorities find, rank, evaluate, and fix accident hotspots (blackspots).

---

## 👤 Project Author & Ownership

| Name | Roll Number | Project Role | Module Coverage |
|---|---|---|---|
| **Nikhil Bontha** | 23EG107E11 | **Lead Full-Stack, AI/GIS & DevOps Engineer** | Complete Architecture, Frontend (React 18 + TS), Backend (FastAPI), Spatial Analytics (DBSCAN/KDE), Database (PostGIS/SQLite), Testing & DevOps |

---

## 🏛️ System Architecture

The product is structured into five distinct, decoupled layers:

1. **Frontend (FE):** React 18, TypeScript, Vite, Tailwind CSS (using asphalt `#1F2328`, paper `#F2F3EF`, lane `#F5B800`, signal risk tokens), Leaflet with OpenStreetMap tiles, Recharts, React Hook Form + Zod.
2. **Backend (BE):** FastAPI (Python 3.11+), Pydantic v2, SQLAlchemy 2, Alembic migrations, JWT access & refresh tokens, OAuth2 password flow, and strict role guards (`admin`, `police_officer`, `safety_analyst`, `authority_official`, `public_viewer`).
3. **Analytics & AI Engine (`analytics/`):**
   - Equirectangular metric projection (`project_to_meters`)
   - DBSCAN spatial clustering ($eps=250\text{ m}$, $min=5\text{ crashes}$)
   - 2D Gaussian Kernel Density Estimation (KDE) heat surface
   - Multi-criteria risk scoring ($45\% \text{ fatalities} + 35\% \text{ frequency} + 20\% \text{ injuries}$)
   - 8 temporal 3-hour bins factor analysis & rule-based recommendation generator
   - Grounded tool-style AI Insights Assistant with citation of hotspot codes and date periods
4. **Database & Storage (DB):**
   - PostgreSQL 16 + PostGIS extension (SQLite fallback for portable testing)
   - Redis for caching, sessions, and asynchronous background tasks
   - MinIO (S3-compatible) for raw and validated accident uploads
5. **DevOps & Observability:**
   - Multi-stage Docker containers orchestrated via `docker compose`
   - Prometheus metrics (`/api/v1/metrics`) & Grafana dashboards
   - GitHub Actions CI/CD workflows for linting, type-checking, testing, and container builds

---

## 🔑 Pre-Seeded Demo Accounts

All demo accounts share the password: `Password123!` (or `DemoPass123!`).

| User | Role | Department / Organisation | Status |
|---|---|---|---|
| **Dr. Kiran Rao** | `admin` | State Road Safety Council | Active |
| **Asha Reddy** | `safety_analyst` | Road Safety Analysis Cell | Active |
| **Ravi Kumar** | `police_officer` | Hyderabad Traffic Police | Active |
| **Imran Sheikh** | `police_officer` | Cyberabad Traffic Police | Active |
| **Sana Fatima** | `authority_official` | HMDA Road Infrastructure | Active |
| **Meera Iyer** | `authority_official` | Municipal Corporation (GHMC) | Active |
| **Pooja Nair** | `safety_analyst` | Former Safety Consultant | Deactivated |
| **Vikram Singh** | `police_officer` | Traffic Enforcement Unit | Pending Approval |
| **Anjali Verma** | `authority_official` | State Highway Authority | Pending Approval |
| **Harish Babu** | `safety_analyst` | Data Intelligence Division | Pending Approval |

---

## 🚀 How to Run the Servers

You can run the application either **locally with Python & Node.js** (recommended for quick development and live demonstration) or **fully containerized via Docker Compose**.

---

### Option A: Local Setup (Fastest & Zero-Config SQLite)

#### 1. Setup & Environment
```bash
# Clone the repository
git clone https://github.com/nikhilbontha/Road-Accident-Hotspot-Mapping.git
cd Road-Accident-Hotspot-Mapping

# Copy environment file
cp .env.example .env
```

#### 2. Start Backend Server (FastAPI)
```bash
# Open Terminal 1:
cd backend

# Create & activate virtual environment:
python -m venv venv

# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install Python requirements:
pip install -r requirements.txt

# (Optional: database comes pre-seeded with 4,812 crashes & 47 blackspots; to re-seed anytime run:)
python ../scripts/seed_demo_data.py

# Launch FastAPI application:
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
* **Backend API:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health Check Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

#### 3. Start Frontend Server (React + Vite)
```bash
# Open Terminal 2:
cd frontend

# Install Node dependencies:
npm install

# Start Vite dev server:
npm run dev -- --host 127.0.0.1 --port 5173
```
* **Web Application:** [http://127.0.0.1:5173](http://127.0.0.1:5173)
* **Public Awareness Map:** [http://127.0.0.1:5173/public](http://127.0.0.1:5173/public)

---

### Option B: Docker Compose (Full Production Multi-Container Stack)

To run the complete production environment (FastAPI, React, PostgreSQL 16 + PostGIS, Redis, MinIO, Prometheus, Grafana):

```bash
docker compose up --build
```

**Service Endpoints:**
* **Frontend App:** [http://localhost](http://localhost) (or `http://localhost:5173`)
* **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Prometheus Metrics:** [http://localhost:9090](http://localhost:9090)
* **Grafana Dashboards:** [http://localhost:3001](http://localhost:3001) (Credentials: `admin` / `admin`)
* **MinIO Object Console:** [http://localhost:9001](http://localhost:9001) (Credentials: `minioadmin` / `minioadmin`)

---

## 🧪 Verification & Testing

### Backend Unit & Integration Tests (pytest)
```bash
python -m pytest backend/tests/ -v
```
All **26 tests** pass:
- RBAC guards & Admin User Management flow
- Authentication, Token Refresh & Pending Approval restriction
- Data Import pipeline, Privacy Masking, & Validation
- Analytics DBSCAN clustering, KDE heat surface, Risk Scoring, & 50,000-record performance benchmark
- Map GeoJSON, Case lifecycle, & Public 500m grid-snapped anonymization
- Dashboard KPIs, Notifications, PDF/CSV Reports, & Grounded AI Assistant

### Frontend Component & Form Tests (Vitest)
```bash
cd frontend
npm test
```
All **6 tests** pass:
- Zod validation schemas for registration, password strength, and department policy agreements
- Color token mappings for signal risk levels
- Mandatory Human-in-the-Loop badge presence

### Performance Benchmark
- **50,000 synthetic records:** DBSCAN clustering + KDE heat surface + Risk scoring processed in **1.33 seconds** ($\le 120\text{ s}$ target passed with $>98\%$ margin).
- **Map & Dashboard APIs:** Sub-50ms indexed response time ($\le 3\text{ s}$ target passed).

---

## 📑 13 Implemented Reference Screens

All 13 screens are fully implemented and visually matched to `docs/Page_*.png`:
1. `Page_01_Landing.tsx` (`/`) – Asphalt hero, 7-step process line, feature showcase, 4 personas, safe advice banner, public map CTA.
2. `Page_02_Signup.tsx` (`/signup`) – Split-screen, concentric risk circles, department policy checkbox, pending approval flow.
3. `Page_03_Login.tsx` (`/login`) – Split-screen, role login, public map link, quick demo account switcher.
4. `Page_04_Dashboard.tsx` (`/dashboard`) – 5-KPI ribbon with YoY deltas, monthly accident line + fatality bars, risk distribution, 7-day $\times$ 8-block heat grid, priority blackspots table.
5. `Page_05_Hotspot_Map.tsx` (`/map`) – Full-bleed interactive Leaflet map, KDE heat surface, ranked blackspot markers, floating filter panel, hotspot dossier card.
6. `Page_06_Data_Import.tsx` (`/import`) – 4-step wizard, automatic PII masking stats, data quality bar, review issues table with fix/skip/accept, template download.
7. `Page_07_Hotspot_Cases.tsx` (`/cases`) – Status tabs with counts, risk filter chips, official assignment picker, case table, CSV export.
8. `Page_08_Hotspot_Detail.tsx` (`/cases/:code`) – 6-step lifecycle stepper, score breakdown stacked bar, 8-bin time-of-day chart, AI recommendations with confidence tags, before/after impact evaluation panel.
9. `Page_09_AI_Assistant.tsx` (`/assistant`) – Grounded chat citing hotspot codes and dates, suggestion chips, right "Data behind this answer" panel with mini map.
10. `Page_10_Reports.tsx` (`/reports`) – Report configurator (Summary, Trends, Intervention), PDF/CSV generation, live paper-style preview sheet.
11. `Page_11_User_Management.tsx` (`/users`) – Admin user management, pending approval yellow-edged banner, approve/reject/deactivate controls, role switcher.
12. `Page_12_Notifications.tsx` (`/notifications`) – Today / Earlier groups, unread indicators, "Tell me when" event toggles.
13. `Page_13_Public_Map.tsx` (`/public`) – Clean public navigation, 500m grid-snapped anonymized hazard bands, zero individual crash points or personal identifiers.

---

## 🔒 Security & Privacy Safeguards (BR-01 to BR-08)

- **BR-01 & BR-02 (Human-in-the-Loop):** The platform is strictly advisory. It never automatically dispatches emergency services, issues e-challans, or makes civil changes. Every AI output displays the mandatory label: `AI-generated · expert review needed`.
- **BR-03 & FR-12 (PII Redaction):** Indian vehicle numbers, phone numbers, and driver names are masked before database persistence and LLM processing.
- **BR-08 (Public Anonymity):** Public endpoints return only aggregated, ~500m grid-snapped accident count bands (`10–19`, `20–29`, `30–39`, `40+`). No raw coordinates, victim names, or vehicle plates are ever exposed.
- **Append-Only Audit Trail:** All imports, analysis runs, assignments, status transitions, and risk level overrides with mandatory justifications are recorded in `audit_logs`.
