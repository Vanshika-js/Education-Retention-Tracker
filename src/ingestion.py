import os
import json
import pandas as pd
import numpy as np
from datetime import datetime

from src.cleaning_master import clean_school_master
from src.cleaning_attendance import clean_attendance
from src.cleaning_mdm import clean_mdm
from src.cleaning_infrastructure import clean_infrastructure
from src.cleaning_scores import clean_test_scores

RAW_DIR = r"C:\Users\mangi\Desktop\Datathon"
PROCESSED_DIR = r"C:\Users\mangi\Desktop\Datathon\data\processed"
REPORTS_DIR = r"C:\Users\mangi\Desktop\Datathon\reports"

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def run_ingestion_and_rescue_pipeline():
    print("=== STARTING DATA RESCUE & GOVERNANCE PIPELINE ===")

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    audit_report = {
        'pipeline_execution_time': datetime.now().isoformat(),
        'datasets': {}
    }

    # 1. School Master
    print("\n[1/5] Rescuing track4_school_master.csv...")
    sm_raw = pd.read_csv(os.path.join(RAW_DIR, "track4_school_master.csv"))
    sm_clean, sm_audit = clean_school_master(sm_raw)
    sm_clean.to_csv(os.path.join(PROCESSED_DIR, "clean_school_master.csv"), index=False)
    audit_report['datasets']['school_master'] = sm_audit
    print(f"   Raw: {sm_audit['raw_rows']} | Clean: {sm_audit['retained_unique_schools']}")

    # 2. Attendance
    print("\n[2/5] Rescuing track4_student_attendance.csv...")
    att_raw = pd.read_csv(os.path.join(RAW_DIR, "track4_student_attendance.csv"))
    att_clean, att_audit = clean_attendance(att_raw)
    att_clean.to_csv(os.path.join(PROCESSED_DIR, "clean_student_attendance.csv"), index=False)
    audit_report['datasets']['student_attendance'] = att_audit
    print(f"   Raw: {att_audit['raw_rows']} | Clean: {att_audit['retained_rows']} | Impossible: {att_audit['impossible_attendance_count']} | Proxy Sunday: {att_audit['proxy_attendance_count']}")

    # 3. MDM Procurement
    print("\n[3/5] Rescuing track4_mid_day_meal_procurement.xlsx...")
    mdm_raw = pd.read_excel(os.path.join(RAW_DIR, "track4_mid_day_meal_procurement.xlsx"))
    mdm_clean, mdm_audit = clean_mdm(mdm_raw)
    mdm_clean.to_csv(os.path.join(PROCESSED_DIR, "clean_mdm_procurement.csv"), index=False)
    audit_report['datasets']['mdm_procurement'] = mdm_audit
    print(f"   Raw: {mdm_audit['raw_rows']} | Clean: {mdm_audit['retained_rows']} | Inferred Units: {mdm_audit['inferred_units_count']}")

    # 4. Infrastructure
    print("\n[4/5] Rescuing track4_school_infrastructure.csv...")
    infra_raw = pd.read_csv(os.path.join(RAW_DIR, "track4_school_infrastructure.csv"))
    infra_hist, infra_curr, infra_audit = clean_infrastructure(infra_raw)
    infra_hist.to_csv(os.path.join(PROCESSED_DIR, "clean_infrastructure_history.csv"), index=False)
    infra_curr.to_csv(os.path.join(PROCESSED_DIR, "clean_infrastructure_current.csv"), index=False)
    audit_report['datasets']['school_infrastructure'] = infra_audit
    print(f"   Raw: {infra_audit['raw_rows']} | History: {infra_audit['history_rows']} | Current Schools: {infra_audit['unique_schools_current']}")

    # 5. FLN Test Scores JSON
    print("\n[5/5] Rescuing track4_test_scores.json...")
    with open(os.path.join(RAW_DIR, "track4_test_scores.json"), 'r', encoding='utf-8') as f:
        scores_raw = pd.DataFrame(json.load(f))
    scores_clean, scores_audit = clean_test_scores(scores_raw)
    scores_clean.to_csv(os.path.join(PROCESSED_DIR, "clean_test_scores.csv"), index=False)
    audit_report['datasets']['test_scores'] = scores_audit
    print(f"   Raw: {scores_audit['raw_rows']} | Clean: {scores_audit['retained_rows']} | Valid Scores: {scores_audit['valid_scores_count']}")

    # Save JSON quality report
    json_path = os.path.join(REPORTS_DIR, "data_quality_report.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(audit_report, f, indent=2, cls=NpEncoder)

    # Save HTML quality report
    html_path = os.path.join(REPORTS_DIR, "data_quality_report.html")
    generate_html_quality_report(audit_report, html_path)

    print("\n=== PIPELINE COMPLETED SUCCESSFULLY ===")
    print(f"Quality report JSON: {json_path}")
    print(f"Quality report HTML: {html_path}")
    return audit_report

def generate_html_quality_report(report_data, output_path):
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Data Quality Audit Report — TransOrg AgentIQ Datathon</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 30px; }}
        h1 {{ color: #38bdf8; border-bottom: 2px solid #0284c7; padding-bottom: 10px; }}
        .timestamp {{ color: #94a3b8; font-size: 0.9em; margin-bottom: 25px; }}
        .card {{ background: #1e293b; border-radius: 10px; padding: 20px; margin-bottom: 20px; border: 1px solid #334155; }}
        h2 {{ color: #f43f5e; margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ border: 1px solid #334155; padding: 10px; text-align: left; }}
        th {{ background: #0f172a; color: #38bdf8; }}
        tr:nth-child(even) {{ background: #182234; }}
        .badge {{ background: #10b981; color: #fff; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em; }}
    </style>
</head>
<body>
    <h1>TransOrg AgentIQ Datathon — Data Quality & Governance Audit Report</h1>
    <div class="timestamp">Generated at: {report_data['pipeline_execution_time']}</div>
"""
    for ds_name, stats in report_data['datasets'].items():
        html_content += f"""
    <div class="card">
        <h2>Dataset: {ds_name.upper()}</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
"""
        for k, v in stats.items():
            val_str = str(v) if not isinstance(v, dict) else json.dumps(v)
            html_content += f"<tr><td>{k.replace('_', ' ').title()}</td><td><span class='badge'>{val_str}</span></td></tr>\n"
        html_content += "</table></div>"

    html_content += "</body></html>"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == "__main__":
    run_ingestion_and_rescue_pipeline()
