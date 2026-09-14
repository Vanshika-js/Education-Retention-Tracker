# Architecture & System Design — Student Retention & Welfare Efficacy Tracker

This document outlines the architectural decisions, design patterns, and system components underlying the Student Retention & Welfare Efficacy Tracker built for Track 4 (Education & EdTech).

---

## 🏛 System Architecture Overview

The system is structured as a decoupled, multi-tier data architecture:

```
+-----------------------------------------------------------------------------------+
|                                 RAW DATA SOURCES                                  |
|  - track4_school_master.csv        (School metadata)                             |
|  - track4_student_attendance.csv   (Daily attendance logs)                       |
|  - track4_mid_day_meal_procurement.xlsx (Food grain supply logs)                  |
|  - track4_school_infrastructure.csv (Amenity inspection audits)                   |
|  - track4_test_scores.json         (FLN assessment scores in 6 scale formats)    |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                           ETL & DATA GOVERNANCE PIPELINE                          |
|  - Canonical ID Normalization     (src/cleaning_ids.py)                           |
|  - ISO Date Parsing & Ambiguity   (src/cleaning_dates.py)                         |
|  - Multilingual Boolean Cleaning  (src/cleaning_boolean.py)                       |
|  - MDM Unit Standardization to KG (src/cleaning_mdm.py)                           |
|  - FLN Score Scale Standardization(src/cleaning_scores.py)                        |
|  - Infrastructure Snapshot Engine (src/cleaning_infrastructure.py)                |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        GOVERNED DUCKDB ANALYTICAL WAREHOUSE                       |
|  Star Schema Tables:                                                              |
|    - dim_school (Central Dimension)                                               |
|    - fact_attendance, fact_mdm_procurement, fact_test_scores                      |
|    - dim_infrastructure_current, dim_infrastructure_history                      |
|    - fact_welfare_risk (Computed Welfare & Retention Risk Index)                  |
|  Analytical Views:                                                                |
|    - vw_district_summary, vw_school_attendance_daily, etc.                        |
+-----------------------------------------------------------------------------------+
                                          |
                        +-----------------+-----------------+
                        |                                   |
                        v                                   v
+-----------------------------------------------+   +-------------------------------+
|         STREAMLIT WEBSITE PORTAL              |   |     REAL GEMINI AI AGENT      |
|  - Top Website Navigation Bar                 |   |  - Gemini 3.6 Flash LLM Engine|
|  - Global Administrative Filters Panel        |   |  - Text-to-SQL Generator      |
|  - 6 Analytical Modules & Action Tables       |   |  - Self-Correcting Execution  |
|  - High-Contrast Plotly Auto-Scaling          |   |  - Executive Narrative Generator|
+-----------------------------------------------+   +-------------------------------+
```

---

## 📑 Architectural Decision Records (ADRs)

### ADR 1: Embedded DuckDB as the Governed Analytical Warehouse
- **Context**: The application needs to query heterogeneous datasets (CSV, Excel XLSX, JSON) efficiently, evaluate aggregation queries across 20,000+ records in real time, and serve dynamic Streamlit visualizations without lag.
- **Decision**: Use DuckDB (`data/processed/education_warehouse.duckdb`) as an embedded analytical database engine.
- **Rationale**:
  - **Vectorized Execution**: DuckDB executes OLAP queries in memory with high performance.
  - **Zero Infrastructure Overhead**: Unlike PostgreSQL or MySQL, DuckDB requires no server daemon setup, credential configuration, or external database management.
  - **Native SQL Views & Python Integration**: Easily interfaces with Pandas DataFrames and allows standard SQL view definitions (`sql/views.sql`) for clean analytics.

---

### ADR 2: Star-Schema Dimensional Design over Full Denormalized Joins
- **Context**: The source datasets exist at fundamentally different natural grains:
  - `School Master`: 1 row per school (`school_id`).
  - `Attendance`: 1 row per school + date + grade.
  - `MDM Procurement`: 1 row per procurement transaction ID.
  - `Infrastructure Audit`: 1 row per inspection date.
  - `FLN Assessment`: 1 row per assessment ID.
- **Decision**: Maintain a strict Star-Schema layout centered around `dim_school`, rather than building a single flat joined table.
- **Rationale**:
  - Joining raw tables directly produces a massive Cartesian product (many-to-many row expansion). For example, joining 20,000 attendance records with 12,000 MDM logs for the same school creates millions of duplicate rows, corrupting aggregate sums (e.g., multiplying food grain quantities or total enrollment counts).
  - Star-Schema keeps fact tables isolated at their native grains while allowing clean aggregations through analytical views (`vw_district_summary`, `vw_school_attendance_monthly`, etc.).

---

### ADR 3: Multi-Factor Welfare & Retention Risk Index vs. Black-Box ML Claims
- **Context**: The datasets lack longitudinal student-level tracking IDs and ground-truth dropout labels.
- **Decision**: Construct a transparent, weighted **Welfare & Retention Risk Index** (0 to 100) instead of claiming ground-truth machine learning dropout predictions.
- **Rationale**:
  - Claiming true dropout prediction on synthetic/aggregate school-level data without individual student drop histories is methodologically flawed.
  - A multi-factor index combining Attendance Risk (30%), Learning Risk (25%), Infrastructure Risk (20%), MDM Procurement Risk (15%), and Data Integrity Anomaly Risk (10%) provides actionable operational insights for education administrators while remaining transparent and explainable.

---

### ADR 4: Text-to-SQL AI Agent with Self-Correction & High-Contrast Visual Scaling
- **Context**: The AI Agent must allow non-technical stakeholders to ask plain-English questions, return valid DuckDB SQL queries, display executive summaries, and render clear graphs.
- **Decision**:
  - Integrate `gemini-3.6-flash` via `google.generativeai` with a built-in Text-to-SQL schema prompt and fallback SQL planner.
  - Implement a **Self-Correcting Query Loop**: If DuckDB raises a syntax or column error during execution, the error traceback is automatically returned to Gemini to self-correct the SQL query.
  - Implement **High-Contrast Plotly Auto-Scaling**: Compute dynamic Y-axis bounds (`[min_value - padding, max_value + padding]`) for bar/scatter charts to highlight visual gaps between values, while using clean hover tooltips on line trend charts to avoid text overlap clutter.

---

## 🔒 Data Quality & Pipeline Safety

1. **Deterministic Execution**: Running `python -m src.ingestion` executes all cleaning routines sequentially and outputs clean CSVs alongside audit reports (`reports/data_quality_report.html`).
2. **Read-Only Database Connections**: The Streamlit dashboard opens DuckDB in read-only mode (`read_only=True`) to prevent concurrent write lock contention and protect data integrity.
3. **Formal Column Casing**: All output DataFrames and charts pass through `format_formal_label()` in `src/agent.py` to ensure proper title casing (`district` → `District Name`).
