-- Analytical SQL Views for Business KPIs & Dashboard Querying

-- 1. Daily School Attendance View
CREATE OR REPLACE VIEW vw_school_attendance_daily AS
SELECT 
    a.record_id,
    a.school_id,
    s.school_name,
    s.district,
    s.block,
    s.school_type,
    a.date AS attendance_date,
    a.grade,
    a.total_students,
    a.present_students,
    a.attendance_rate,
    a.teacher_present,
    a.marked_by,
    a.is_impossible_attendance,
    a.is_proxy_attendance,
    a.is_weekend,
    a.data_quality_status
FROM fact_attendance a
LEFT JOIN dim_school s ON a.school_id = s.school_id;

-- 2. Monthly Attendance Trends & Anomaly Rates View
CREATE OR REPLACE VIEW vw_school_attendance_monthly AS
SELECT 
    s.district,
    strftime(TRY_CAST(a.date AS DATE), '%Y-%m') AS month,
    COUNT(a.record_id) AS total_records,
    AVG(CASE WHEN a.data_quality_status = 'VALID' THEN a.attendance_rate END) AS avg_attendance_rate,
    SUM(CASE WHEN a.is_proxy_attendance THEN 1 ELSE 0 END) AS proxy_anomaly_records,
    SUM(CASE WHEN a.is_impossible_attendance THEN 1 ELSE 0 END) AS impossible_records,
    (SUM(CASE WHEN a.is_proxy_attendance THEN 1 ELSE 0 END) * 100.0 / COUNT(a.record_id)) AS proxy_anomaly_rate_pct
FROM fact_attendance a
LEFT JOIN dim_school s ON a.school_id = s.school_id
GROUP BY s.district, strftime(TRY_CAST(a.date AS DATE), '%Y-%m');

-- 3. MDM Procurement Summary View
CREATE OR REPLACE VIEW vw_school_mdm_summary AS
SELECT 
    m.procurement_id,
    m.school_id,
    s.school_name,
    s.district,
    s.block,
    m.date AS procurement_date,
    m.vendor_name,
    m.grain_type,
    m.quantity_kg,
    m.total_cost,
    m.cost_per_kg,
    m.payment_status,
    m.unit_inferred_flag
FROM fact_mdm_procurement m
LEFT JOIN dim_school s ON m.school_id = s.school_id;

-- 4. Infrastructure Current View
CREATE OR REPLACE VIEW vw_school_infrastructure_summary AS
SELECT 
    i.school_id,
    s.school_name,
    s.district,
    s.block,
    i.date AS last_inspection_date,
    i.has_electricity,
    i.has_drinking_water,
    i.has_functional_toilet,
    i.has_boundary_wall,
    i.has_playground,
    i.infrastructure_score,
    i.infrastructure_deficit_pct,
    i.inspector_name,
    i.remarks
FROM dim_infrastructure_current i
LEFT JOIN dim_school s ON i.school_id = s.school_id;

-- 5. FLN Test Scores Summary View
CREATE OR REPLACE VIEW vw_school_test_summary AS
SELECT 
    t.assessment_id,
    t.school_id,
    s.school_name,
    s.district,
    s.block,
    t.date AS assessment_date,
    t.grade,
    t.subject,
    t.grading_scale_raw,
    t.avg_score_raw,
    t.score_percentage
FROM fact_test_scores t
LEFT JOIN dim_school s ON t.school_id = s.school_id;

-- 6. District Summary KPI View
CREATE OR REPLACE VIEW vw_district_summary AS
SELECT 
    s.district,
    COUNT(DISTINCT s.school_id) AS total_schools,
    SUM(s.total_enrolled_students) AS total_enrolled_students,
    AVG(att.avg_attendance_rate) AS avg_attendance_rate,
    AVG(att.proxy_anomaly_rate) AS proxy_anomaly_rate,
    AVG(infra.infrastructure_score) AS avg_infrastructure_score,
    AVG(infra.infrastructure_deficit_pct) AS avg_infrastructure_deficit,
    AVG(ts.avg_fln_score) AS avg_fln_score,
    SUM(mdm.total_quantity_kg) AS total_mdm_quantity_kg,
    SUM(mdm.total_cost) AS total_mdm_cost
FROM dim_school s
LEFT JOIN (
    SELECT school_id, 
           AVG(CASE WHEN data_quality_status = 'VALID' THEN attendance_rate END) AS avg_attendance_rate,
           (SUM(CASE WHEN is_proxy_attendance THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) AS proxy_anomaly_rate
    FROM fact_attendance
    GROUP BY school_id
) att ON s.school_id = att.school_id
LEFT JOIN (
    SELECT school_id, infrastructure_score, infrastructure_deficit_pct
    FROM dim_infrastructure_current
) infra ON s.school_id = infra.school_id
LEFT JOIN (
    SELECT school_id, AVG(score_percentage) AS avg_fln_score
    FROM fact_test_scores
    GROUP BY school_id
) ts ON s.school_id = ts.school_id
LEFT JOIN (
    SELECT school_id, SUM(quantity_kg) AS total_quantity_kg, SUM(total_cost) AS total_cost
    FROM fact_mdm_procurement
    GROUP BY school_id
) mdm ON s.school_id = mdm.school_id
GROUP BY s.district;
