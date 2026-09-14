-- DDL Schema definition for DuckDB Education & EdTech Warehouse

DROP TABLE IF EXISTS dim_school;
CREATE TABLE dim_school AS SELECT * FROM read_csv_auto('data/processed/clean_school_master.csv');

DROP TABLE IF EXISTS fact_attendance;
CREATE TABLE fact_attendance AS SELECT * FROM read_csv_auto('data/processed/clean_student_attendance.csv');

DROP TABLE IF EXISTS fact_mdm_procurement;
CREATE TABLE fact_mdm_procurement AS SELECT * FROM read_csv_auto('data/processed/clean_mdm_procurement.csv');

DROP TABLE IF EXISTS fact_infrastructure_history;
CREATE TABLE fact_infrastructure_history AS SELECT * FROM read_csv_auto('data/processed/clean_infrastructure_history.csv');

DROP TABLE IF EXISTS dim_infrastructure_current;
CREATE TABLE dim_infrastructure_current AS SELECT * FROM read_csv_auto('data/processed/clean_infrastructure_current.csv');

DROP TABLE IF EXISTS fact_test_scores;
CREATE TABLE fact_test_scores AS SELECT * FROM read_csv_auto('data/processed/clean_test_scores.csv');
