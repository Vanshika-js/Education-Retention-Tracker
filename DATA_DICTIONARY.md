# Data Dictionary — Student Retention & Welfare Efficacy Tracker

This document provides a detailed data dictionary covering raw attributes, cleaned fields, data types, business descriptions, and transformation rules across all 5 source datasets and the DuckDB Governed Analytical Layer.

---

## 🏛 1. School Master Dimension (`dim_school`)

**Primary Key**: `school_id`  
**Description**: Canonical master catalog of all reporting schools within the state education department.

| Field Name | Raw Type | Cleaned Type | Range / Allowed Values | Transformation Logic | Business Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `school_id` | `VARCHAR` | `VARCHAR` | `SCH0001` - `SCH9999` | `normalize_school_id()`: Trims whitespace, upper-cases string, extracts numeric digits, and formats to 4-digit zero-padded string (`SCH0001`). | Unique canonical identifier for each school. |
| `school_name` | `VARCHAR` | `VARCHAR` | Non-empty text string | Trimmed, title-cased string. Missing names filled from historical lookup. | Official name of the educational institution. |
| `district` | `VARCHAR` | `VARCHAR` | `Amritsar`, `Bathinda`, `Ferozepur`, `Jalandhar`, `Ludhiana`, `Moga`, `Patiala`, `Sangrur` | Title-cased. Inconsistent casing (e.g., `moga`, `AMRITSAR`) normalized. Unmapped entries assigned `Unknown District`. | Administrative district name. |
| `block` | `VARCHAR` | `VARCHAR` | Non-empty text string | Title-cased string. Missing blocks assigned `Unknown Block`. | Sub-district administrative block. |
| `total_enrolled_students` | `INT` | `INT` | $> 0$ | Preserved integer. Duplicate rows removed based on `school_id`. | Total officially enrolled student capacity. |
| `school_type` | `VARCHAR` | `VARCHAR` | `Primary`, `Upper Primary`, `Secondary`, `Higher Secondary` | Standardized text casing and mapped variants. | Educational level classification. |
| `medium` | `VARCHAR` | `VARCHAR` | `Punjabi`, `Hindi`, `English` | Standardized text casing. | Primary language medium of instruction. |

---

## 📅 2. Fact Attendance (`fact_attendance`)

**Primary Key**: `record_id` (Grain: `school_id` + `attendance_date` + `grade`)  
**Description**: Daily student attendance logs capturing present counts, enrolled counts, teacher presence, and data quality anomaly flags.

| Field Name | Raw Type | Cleaned Type | Range / Allowed Values | Transformation Logic | Business Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `record_id` | `VARCHAR` | `VARCHAR` | `ATT0000001`+ | Preserved raw ID or auto-generated primary key. | Attendance log transaction identifier. |
| `school_id` | `VARCHAR` | `VARCHAR` | `SCH0001`+ | `normalize_school_id()` | Linking foreign key to `dim_school`. |
| `attendance_date` | `VARCHAR` | `DATE` | `YYYY-MM-DD` | `normalize_date()`: Parses ISO strings (`YYYY-MM-DD`), slash dates (`DD/MM/YYYY`), and flags ambiguous dates. | Date of attendance recording. |
| `grade` | `VARCHAR` | `VARCHAR` | `Grade 1` - `Grade 12` | Mapped Roman numerals (e.g., `Class IX` → `Grade 9`) and numeric strings to standard format (`Grade X`). | Student grade or class level. |
| `total_students` | `INT` | `INT` | $\ge 0$ | Preserved integer count of enrolled class students. | Enrolled student count for the specific grade. |
| `present_students` | `INT` | `INT` | $\ge 0$ | Preserved integer count of students physically present. | Count of students marked present. |
| `attendance_rate` | `N/A` | `FLOAT` | $0.0 - 100.0\%$ | Derived: `(present_students / total_students) * 100`. Set to `NULL` if `total_students == 0`. | Calculated daily attendance percentage. |
| `teacher_present` | `VARCHAR` | `BOOLEAN` | `TRUE`, `FALSE`, `NULL` | `normalize_boolean()`: Maps multilingual variants (`Hai`, `Kharab`, `Yes`, `1`) to boolean values. | Teacher attendance indicator. |
| `marked_by` | `VARCHAR` | `VARCHAR` | Text string | Trimmed string indicating authority (e.g., `Class Teacher`, `Principal`). | Authority who logged attendance. |
| `is_impossible_attendance` | `N/A` | `BOOLEAN` | `TRUE`, `FALSE` | Flagged `TRUE` if `present_students > total_students`. | Data quality anomaly flag for invalid counts. |
| `is_proxy_attendance` | `N/A` | `BOOLEAN` | `TRUE`, `FALSE` | Flagged `TRUE` if `present_students == total_students` (100% attendance) on a Sunday or official holiday. | Integrity anomaly flag for Sunday proxy marking. |
| `is_weekend` | `N/A` | `BOOLEAN` | `TRUE`, `FALSE` | Flagged `TRUE` if day of week is Sunday. | Weekend calendar indicator. |
| `data_quality_status` | `N/A` | `VARCHAR` | `VALID`, `IMPOSSIBLE_COUNT`, `SUNDAY_PROXY` | Categorized based on anomaly flags. | Data validation audit status. |

---

## 🍲 3. Fact MDM Procurement (`fact_mdm_procurement`)

**Primary Key**: `procurement_id`  
**Description**: Food grain procurement transactions for the Mid-Day Meal program, converted into standard units (KG) and clean INR currency values.

| Field Name | Raw Type | Cleaned Type | Range / Allowed Values | Transformation Logic | Business Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `procurement_id` | `VARCHAR` | `VARCHAR` | `MDM0000001`+ | Preserved raw ID. | Procurement log transaction identifier. |
| `school_id` | `VARCHAR` | `VARCHAR` | `SCH0001`+ | `normalize_school_id()` | Linking foreign key to `dim_school`. |
| `procurement_date` | `VARCHAR` | `DATE` | `YYYY-MM-DD` | `normalize_date()` | Date of food grain procurement. |
| `vendor_name` | `VARCHAR` | `VARCHAR` | Standardized entities | Standardized supplier entity names (e.g., `Kumar Enterprises`, `Singh Agro Group`, `Sharma Traders`, `Goyal Mills`). | Name of approved supplier vendor. |
| `grain_type` | `VARCHAR` | `VARCHAR` | `Rice`, `Wheat`, `Pulses`, `Oil` | Standardized commodity variants (e.g., `Chawal` → `Rice`, `Kanak` → `Wheat`). | Food grain commodity type. |
| `quantity_kg` | `VARCHAR` | `FLOAT` | $> 0.0$ | Standardized non-standard units to KG: `1 Bag = 50 KG`, `1 Sack = 50 KG`, `Grams = 0.001 KG`, `Quintal = 100 KG`. | Net procurement weight in Kilograms. |
| `total_cost` | `VARCHAR` | `FLOAT` | $\ge 0.0$ | Stripped currency symbols (`₹`, `Rs.`, `/-`, `,`) and cast to numeric float. | Total procurement cost in INR (₹). |
| `cost_per_kg` | `N/A` | `FLOAT` | $> 0.0$ | Derived: `total_cost / quantity_kg`. | Calculated unit cost efficiency (₹/KG). |
| `payment_status` | `VARCHAR` | `VARCHAR` | `Paid`, `Pending`, `Unknown` | Case-normalized payment status. | Supplier payment disbursement status. |

---

## 🏫 4. Dim Infrastructure Current (`dim_infrastructure_current`)

**Primary Key**: `school_id`  
**Description**: Current operational status of 5 core basic amenities per school, extracted from inspection audit logs.

| Field Name | Raw Type | Cleaned Type | Range / Allowed Values | Transformation Logic | Business Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `school_id` | `VARCHAR` | `VARCHAR` | `SCH0001`+ | `normalize_school_id()` | Unique school linking key. |
| `last_inspection_date` | `VARCHAR` | `DATE` | `YYYY-MM-DD` | `normalize_date()` of most recent inspection. | Date of latest inspection audit. |
| `has_electricity` | `VARCHAR` | `BOOLEAN` | `TRUE`, `FALSE`, `NULL` | `normalize_boolean()`: Maps `Hai`/`Haan`/`1`/`Yes` → `TRUE`; `Kharab`/`Nahi`/`0`/`No` → `FALSE`. | Functional electricity availability. |
| `has_drinking_water` | `VARCHAR` | `BOOLEAN` | `TRUE`, `FALSE`, `NULL` | `normalize_boolean()` | Safe drinking water access status. |
| `has_functional_toilet` | `VARCHAR` | `BOOLEAN` | `TRUE`, `FALSE`, `NULL` | `normalize_boolean()` | Functional toilet sanitation status. |
| `has_boundary_wall` | `VARCHAR` | `BOOLEAN` | `TRUE`, `FALSE`, `NULL` | `normalize_boolean()` | Perimeter boundary wall security status. |
| `has_playground` | `VARCHAR` | `BOOLEAN` | `TRUE`, `FALSE`, `NULL` | `normalize_boolean()` | Playground facility status. |
| `infrastructure_score` | `N/A` | `FLOAT` | $0.0 - 100.0\%$ | Derived: `(Count of available functional amenities / 5) * 100`. | Overall infrastructure health score (%). |
| `infrastructure_deficit_pct` | `N/A` | `FLOAT` | $0.0 - 100.0\%$ | Derived: `100.0 - infrastructure_score`. | Calculated amenity deficit index (%). |

---

## 🎓 5. Fact Test Scores (`fact_test_scores`)

**Primary Key**: `assessment_id`  
**Description**: Standardized learning assessment scores from FLN evaluations, converted from 6 scale formats into a unified percentage metric.

| Field Name | Raw Type | Cleaned Type | Range / Allowed Values | Transformation Logic | Business Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `assessment_id` | `VARCHAR` | `VARCHAR` | `TST0000001`+ | Preserved raw assessment ID. | Assessment transaction identifier. |
| `school_id` | `VARCHAR` | `VARCHAR` | `SCH0001`+ | `normalize_school_id()` | Foreign key linking to `dim_school`. |
| `assessment_date` | `VARCHAR` | `DATE` | `YYYY-MM-DD` | `normalize_date()` | Date of test administration. |
| `grade` | `VARCHAR` | `VARCHAR` | `Grade 1` - `Grade 12` | Grade normalization. | Student class level evaluated. |
| `subject` | `VARCHAR` | `VARCHAR` | `Mathematics`, `English`, `Hindi`, `Punjabi`, `EVS`, `Science` | Standardized subject names across Punjabi/Hindi variants. | Academic subject evaluated. |
| `grading_scale_raw` | `VARCHAR` | `VARCHAR` | Text string | Preserved original grading scale description. | Original format representation. |
| `score_percentage` | `VARCHAR` | `FLOAT` | $0.0 - 100.0\%$ | `clean_scores.py`: Parses raw marks (`32/50` → `64%`), letter grades (`A+` → `95%`, `A` → `85%`, `B` → `75%`, `C` → `60%`, `D` → `45%`, `F` → `25%`), CGPA (`8.0` → `76%`), and raw percentage strings. | Unified standardized score percentage. |

---

## ⚠️ 6. Fact Welfare Risk (`fact_welfare_risk`)

**Primary Key**: `school_id`  
**Description**: Multi-dimensional Welfare & Retention Risk Index computed per school to prioritize departmental interventions.

| Field Name | Cleaned Type | Range / Allowed Values | Weight | Business Formula & Description |
| :--- | :--- | :--- | :---: | :--- |
| `school_id` | `VARCHAR` | `SCH0001`+ | Key | Linking identifier for school. |
| `welfare_risk_score` | `FLOAT` | $0.0 - 100.0$ | Composite | Weighted index: $0.30(\text{AttRisk}) + 0.25(\text{LearnRisk}) + 0.20(\text{InfraRisk}) + 0.15(\text{MDMRisk}) + 0.10(\text{IntegrityRisk})$. |
| `welfare_risk_category` | `VARCHAR` | `High Risk`, `Moderate Risk`, `Low Risk` | Label | Classified: `High Risk` ($\ge 70$), `Moderate Risk` ($40 - 69$), `Low Risk` ($< 40$). |
| `avg_attendance_rate` | `FLOAT` | $0.0 - 100.0\%$ | 30% | Validated average attendance rate. Lower rate increases `AttRisk`. |
| `avg_fln_score` | `FLOAT` | $0.0 - 100.0\%$ | 25% | Average standardized FLN score. Lower score increases `LearnRisk`. |
| `infrastructure_deficit_pct` | `FLOAT` | $0.0 - 100.0\%$ | 20% | Missing amenities percentage. Higher deficit increases `InfraRisk`. |
| `proxy_anomaly_rate` | `FLOAT` | $0.0 - 100.0\%$ | 10% | Sunday proxy marking frequency. Higher rate increases `IntegrityRisk`. |
