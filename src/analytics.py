import os
import duckdb

DB_PATH = r"C:\Users\mangi\Desktop\Datathon\data\processed\education_warehouse.duckdb"
PROCESSED_DIR = r"C:\Users\mangi\Desktop\Datathon\data\processed"
SQL_DIR = r"C:\Users\mangi\Desktop\Datathon\sql"

def get_duckdb_connection(db_path=DB_PATH):
    """
    Returns an active DuckDB connection, initializing tables and views if needed.
    """
    conn = duckdb.connect(db_path)
    return conn

def initialize_warehouse(db_path=DB_PATH):
    """
    Reads cleaned CSV files from data/processed/, builds Star Schema tables and analytical SQL views.
    """
    print(f"=== INITIALIZING DUCKDB ANALYTICAL WAREHOUSE: {db_path} ===")
    
    # Remove existing DB file if refreshing
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass

    conn = duckdb.connect(db_path)

    # 1. Register Dim School
    sm_path = os.path.join(PROCESSED_DIR, "clean_school_master.csv").replace('\\', '/')
    conn.execute(f"CREATE TABLE dim_school AS SELECT * FROM read_csv_auto('{sm_path}')")
    
    # 2. Register Fact Attendance
    att_path = os.path.join(PROCESSED_DIR, "clean_student_attendance.csv").replace('\\', '/')
    conn.execute(f"CREATE TABLE fact_attendance AS SELECT * FROM read_csv_auto('{att_path}')")
    
    # 3. Register Fact MDM Procurement
    mdm_path = os.path.join(PROCESSED_DIR, "clean_mdm_procurement.csv").replace('\\', '/')
    conn.execute(f"CREATE TABLE fact_mdm_procurement AS SELECT * FROM read_csv_auto('{mdm_path}')")
    
    # 4. Register Fact Infrastructure History
    inf_h_path = os.path.join(PROCESSED_DIR, "clean_infrastructure_history.csv").replace('\\', '/')
    conn.execute(f"CREATE TABLE fact_infrastructure_history AS SELECT * FROM read_csv_auto('{inf_h_path}')")

    # 5. Register Dim Infrastructure Current
    inf_c_path = os.path.join(PROCESSED_DIR, "clean_infrastructure_current.csv").replace('\\', '/')
    conn.execute(f"CREATE TABLE dim_infrastructure_current AS SELECT * FROM read_csv_auto('{inf_c_path}')")

    # 6. Register Fact Test Scores
    ts_path = os.path.join(PROCESSED_DIR, "clean_test_scores.csv").replace('\\', '/')
    conn.execute(f"CREATE TABLE fact_test_scores AS SELECT * FROM read_csv_auto('{ts_path}')")

    print("   Tables created successfully!")

    # 7. Apply Views DDL
    with open(os.path.join(SQL_DIR, "views.sql"), 'r', encoding='utf-8') as f:
        views_sql = f.read()

    for stmt in views_sql.split(';'):
        stmt_clean = stmt.strip()
        if stmt_clean:
            conn.execute(stmt_clean)

    print("   SQL Views registered successfully!")
    
    # Quick sanity check query
    d_count = conn.execute("SELECT COUNT(*) FROM vw_district_summary").fetchone()[0]
    print(f"   Sanity check: vw_district_summary contains {d_count} districts.")

    conn.close()
    return DB_PATH

if __name__ == '__main__':
    initialize_warehouse()
