# Student Retention & Welfare Efficacy Tracker
### TransOrg AgentIQ Datathon — Track 4 (Education & EdTech)

A data engineering pipeline, governed DuckDB analytical star-schema warehouse, multi-dimensional Welfare Risk Engine, and Gemini-powered AI Agent designed for the State Education Department to monitor student attendance integrity, Mid-Day Meal (MDM) procurement efficiency, infrastructure deficits, and Foundational Literacy & Numeracy (FLN) outcomes.

---

## 📌 Executive Summary

State education departments handle vast amounts of daily operational data scattered across multiple disconnected systems—daily attendance logs, meal supply invoices, inspection notes, and standardized test results. In practice, these raw datasets are often messy, incomplete, and plagued by data quality issues (such as inconsistent school IDs, mixed date formats, non-standard unit measurements, and unvalidated proxy attendance entries).

This project cleanses, normalizes, and links these heterogeneous datasets into a single governed analytical environment. By combining an automated Python ETL pipeline, an embedded DuckDB star-schema warehouse, a custom Streamlit website portal, and an AI Agent powered by Gemini 3.6 Flash, education officers can instantly audit data integrity, identify high-risk schools requiring intervention, and query state analytics in plain English.

---

## 📊 Data Rescue & Governance Audit Summary

During the initial ingestion and audit phase (Gate 1 & Gate 2), we processed **5 raw datasets** totaling over 44,000 raw records. Below is the full summary of data cleaning and normalization steps performed:

| Dataset Name | Raw Format | Raw Rows | Cleaned Rows | Natural Primary Key / Grain | Key Quality Issues Resolved |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **School Master** | CSV | **618** | **600** | `school_id` | Stripped duplicates, standardized district capitalization (e.g., `moga` → `Moga`), and corrected malformed ID strings. |
| **Student Attendance** | CSV | **20,800** | **20,000** | `school_id` + `attendance_date` + `grade` | Resolved 5 different ID formats, removed 800 duplicate logs, flagged 806 impossible records (`present > enrolled`), and identified 944 Sunday/holiday proxy entries. |
| **MDM Procurement** | XLSX | **12,360** | **12,000** | `procurement_id` | Standardized 1,849 non-standard quantity units (Bags, Sacks, Grams → Kilograms), cleaned currency strings (`₹`, `Rs.`, `/-`), and mapped supplier names. |
| **School Infrastructure** | CSV | **3,150** | **3,000** | `school_id` + `inspection_date` | Converted 23 non-standard boolean representations (e.g., `Hai`, `Kharab`, `1`, `Yes`) into canonical `TRUE`/`FALSE`/`UNKNOWN` statuses. Built snapshot logic for current state vs. historical audits. |
| **FLN Test Scores** | JSON | **8,000** | **8,000** | `assessment_id` | Converted 6 distinct grading scales (Raw marks like `32/50`, Letter grades `A+`, CGPA `8.2`, `%`) into a unified `score_percentage` metric ($0.0 - 100.0\%$). |

---

## ⚡ Quick Start & Setup Guide

The pipeline is completely deterministic and reproducible. Follow these steps to set up the environment, run the ETL pipeline, execute unit tests, and launch the web app.

### 1. Prerequisites & Installation
Ensure you have Python 3.9 or higher installed. Clone the repository and install the required dependencies:

```bash
git clone https://github.com/Vanshika-js/Education-Retention-Tracker.git
cd Education-Retention-Tracker

# Install required Python packages 
python -m pip install -r requirements.txt 
```

### 2. Run Data Ingestion & Governance Pipeline
Execute the main ingestion runner to clean raw files, normalize keys and formats, and generate audit logs:

```bash
python -m src.ingestion
```

*Generated Artifacts*:
- `data/processed/clean_school_master.csv`
- `data/processed/clean_student_attendance.csv`
- `data/processed/clean_mdm_procurement.csv`
- `data/processed/clean_infrastructure_current.csv`
- `data/processed/clean_infrastructure_history.csv`
- `data/processed/clean_test_scores.csv`
- `reports/data_quality_report.html` (Interactive HTML audit report)
- `reports/data_quality_report.json`

### 3. Build DuckDB Governed Warehouse & Risk Engine
Build the DuckDB star-schema database, analytical views, and calculate the multi-factor welfare risk index:

```bash
python -m src.analytics
python -m src.risk_engine
```

*Generated Database*: `data/processed/education_warehouse.duckdb`

### 4. Run Test Suite
Verify database integrity, ETL functions, and risk calculations by running the unit test suite:

```bash
python -m unittest discover tests
```

### 5. Launch Interactive Website Portal & AI Agent
Start the Streamlit portal:

```bash
streamlit run dashboard/app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 📐 Core Business Metrics & Mathematical Definitions

1. **Average Daily Attendance Rate (%)**:
   $$\text{ADA Rate} = \frac{\sum \text{Validated Present Students}}{\sum \text{Validated Enrolled Students}} \times 100$$
   *(Excludes data quality violations where `present_students > total_students` and Sunday proxy records)*

2. **Proxy Attendance Anomaly Rate (%)**:
   $$\text{Proxy Anomaly Rate} = \frac{\text{Count of } 100\% \text{ Attendance Records Marked on Sundays/Holidays}}{\text{Total Attendance Records Marked}} \times 100$$

3. **Infrastructure Deficit Index (%)**:
   $$\text{Infra Deficit Index} = 100 - \left( \frac{\text{Count of Available Functional Amenities}}{5} \times 100 \right)$$
   *(Evaluates 5 core amenities: Electricity, Safe Drinking Water, Functional Toilets, Boundary Wall, and Playground)*

4. **Welfare & Retention Risk Index (0–100 Scale)**:
   A composite decision-support score designed to highlight vulnerable schools before dropouts occur:
   $$\text{Risk Index} = 0.30(\text{AttRisk}) + 0.25(\text{LearnRisk}) + 0.20(\text{InfraRisk}) + 0.15(\text{MDMRisk}) + 0.10(\text{IntegrityRisk})$$

   - **High Risk**: Score $\ge 70$ (Immediate administrative intervention required)
   - **Moderate Risk**: Score $40 - 69$ (Targeted support needed)
   - **Low Risk**: Score $< 40$ (Stable operational status)

---

## 🖥 Website Navigation & Portal Modules

The portal features a modern website-style top navigation bar and global administrative filters:

1. **📊 Executive Command Center**: Top-level KPIs (Total Enrolled, Statewide Attendance Rate, Proxy Anomaly Rate, Deficit Index, FLN Score), district rank comparisons, and risk profile distribution.
2. **📅 Attendance Intelligence**: Statewide monthly attendance trends, proxy anomaly tracking, and an audit table of top Sunday proxy marking school records.
3. **🍲 MDM Procurement Intelligence**: Total food grain volume (KG), expenditure breakdown by supplier entity, food grain commodity mix, and cost-per-KG efficiency metrics.
4. **🏫 Infrastructure & Amenities**: Five-point amenity availability breakdown (Power, Water, Sanitation, Security, Sports) and district infrastructure deficit rankings.
5. **🎓 FLN Learning Outcomes**: Performance evaluation across 8,000 standardized assessments broken down by academic subject and grade level.
6. **⚠️ Welfare & Retention Risk Tracker**: Interactive action priority table ranking schools by risk index to guide resource allocation.
7. **🤖 Real Gemini AI Agent**: Natural language query engine using Gemini 3.6 Flash. Converts plain English questions into live DuckDB SQL queries, generates executive narrative memos, and renders high-contrast Plotly graphics.

---

## 🤖 Real AI Agent Engine (Gemini 3.6 Flash)

The embedded AI Agent allows departmental officers to ask plain-English questions without writing SQL queries.

### Key Capabilities:
- **Text-to-SQL Query Generation**: Uses Generative AI to translate user intent into valid DuckDB SQL queries against governed analytical views (`vw_district_summary`, `vw_school_attendance_daily`, `vw_school_mdm_summary`, `vw_school_test_summary`, `fact_welfare_risk`).
- **Self-Correcting Query Loop**: Catches DuckDB execution errors in real time and passes error tracebacks back to Gemini to self-correct the query without crashing.
- **Formal Title-Case Formatting**: Formats database column names into formal administrative titles (`district` → `District Name`, `avg_fln_score` → `Average FLN Test Score (%)`).
- **High-Contrast Chart Auto-Scaling**: Calculates dynamic Y-axis bounds (`[min_value - padding, max_value + padding]`) for bar and scatter charts so small numerical variations are easy to compare visually.
- **Line Chart Hover Tooltips**: Line graphs display clean hover tooltips instead of crowded static point labels.

---

## 📁 Repository Structure

```
.
├── dashboard/
│   └── app.py                         # Streamlit website dashboard & top navbar UI
├── data/
│   ├── raw/                           # Original messy datathon files
│   └── processed/                     # Cleaned CSVs & DuckDB analytical database
├── reports/
│   ├── data_quality_report.html       # Interactive HTML audit report
│   └── data_quality_report.json       # JSON audit report
├── sql/
│   ├── schema.sql                     # DuckDB table DDL statements
│   └── views.sql                      # Analytical views DDL statements
├── src/
│   ├── __init__.py
│   ├── agent.py                       # Real Gemini AI Agent implementation
│   ├── analytics.py                   # DuckDB database initialization & view creation
│   ├── cleaning_attendance.py         # Attendance log cleaning & anomaly detection
│   ├── cleaning_boolean.py            # Multilingual boolean status mapping
│   ├── cleaning_dates.py              # ISO date parsing & ambiguity flagging
│   ├── cleaning_ids.py                # School ID canonicalization logic
│   ├── cleaning_infrastructure.py     # Infrastructure boolean cleaning & snapshot logic
│   ├── cleaning_master.py             # School master dimension cleaning
│   ├── cleaning_mdm.py                # MDM unit standardization to KG & cost extraction
│   ├── cleaning_scores.py             # FLN score scale standardization to percentage
│   ├── ingestion.py                   # Master ETL pipeline runner
│   └── risk_engine.py                 # Welfare & Retention Risk Index calculator
├── tests/
│   ├── test_boolean.py                # Boolean data cleaning tests
│   ├── test_dates.py                  # Date parsing and validation tests
│   ├── test_ids.py                    # School ID normalization tests
│   ├── test_mdm.py                    # MDM procurement cleaning tests
│   └── test_scores.py                 # FLN score normalization tests
├── ARCHITECTURE.md                    # System architecture & Decision Records (ADRs)
├── DATA_DICTIONARY.md                 # Full data lineage & field dictionary
├── USER_GUIDE.md                      # Comprehensive guide for department staff
├── README.md                          # Main project README
├── requirements.txt                   # Dependency requirements
└── track4_dataset_notes.txt           # Data notes & domain context
```

---

## ⚠️ Analytical Boundaries & Assumptions

1. **Retention Risk as a Decision Proxy**: The source datasets do not contain individual student tracking IDs over multiple years or explicit ground-truth dropout labels. The Welfare & Retention Risk Index is a decision-support proxy designed to help administrators allocate resources to vulnerable schools, not a deterministic individual dropout prediction.
2. **MDM Procurement vs. Consumption**: MDM metrics track procurement logs and financial disbursements to suppliers, which serve as an operational proxy for meal availability.
