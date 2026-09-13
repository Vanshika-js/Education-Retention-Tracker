import pandas as pd
import numpy as np
import duckdb
from src.analytics import get_duckdb_connection, DB_PATH

def compute_welfare_risk_scores(db_path=DB_PATH):
    """
    Computes a transparent, multi-dimensional Welfare & Retention Risk Index (0-100) per school.
    Weights:
      - Attendance Risk (30%): 100 - attendance_rate
      - Learning Outcome Risk (25%): 100 - avg_fln_score
      - Infrastructure Deficit (20%): infrastructure_deficit_pct
      - MDM Regularity Proxy Risk (15%): procurement gap vs attendance
      - Data Quality Integrity Risk (10%): anomaly rate
    """
    conn = get_duckdb_connection(db_path)

    query = """
    SELECT 
        s.school_id,
        s.school_name,
        s.district,
        s.block,
        s.total_enrolled_students,
        COALESCE(att.avg_attendance_rate, 75.0) AS avg_attendance_rate,
        COALESCE(att.proxy_anomaly_rate, 0.0) AS proxy_anomaly_rate,
        COALESCE(infra.infrastructure_deficit_pct, 40.0) AS infrastructure_deficit_pct,
        COALESCE(infra.infrastructure_score, 60.0) AS infrastructure_score,
        COALESCE(ts.avg_fln_score, 65.0) AS avg_fln_score,
        COALESCE(mdm.total_quantity_kg, 0.0) AS total_mdm_kg
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
        SELECT school_id, SUM(quantity_kg) AS total_quantity_kg
        FROM fact_mdm_procurement
        GROUP BY school_id
    ) mdm ON s.school_id = mdm.school_id;
    """

    df = conn.execute(query).df()
    conn.close()

    # Sub-score calculations (normalized 0 to 100)
    df['attendance_risk'] = (100.0 - df['avg_attendance_rate']).clip(0, 100)
    df['learning_risk'] = (100.0 - df['avg_fln_score']).clip(0, 100)
    df['infrastructure_risk'] = df['infrastructure_deficit_pct'].clip(0, 100)
    
    # MDM Risk: if zero procurement relative to enrollment -> higher risk
    expected_kg = df['total_enrolled_students'] * 0.5  # Rough proxy baseline
    df['mdm_risk'] = np.where(df['total_mdm_kg'] < expected_kg, 60.0, 20.0)

    # Data Integrity Risk
    df['integrity_risk'] = df['proxy_anomaly_rate'].clip(0, 100)

    # Overall Composite Risk Index (0 - 100)
    df['welfare_risk_score'] = (
        (df['attendance_risk'] * 0.30) +
        (df['learning_risk'] * 0.25) +
        (df['infrastructure_risk'] * 0.20) +
        (df['mdm_risk'] * 0.15) +
        (df['integrity_risk'] * 0.10)
    ).round(2)

    # Categorization
    conditions = [
        (df['welfare_risk_score'] < 40),
        (df['welfare_risk_score'] >= 40) & (df['welfare_risk_score'] < 70),
        (df['welfare_risk_score'] >= 70)
    ]
    choices = ['Low Risk', 'Moderate Risk', 'High Risk']
    df['welfare_risk_category'] = np.select(conditions, choices, default='Moderate Risk')

    return df

def save_welfare_risk_view(db_path=DB_PATH):
    risk_df = compute_welfare_risk_scores(db_path)
    conn = duckdb.connect(db_path)
    conn.execute("DROP TABLE IF EXISTS fact_welfare_risk")
    conn.register('temp_risk', risk_df)
    conn.execute("CREATE TABLE fact_welfare_risk AS SELECT * FROM temp_risk")
    
    conn.execute("""
    CREATE OR REPLACE VIEW vw_school_welfare_risk AS 
    SELECT * FROM fact_welfare_risk
    """)
    conn.close()
    print("   Welfare Risk View registered in DuckDB successfully!")
    return risk_df

if __name__ == '__main__':
    save_welfare_risk_view()
