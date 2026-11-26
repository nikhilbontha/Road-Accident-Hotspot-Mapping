# Road Accident Hotspot Mapping - Full Specification (SPEC.md)

# PART B: PRODUCT SUMMARY

**What it is:** A web-based geospatial decision-support platform that helps traffic police, road safety analysts and road/transport authorities find, rank and fix accident hotspots (black spots).

**Core value chain:** Collect → Validate → Analyze → Map → Prioritize → Recommend → Track.

**Users and roles (RBAC):** `admin`, `police_officer` (Traffic Police Officer), `safety_analyst` (Road Safety Analyst), `authority_official` (Road Authority Official), `public_viewer` (no account; public page only).

**Role–permission matrix (enforce in the API, not just the UI):**

| Capability | admin | police_officer | safety_analyst | authority_official | public_viewer |
|---|---|---|---|---|---|
| Manage users and roles | Yes | No | No | No | No |
| Import / create accident records | Yes | Yes | Yes | No | No |
| Run hotspot analysis | Yes | Yes | Yes | No | No |
| View hotspot map | Yes | Yes | Yes | Yes | Aggregated only |
| Assign hotspots for action | Yes | Yes | No | Yes | No |
| Update status / add comments | Yes | Yes | Yes | Yes | No |
| Override risk level | Yes | No | Yes | No | No |
| Use AI insights assistant | Yes | Yes | Yes | Yes | No |
| View dashboard and analytics | Yes | Yes | Yes | Yes | Aggregated only |
| Export reports | Yes | Yes | Yes | Yes | No |

**Out of scope (do not build):** autonomous road/engineering changes; automatic enforcement (e-challan) or emergency dispatch; replacing national/state systems (iRAD/eDAR); real-time live GPS/traffic streaming (manual upload only); profiling individual drivers, victims or vehicles. **Future only (do not build, but keep the code extensible):** iRAD/FIR integration, live traffic/weather feeds, predictive forecasting, mobile app, email/SMS, feedback learning.

---

# PART C: ARCHITECTURE AND TECH STACK (follow the architecture image)

Five layers plus testing. Keep each layer in its own module with clear interfaces.

| Layer | Technology |
|---|---|
| **Frontend (FE)** | React 18 + TypeScript SPA, Vite, React Router, TanStack Query, Tailwind CSS (design tokens in Part D), Leaflet or MapLibre GL with OpenStreetMap tiles (no paid key), Recharts (or hand-built SVG) for charts, React Hook Form + Zod |
| **Backend (BE)** | FastAPI (Python 3.11+), Pydantic v2, SQLAlchemy 2 + Alembic, JWT auth (access + refresh), OAuth2 password flow, RBAC dependency guards, REST over HTTPS, OpenAPI docs. Services: **Accident API** (CRUD), **Data Service** (import, validate, mask), **Hotspot Service** (analysis, risk), **Notify Service** (alerts and events), **Auth Service** (JWT, OAuth2, RBAC) |
| **Analytics / AI** | Python package `analytics/`: pandas, GeoPandas, Shapely, scikit-learn (DBSCAN), SciPy/scikit-learn KDE. Pipeline: Data Validation & Geocoding → Hotspot Detection (KDE / DBSCAN) → Risk Scoring & Classification → Factor Analysis & Recommendations. **LLM provider** (Claude or GPT API behind a `LLMClient` interface, selected by env var) powers only the AI Insights Assistant and optional wording of recommendation text. |
| **Database & Storage (DB)** | **PostgreSQL + PostGIS** (accidents, hotspots, users, audit), **Redis** (sessions, cache, task queue; use RQ or Celery for background analysis jobs), **Object storage** (MinIO locally, AWS S3 in cloud) for uploaded files, **OpenStreetMap / Nominatim** for map tiles and geocoding (cache results, respect rate limits, allow a swappable provider) |
| **DevOps & Deployment** | Docker (one image per service) → GitHub (source) → GitHub Actions (CI/CD) → AWS or Azure (deployment) → Prometheus (monitoring) → Grafana (dashboards) |
| **Testing (QA)** | pytest + httpx (backend), Vitest + Testing Library (frontend), Playwright (end-to-end + visual checks), Postman/Newman collection, data-validation tests |

**Project Author and Ownership:** Nikhil Bontha (23EG107E11) – Full-Stack Engineering, Spatial Analytics & GIS, Database & PostGIS, Testing & QA, Deployment & DevOps.

**Repository layout:**
```
road-accident-hotspot-mapping/
├─ docs/                      # BRD, architecture, Page_*.png, SPEC.md, ASSUMPTIONS.md
├─ frontend/                  # React SPA
├─ backend/
│  ├─ app/ (api/, core/, models/, schemas/, services/, tasks/)
│  ├─ analytics/              # validation, geocoding, masking, hotspots, scoring, factors, recommendations
│  ├─ alembic/  ├─ tests/  └─ Dockerfile
├─ infra/ (docker-compose.yml, prometheus/, grafana/, nginx/, terraform-or-bicep/ optional)
├─ scripts/ (seed_demo_data.py, generate_templates.py)
├─ .github/workflows/ (ci.yml, cd.yml)
├─ .env.example  └─ README.md
```

---

# PART D: DESIGN SYSTEM (match the reference screens)

**Mood:** a road-safety control room. Asphalt-dark navigation, signal colours for risk, road-marking yellow as the single accent.

**Colour tokens**
- `--asphalt #1F2328` (sidebar, dark panels, primary dark buttons)
- `--paper #F2F3EF` (page background), `--card #FFFFFF`, `--line #DADCD5`
- `--ink #1D2125` (text), `--muted #6A7077`
- `--lane #F5B800` (accent: primary buttons, active nav marker, step highlights)
- Risk: `--crit #C62F2A`, `--high #E2762B`, `--med #E7B416` (dark text on it), `--low #3E8E62`
- Status dots: Identified `#9AA0A6`, Under review `#F5B800`, Assigned `#2F6FB5`, Action in progress `#E2762B`, Implemented `#3E8E62`, Closed `#1F2328`
- Link/inline accent text on light: `#8A6A00`. Warning note background `#FFF3C4` with text `#6B5200`.

**Type:** Fira Sans only (400, 500, 600), tabular numerals on. Page title 19–22 px/600; card title 14.5 px/600; body 14 px; table 13.3 px; helper text 12.5 px muted. Sentence case everywhere, no all-caps labels.

**Layout:** app shell = left sidebar 224 px (asphalt, a dashed yellow “lane marking” line down its right edge, active item has a yellow left bar and tinted background) + top bar 64 px (white, page title and one-line subtitle on the left; filters/actions and a notifications bell with a red dot on the right) + content area with 20–28 px padding on `--paper`. Cards: white, 1 px `--line` border, 10 px radius, 16–18 px padding. Buttons: 8 px radius; primary = `--lane` fill with dark text; secondary = white with border. Chips: pill shaped, risk colours. Floating panels on the map: white, 12 px radius, soft shadow. Inputs look like “pills” with a 1 px border.

**Sidebar items (in order):** Dashboard, Hotspot Map, Data Import, Hotspot Cases, AI Assistant, Reports, then a divider and User Management (admin only). Footer: user avatar initials, name, role. Brand: yellow rounded square with map-pin icon + “Hotspot Mapping”.

**Copy rules:** plain verbs, active voice, names stay the same across a flow (the button “Assign hotspot” produces the toast “Hotspot assigned”). Errors say what happened and how to fix it. Empty states invite an action. Every AI output carries the label **“AI-generated · expert review needed”**.

**Quality floor:** responsive down to tablets (≥768 px) with the sidebar collapsing, visible keyboard focus, WCAG AA contrast, reduced-motion respected, loading skeletons and error states on every data view.

---

# PART E: DATA MODEL (PostgreSQL + PostGIS)

Use UUID primary keys, `created_at/updated_at`, and PostGIS `geometry(Point,4326)` with GiST indexes.

- **users**: id, full_name, email (unique), organisation, role (enum), password_hash (bcrypt/argon2), status (`pending|active|deactivated`), last_active_at.
- **import_batches**: id, file_name, object_key, uploaded_by, template_version, total_rows, accepted_rows, corrected_rows, rejected_rows, masked_counts (JSON: vehicle_numbers, names, phone_numbers), status (`uploaded|checked|reviewed|imported|failed`), created_at.
- **import_issues**: id, batch_id, row_number, issue_type, field, message, suggested_fix, action (`fix|skip|accept|done`), resolved bool.
- **accident_records**: id, accident_code (unique, e.g. `ACC-2026-01882`), occurred_at (date + time), geom, latitude, longitude, location_text, geocode_confidence, road_name, road_type (`national_highway|city_road|junction|other`), severity (`fatal|grievous_injury|minor_injury|non_injury`), fatalities, injuries, vehicle_types (array), weather, light_condition, probable_cause, source_batch_id, flags (e.g. `needs_correction`). **No personal identifiers are ever stored** (masked or dropped before insert).
- **analysis_runs**: id, run_number, started_by, parameters (JSON: radius_m default 250, min_accidents default 5, period, severity_weights, algorithm), status, record_count, duration_ms, created_at.
- **hotspots**: id, code (`H-0142`), name, geom (centroid) + boundary geometry, road_name, area/zone, accidents_count, fatalities, injured, period_start/end, risk_score (0–100), score_breakdown (JSON: deaths, frequency, injuries), risk_level (`critical|high|medium|low`), risk_overridden bool, status (lifecycle enum), assignee_id, peak_time_text, analysis_run_id, updated_at.
- **hotspot_accidents**: hotspot_id, accident_id.
- **hotspot_factors**: hotspot_id, factor_key, label, count, percent (two-wheelers, poor lighting at night, overspeeding, wet road, no pedestrian crossing, etc.), plus time-block counts (8 blocks of 3 hours) stored in JSON.
- **recommendations**: id, hotspot_id, title, linked_factor, evidence_text, confidence (`high|medium|low`), is_ai_generated true, reviewed_by, reviewed_at.
- **hotspot_comments**: id, hotspot_id, user_id, body, created_at.
- **hotspot_interventions**: id, hotspot_id, description, implemented_on, recorded_by (used for before/after comparison).
- **audit_logs** (append-only): id, actor_id, action, entity_type, entity_id, before (JSON), after (JSON), reason, created_at. Revoke UPDATE/DELETE from the app DB role and add a trigger that blocks edits (FR-13b).
- **notifications**: id, user_id, type (`critical_detected|assigned|risk_changed|action_implemented`), title, body, entity_id, is_read, created_at. **notification_settings**: user_id, one boolean per type.
- **chat_conversations / chat_messages**: id, user_id, role, content, cited_hotspot_ids, created_at.
- **reports**: id, type, params (JSON), format (`pdf|csv`), object_key, created_by, created_at.
- **system_settings**: scoring weights, risk thresholds (default Critical ≥ 80, High 60–79, Medium 40–59, Low < 40), severity weights, allowed file types, max file size (25 MB), geographic bounds.

---

# PART F: BACKEND, ANALYTICS RULES AND API

## F1. Authentication and access (FR-01)
- Register creates a user with `status=pending`. Login is refused with a clear message (“Your account is waiting for approval”) until an admin approves. Invalid credentials → generic error. Deactivated users cannot log in.
- JWT access (short) + refresh tokens; password hashing; rate-limit login; HTTPS only in deployment. Redis stores sessions/refresh state.
- Guard every route with role dependencies from the matrix. Public endpoints return **aggregated, anonymized** data only (BR-08).

## F2. Import and validation (FR-02, FR-03, FR-12)
Pipeline when a file is uploaded (CSV/XLSX, ≤ 25 MB; reject others with a clear message; provide a downloadable template v2 with required columns: date, time, location, severity; optional: latitude, longitude, road name/type, fatalities, injuries, vehicle types, weather, light condition, probable cause):
1. Store the raw file in object storage (access restricted).
2. **Mask first (BR-03, FR-12):** detect and mask/drop vehicle registration numbers (Indian format regex such as `[A-Z]{2}[ -]?\d{1,2}[ -]?[A-Z]{1,3}[ -]?\d{4}`), phone numbers, names (known name columns and pattern-based detection), licence numbers. Count what was masked per type. Masking runs **before** any storage of rows, any analysis and any LLM call.
3. **Validate:** required fields; date/time formats (e.g. “25:10” invalid); latitude/longitude within valid bounds; negative counts; duplicates (same time, place and severity within tolerance, or same `accident_code`); standardize categories (e.g. “Grevious” → “Grievous injury”, “foggy” → “Fog”).
4. **Geocode** address-only rows via the geocoding provider with a stored confidence (e.g. 78%); flag low confidence.
5. Output a **data quality report**: accepted, corrected (auto-fixed), rejected (needs attention), plus an issues list with row, what was found, field, suggested fix, action.
6. User reviews issues (fix / skip / accept), then **Import N records**. Rejected rows stay out until fixed and can be re-submitted. Every import is logged in `audit_logs`.

## F3. Hotspot detection (FR-04)
- Inputs: validated accidents in the chosen period/area, user-configurable parameters (search radius default 250 m, minimum accidents default 5, period default 12 months, severity weighting).
- Algorithm: project to a metric CRS; run **DBSCAN** (eps = radius, `min_samples` = minimum accidents) for clusters on roads/junctions; compute **KDE** surface for the heatmap layer; snap cluster centroids to the nearest road/junction when road data is available.
- Store parameters with every result so runs are **reproducible**.
- **Insufficient data rule:** if there are fewer records than the minimum or no cluster meets the threshold, return “No reliable hotspot can be determined from this data” instead of guessing.
- Run long analyses as background jobs (Redis queue) with status polling; handle failures gracefully (clear message, data saved, retry).

## F4. Risk scoring and classification (FR-05)
- Severity weights (configurable): fatal 10, grievous injury 5, minor injury 2, non-injury 1.
- `risk_score = 100 × (0.45·norm_deaths + 0.35·norm_frequency + 0.20·norm_injuries)`, each term normalised against the highest value among hotspots in the run. Save the breakdown (deaths, frequency, injuries points) so the UI can show **“Why the score is 92”**.
- Level thresholds from `system_settings` (Critical ≥ 80, High 60–79, Medium 40–59, Low < 40). Admin can edit weights and thresholds; the UI displays them.
- Override by `admin` or `safety_analyst` requires a reason; store `risk_overridden`, write an audit entry (user, time, reason, old → new) and trigger a notification.
- A newly detected **Critical** hotspot triggers notifications to relevant users (BR-06).

## F5. Contributing factors and recommendations (FR-07)
- Per hotspot compute: accidents by 3-hour block (12a, 3a, 6a, 9a, 12p, 3p, 6p, 9p), by weekday, weather, light condition, road type, vehicle type, recorded causes; factor percentages (e.g. two-wheelers 58%, poor lighting at night 46%, overspeeding 34%, wet road 21%, no pedestrian crossing 18%); peak time text (e.g. “6–9 pm, Fri–Sat”).
- Recommendations come from a **rule table** mapping factors to interventions (lighting → high-mast lighting; overspeeding → warning signs and rumble strips; two-wheeler conflicts → protected turning lane; pedestrian exposure → marked crossing with refuge island; wet road → drainage/anti-skid surfacing; junction conflicts → signal/junction redesign; enforcement where relevant).
- Each recommendation stores: linked factor, **evidence** (e.g. “23 of 41 crashes happened between 6 pm and midnight”), **confidence** High/Medium/Low (configurable heuristic using share of accidents, sample size and how complete the field is; tune so the seeded H-0142 shows High for lighting, Medium for overspeeding and two-wheelers, Low for the crossing).
- The LLM may only rephrase titles/evidence text; it never invents numbers. Always label **AI-generated · expert review needed** (BR-01).

## F6. Tracking and audit (FR-08, FR-13)
- Lifecycle: **Identified → Under review → Assigned → Action in progress → Implemented → Closed**; may be **Reopened** from Implemented or Closed. Enforce valid transitions server-side.
- Assign (authorised roles only), comment (timestamped, attributed), record intervention with date, **before/after comparison** (accidents in equal windows before and after the intervention date; show counts and % change with the caveat that short windows are indicative only).
- Log to `audit_logs`: imports, record edits, analysis runs, assignments, status changes, risk overrides, comments. Records cannot be edited by regular users.

## F7. Notifications (FR-10)
In-app only. Events: critical hotspot detected, hotspot assigned, risk level changed, action marked implemented. Only relevant users receive them (assignee, role-appropriate owners). Users can list, filter All/Unread, mark one/all as read, and toggle each event type in settings. Email/SMS are explicitly “not available yet”.

## F8. Dashboard and reports (FR-11)
- KPIs: total accidents, fatalities, injured, hotspots identified (and how many critical), actions implemented (and how many in progress); each with change vs previous 12 months where meaningful.
- Charts: accidents by month (line) with fatalities per month (bars); hotspots by risk level; day-of-week × 3-hour heat grid; accidents by severity, road type and area; top hotspots needing action first.
- All figures must equal the underlying data; filter by date range, area (and environment/road type where relevant). Dashboard and map load ≤ 3 s using indexed queries and Redis caching.
- Reports: types **Hotspot summary, Monthly trends, Intervention impact**; filters period/area/risk levels; formats PDF (WeasyPrint or ReportLab) and CSV; stored in object storage and listed under “Recent reports”.

## F9. AI Insights Assistant (FR-09)
- Chat endpoint with conversation history. Implement **tool-style retrieval**: the backend runs parameterised queries (top hotspots by area/time, factor summary, night-time deaths, before/after for an intervention, current status) and gives the LLM **only masked, aggregated results**.
- Answers must be grounded in stored data, cite hotspot IDs and the data period (“Based on H-0142, H-0087 and H-0215 · 1 Dec 2025 – 23 Nov 2026”), include caveats (short windows, confounders), and politely refuse out-of-scope questions.
- Suggested prompts shown as chips. If the LLM times out or errors, show a clear message and let the user retry; nothing is lost.

## F10. REST API (prefix `/api/v1`; all return JSON; paginate lists; OpenAPI documented)
- **Auth:** `POST /auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `GET /auth/me`
- **Users (admin):** `GET/POST /users`, `PATCH /users/{id}` (role, status), `POST /users/{id}/approve`, `POST /users/{id}/reject`, `POST /users/{id}/deactivate`
- **Accidents:** `GET/POST /accidents`, `GET/PATCH /accidents/{id}`, filters (date, severity, time of day, road type, weather, vehicle type, area)
- **Imports:** `GET /imports/template`, `POST /imports` (upload), `GET /imports/{id}`, `GET /imports/{id}/issues`, `PATCH /imports/{id}/issues/{issue_id}`, `POST /imports/{id}/commit`
- **Analysis:** `POST /analysis/runs`, `GET /analysis/runs/{id}` (status), `GET /analysis/settings`, `PUT /analysis/settings` (admin)
- **Map:** `GET /map/hotspots` (GeoJSON), `GET /map/accidents` (GeoJSON, clustered), `GET /map/heat` (KDE grid), `GET /public/map` (aggregated, ~500 m grid areas, count bands such as 10–19, 20–29, 30–39, 40+)
- **Hotspots/cases:** `GET /hotspots` (search + filters: status, risk, assignee, area, updated), `GET /hotspots/{id}`, `POST /hotspots/{id}/assign`, `POST /hotspots/{id}/status`, `POST /hotspots/{id}/risk-override`, `POST /hotspots/{id}/comments`, `POST /hotspots/{id}/interventions`, `GET /hotspots/{id}/factors`, `GET /hotspots/{id}/recommendations`, `GET /hotspots/{id}/activity`
- **Dashboard:** `GET /dashboard/summary`, `/dashboard/monthly`, `/dashboard/risk-distribution`, `/dashboard/heat-grid`, `/dashboard/top-hotspots`
- **Reports:** `GET /reports`, `POST /reports`, `GET /reports/{id}/download`
- **Notifications:** `GET /notifications`, `POST /notifications/{id}/read`, `POST /notifications/read-all`, `GET/PUT /notifications/settings`
- **Assistant:** `POST /assistant/chat`, `GET /assistant/conversations`
- **Ops:** `GET /health`, `GET /metrics` (Prometheus)

---

# PART G: PAGES (13). Build each to match its reference image

Routes and access: `/` Landing (public) · `/signup` · `/login` · `/dashboard` · `/map` · `/import` · `/cases` · `/cases/:code` · `/assistant` · `/reports` · `/users` (admin) · `/notifications` · `/public` (public). Unauthenticated users hitting app routes go to `/login`. Use the exact demo copy shown in the images as seed content.

**01 Landing (`Page_01_Landing.png`)**: Dark hero (asphalt) with brand, nav links (How it works, Features, Who it’s for, Public map), buttons “Sign in” (outline) and “Create account” (yellow). Headline “Know which roads to fix first.”, supporting sentence, buttons “Create an account” (yellow) and “View the public map” (outline), small note “Rankings are advice for experts to check. Nothing changes on a road automatically.” Right side: framed map preview with ranked hotspot markers and a card “Rank 1 of 47 · demo data / NH-65 × Station Road Junction / Critical 41 accidents · 9 deaths”. Sections: “From spreadsheet to action in seven steps” (Collect, Validate, Analyze, Map, Prioritize, Recommend, Track on a dashed line); “Built for the people who decide where money goes” (six feature rows + a “Suggested actions” sample card with the AI-generated label); “One platform, four kinds of users” (Traffic police, Road safety analysts, Road authorities, The public); dark band “Advice, never automatic action” with three points (Evidence on every result, Personal details hidden, Every change is recorded); closing call to action “See the hotspots near you” with “Create an account” and “Sign in”; footer “Road Accident Hotspot Mapping · Team 12 · Anurag University” and “Demo data only · BRD-RAH-001”.

**02 Sign up (`Page_02_Signup.png`)**: Split screen. Left asphalt panel: brand, headline “Join your team’s road safety workspace.”, three bullets (See every accident and hotspot on one map / Share cases and track what gets fixed / Keep personal details out of your analysis), concentric risk rings over a road with a dashed yellow centre line. Right: “Create your account”, helper “Use your work email. An administrator approves new accounts before you can sign in.” Fields: Full name, Work email, Organisation, Role (Traffic Police Officer, Road Safety Analyst, Road Authority Official), Password (hint “At least 10 characters.”), required checkbox “I will handle accident data under my department’s policy.”, button “Create account”, link “Already have an account? Sign in”. Validate with Zod; after submit show a confirmation that approval is pending.

**03 Login (`Page_03_Login.png`)**: Same split layout. Headline “Find where crashes cluster. Fix those places first.” plus supporting text. Right: “Sign in”, “Use your department account to continue.”, Email, Password with “Forgot password?”, yellow “Sign in”, “or”, “View public hotspot map”, note “The public map shows combined, anonymized figures only.”, “New to the team? Create an account”. Handle pending/deactivated/invalid states with clear messages.

**04 Dashboard (`Page_04_Dashboard.png`)**: Top bar filters “Dec 2025 – Nov 2026”, “All areas”, “Export report”. One KPI strip (Accidents recorded 4,812; Fatalities 389; People injured 5,274; Hotspots identified 47 “12 are critical”; Actions implemented 18 “11 more in progress”), with ▲/▼ change lines (red when worse, green when better). Row 2: “Accidents by month” (area/line + fatalities bars with values, months Dec–Nov) and “Hotspots by risk level” (Critical 12, High 15, Medium 13, Low 7; “47 hotspots in total · 2 new this week”). Row 3: “When accidents happen” (Mon–Sun × 12a…9p heat grid, white→amber→red, with legend) and “Hotspots that need action first” table (rank, location, risk chip, accidents, deaths, status).

**05 Hotspot Map (`Page_05_Hotspot_Map.png`)**: Full-bleed map under the top bar (search box “Search road or junction”). Layers: KDE heatmap, accident points, numbered ranked hotspot markers coloured by risk, selected marker ringed. Left floating **Filters** panel: Date range, Severity chips (Fatal, Grievous, Minor, Non-injury), Time-of-day range slider (e.g. 3 pm – 12 am), Road type chips (National highway, City road, Junction only), Weather chips (All, Rain, Fog), Map layers checkboxes (Heatmap, Accident points, Ranked hotspots, Show only unassigned), Reset. Right floating **hotspot card**: “Hotspot H-0142 · Rank 1 of 47”, name, Critical chip, status tag, “Score 92 / 100”, three stats (41 accidents, 9 deaths, 63 injured), peak time and main factors text, buttons “Open details” and “Assign”, and a list “Other high-priority hotspots”. Bottom-left risk legend, bottom-right zoom control. Filters update the map and counts; map loads ≤ 3 s.

**06 Data Import (`Page_06_Data_Import.png`)**: Four-step stepper (Upload file ✓, Check data ✓, **Review issues**, Import). Left: file card (name, rows, upload date, template version, “Replace file”), segmented quality bar and counts (3,214 ready to import · 187 corrected for you · 81 need your attention), “Issues found” table (Row, What we found, Field, Suggested fix, Action; examples: latitude outside valid range, duplicate of ACC-2026-01882, address-only match 78%, “Grevious” → “Grievous injury”, missing date, invalid time “25:10”, negative fatalities). Right: “Personal details were hidden” (vehicle registration numbers 1,206 · names 312 · phone numbers 74), “File requirements” (.csv, .xlsx; 25 MB; required columns; “Download template”), dark “Ready when you are” card with “Import 3,401 records” and “Fix the 81 rows first”. Also build the first two steps (drag-and-drop upload with progress; automatic checking with progress) and the final success state.

**07 Hotspot Cases (`Page_07_Hotspot_Cases.png`)**: Status tabs with counts (All 47, Identified 9, Under review 11, Assigned 8, Action in progress 11, Implemented 6, Closed 2), search box, filters (Risk level, Assigned to, Area, Updated), table (ID, Location, Risk, Score, Accidents, Assigned to with inline “Assign” when empty, Status with coloured dot, Updated), pagination “Showing 10 of 47”, “Export list”.

**08 Hotspot Detail (`Page_08_Hotspot_Detail.png`)**: Title with risk chip and the six-step lifecycle stepper (current step highlighted). Stats strip: Risk score 92 / 100, Accidents 41, Deaths 9, Injured 63, Peak time “6–9 pm, Fri–Sat”, Analysis settings “250 m radius · 5+ accidents · 12 months”. Left: “Accidents by time of day” bar chart (values 3, 1, 3, 2, 3, 6, 15, 8; top bars red), “What contributed to these accidents” bars, “Why the score is 92” stacked bar (41 from deaths · 32 from number of accidents · 19 from injuries). Right: “Suggested actions” card with the label “AI-generated · expert review needed” and four recommendations (title, “Addresses <factor> · <evidence>”, confidence tag); “Assignment” card (official picker, “Assign hotspot”, “Change risk level”, activity log, comment box). Add the before/after panel after an intervention is recorded.

**09 AI Assistant (`Page_09_AI_Assistant.png`)**: Chat column (user bubbles dark, assistant bubbles white) with rich answers (table of top hotspots; before/after bars with a caution box; source line), suggestion chips (“What caused most crashes at H-0142?”, “Show unassigned critical hotspots”, “Compare Zone 3 with Zone 5”), input with Send, footnote “Answers come from your stored accident data. Check them before acting on a road.” Right panel “Data behind this answer”: mini map and the hotspots cited (ID, name, risk chip, accident count).

**10 Reports (`Page_10_Reports.png`)**: Left: “Create a report” (type, period, area, risk-level chips, format PDF/CSV, “Download report”) and “Recent reports” with Download links. Right: live paper-style preview (title, filters line, three KPIs, hotspots by risk, main contributing factors, top hotspots table).

**11 User Management (`Page_11_User_Management.png`)**: Admin only. Yellow-edged card “3 accounts waiting for approval” with Approve/Reject per row; search and role filter chips; table (User with email, Role tag, Status dot Active/Deactivated/Pending, Last active, Edit); “Add user” button; editing allows role change and deactivate.

**12 Notifications (`Page_12_Notifications.png`)**: Tabs All / Unread (count), “Mark all as read”, grouped Today / Earlier this week; unread items have a coloured dot and bold title; types: critical hotspot detected (red), hotspot assigned (blue), risk level changed (orange), action marked implemented (green). Right card “Tell me when” with four toggles and the note “Notifications appear here in the app. Email and SMS are not available yet.” Bell icon in the top bar shows the unread dot.

**13 Public Map (`Page_13_Public_Map.png`)**: No sidebar; light header (brand, “Public hotspot map · Combined, anonymized figures · Dec 2025 – Nov 2026”, “Create account”, “Sign in”). Map with heat and ranked areas only (**no individual accident points, no names, no assign/override controls**). Left card “Areas to take extra care” (area, risk chip, count band), right “Selected area” card with a plain safety message, bottom notice “Areas are shown within about 500 m. No personal details are shown.” The API must return only banded, grid-snapped data.

---

# PART H: DEVOPS, SECURITY, NFRs AND DEMO DATA

**docker-compose services:** `frontend` (nginx), `backend` (FastAPI + uvicorn), `worker` (RQ/Celery), `postgres` (PostGIS image), `redis`, `minio`, `prometheus`, `grafana`. One command: `docker compose up --build`. Include health checks, volumes, and an init job that runs Alembic migrations and the seed script.

**CI (GitHub Actions `ci.yml`):** on push/PR: lint (ruff, eslint), type-check (mypy/tsc), backend tests with a PostGIS service container, frontend tests, Playwright smoke tests, build Docker images. **CD (`cd.yml`):** on main, build and push images, deploy to AWS (ECS/EC2 + RDS PostgreSQL with PostGIS + ElastiCache + S3) or Azure equivalents; document the chosen path in README.

**Monitoring:** expose metrics via `prometheus-fastapi-instrumentator` (request rate, latency, errors, analysis duration, queue depth); provision Grafana dashboards (API health, analysis jobs, import volumes).

**Security:** HTTPS/TLS in deployment, hashed passwords, JWT expiry + refresh, RBAC on every endpoint, input validation, upload type/size limits, object storage not public, secrets only via env, CORS locked to the frontend origin, audit trail immutable, personal identifiers masked before storage and before any LLM call, public endpoints aggregated only.

**Non-functional targets (BRD §9):** analysis of up to 50,000 records ≤ 120 s; map and dashboard ≤ 3 s; concurrent users and analyses without failure; graceful handling of geocoding, map and LLM failures (clear message, retry, data saved); ≥ 95% availability during evaluation; modular layers (UI / API / analytics / data); every hotspot shows evidence, parameters and a confidence indicator; latest Chrome, Edge, Firefox; core tasks usable without training docs.

**Demo seed (`scripts/seed_demo_data.py`):** idempotent. Create demo users (password in README): Asha Reddy (safety_analyst), Ravi Kumar and Imran Sheikh (police_officer), Sana Fatima and Meera Iyer (authority_official), Dr. Kiran Rao (admin), Pooja Nair (deactivated), and pending: Vikram Singh, Anjali Verma, Harish Babu. Generate ~4,812 synthetic accidents (Dec 2025 – Nov 2026; 389 fatalities, 5,274 injured) around a configurable city centre (`DEMO_CENTER_LAT/LON` in `.env`), with realistic evening peaks, and 47 hotspots split Critical 12 / High 15 / Medium 13 / Low 7 and statuses Identified 9 / Under review 11 / Assigned 8 / Action in progress 11 / Implemented 6 / Closed 2. Hard-code these top hotspots so pages match the images: H-0142 NH-65 × Station Road Junction (Critical, 92, 41 accidents, 9 deaths, 63 injured, Under review, unassigned); H-0087 Outer Ring Road, Exit 12 (Critical, 88, 37, 7 deaths, Assigned to Ravi Kumar); H-0103 Market Road Curve (High, 79, 29, 4, Action in progress, Sana Fatima); H-0215 Bypass Road Underpass (High, 74, 26, 3, Identified); H-0061 School Crossing, Ring Road (Medium, 58, 22, 1, Implemented, Meera Iyer); H-0178 Lake View Roundabout; H-0039 Industrial Area Gate 2; H-0124 Old Town Bridge Approach; H-0196 Canal Road Bend; H-0052 Railway Station Crossing. H-0142 time-of-day counts: 3, 1, 3, 2, 3, 6, 15, 8; factors: two-wheelers 58%, poor lighting 46%, overspeeding 34%, wet road 21%, no pedestrian crossing 18%. Include sample notifications, an example import batch with the 3,214 / 187 / 81 split and issue rows shown on the Import page, and the before/after example for H-0087 (14 → 9 accidents, signal installed 14 May 2026). Also ship a sample CSV with seeded **duplicates, invalid coordinates and fake personal identifiers** for testing FR-03 and FR-12.

---

# PART I: PHASES AND PHASE PROMPTS

Match BRD milestones. After each phase: run tests, start the app, verify with the browser agent against the reference images, post screenshots.

**Phase 0: Plan and scaffold.** “Read docs/SPEC.md, the BRD and all reference images. Produce the Implementation Plan and Task List. Then scaffold the monorepo, docker-compose (postgres+postgis, redis, minio), FastAPI skeleton with `/health`, React + Vite + Tailwind shell with the design tokens from Part D, CI skeleton, `.env.example`, README. Stop for my approval.”

**Phase 1: Database, auth and users (FR-01).** “Implement the data model with Alembic migrations, register/login/refresh/me, the pending-approval flow, RBAC guards for all five roles, and the User Management API. Build pages 02 Sign up, 03 Login and 11 User Management exactly like the references. Add backend tests for every role/permission and frontend tests for form validation.”

**Phase 2: Import pipeline (FR-02, FR-03, FR-12).** “Implement upload to MinIO, masking (before storage/LLM), validation, standardisation, duplicate detection, geocoding with cache and confidence, data quality report, issue review actions, commit, template download and audit logging. Build page 06 Data Import (all four steps). Add tests using the sample CSV with seeded duplicates, invalid coordinates and fake personal identifiers.”

**Phase 3: Analytics engine (FR-04, FR-05, FR-07).** “Implement the `analytics/` package: DBSCAN hotspot detection, KDE heat surface, risk scoring with breakdown, configurable thresholds and weights, factor analysis, rule-based recommendations with evidence and confidence, insufficient-data handling, reproducible parameters, background jobs with status polling. Add unit tests with seeded clusters and the performance test for 50,000 records ≤ 120 s.”

**Phase 4: Map, hotspots and tracking (FR-06, FR-08, FR-13).** “Implement the map APIs (GeoJSON, heat, public aggregated), hotspot/case APIs, assignment, status lifecycle with valid transitions, comments, interventions, before/after comparison and the append-only audit trail. Build pages 05 Hotspot Map, 07 Hotspot Cases, 08 Hotspot Detail and 13 Public Map. Verify filters, ≤ 3 s load and that the public API leaks no individual records.”

**Phase 5: Dashboard, notifications, reports, assistant (FR-09, FR-10, FR-11).** “Implement the dashboard endpoints with caching, notification events and settings, report generation (PDF/CSV), and the grounded AI assistant with an `LLMClient` abstraction, tool-style retrieval, citations, caveats and refusal of out-of-scope questions. Build pages 04 Dashboard, 09 AI Assistant, 10 Reports, 12 Notifications and 01 Landing. Verify that dashboard figures equal database queries.”

**Phase 6: Seed, polish and testing.** “Write the seed script that reproduces the demo data in Part H so every page matches the reference screenshots. Add Playwright end-to-end tests for the main journeys (sign up → admin approval → login → import → analyse → map → assign → status change → report), responsive and accessibility checks, and the Postman/Newman collection. Fix every visual difference versus `docs/Page_*.png`.”

**Phase 7: DevOps and deployment.** “Finish Dockerfiles, compose (with Prometheus and Grafana dashboards), GitHub Actions CI/CD, deployment instructions for AWS or Azure, security hardening checklist, and documentation: README, architecture diagram, API docs link, user guide, test report template, `docs/ASSUMPTIONS.md`. Produce a final acceptance report mapping every FR and BO in the BRD traceability matrix to its passing test.”

---

# ACCEPTANCE CHECKLIST (the agent must tick every line in its final report)

- [ ] FR-01 login/register/RBAC/admin user management, pending-approval flow
- [ ] FR-02 manual + bulk import, unique IDs, validation, file-type and size limits, import summary
- [ ] FR-03 duplicates, invalid values and coordinates detected; address geocoding with confidence; data quality report; resubmit rejected rows
- [ ] FR-04 hotspots detected from seeded clusters; configurable parameters stored; “no reliable hotspot” rule
- [ ] FR-05 risk score, levels, configurable weights/thresholds, override with reason in audit trail
- [ ] FR-06 interactive map with heatmap, clusters/markers, all filters, popups, ≤ 3 s
- [ ] FR-07 factor analysis and recommendations with evidence, confidence and AI/expert-review label
- [ ] FR-08 assign, status lifecycle, comments, search/filter, before/after comparison
- [ ] FR-09 assistant grounded in data, cites sources, refuses out-of-scope, shows caveats
- [ ] FR-10 in-app notifications for the four events, only to relevant users, read/unread, settings
- [ ] FR-11 dashboard figures match data, filters, exportable PDF/CSV reports, ≤ 3 s
- [ ] FR-12 personal identifiers masked before storage and LLM calls; public view aggregated only
- [ ] FR-13 append-only audit trail of imports, analysis runs, assignments, status changes, overrides, comments
- [ ] BR-01 to BR-08 enforced in code and covered by tests
- [ ] All 13 pages built and visually matched to `docs/Page_*.png`
- [ ] `docker compose up` works from a clean clone; CI green; README complete
