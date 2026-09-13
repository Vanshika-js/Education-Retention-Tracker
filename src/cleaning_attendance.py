import pandas as pd
import numpy as np
from src.cleaning_ids import apply_school_id_normalization
from src.cleaning_dates import apply_date_normalization
from src.cleaning_boolean import apply_boolean_normalization

GRADE_MAPPING = {
    'I': 'Grade 1', '1': 'Grade 1', 'GRADE 1': 'Grade 1',
    'II': 'Grade 2', '2': 'Grade 2', 'GRADE 2': 'Grade 2',
    'III': 'Grade 3', '3': 'Grade 3', 'GRADE 3': 'Grade 3',
    'IV': 'Grade 4', '4': 'Grade 4', 'GRADE 4': 'Grade 4',
    'V': 'Grade 5', '5': 'Grade 5', 'GRADE 5': 'Grade 5',
    'VI': 'Grade 6', '6': 'Grade 6', 'GRADE 6': 'Grade 6',
    'VII': 'Grade 7', '7': 'Grade 7', 'GRADE 7': 'Grade 7',
    'VIII': 'Grade 8', '8': 'Grade 8', 'GRADE 8': 'Grade 8',
    'IX': 'Grade 9', '9': 'Grade 9', 'GRADE 9': 'Grade 9',
    'X': 'Grade 10', '10': 'Grade 10', 'GRADE 10': 'Grade 10',
    'XI': 'Grade 11', '11': 'Grade 11', 'GRADE 11': 'Grade 11',
    'XII': 'Grade 12', '12': 'Grade 12', 'GRADE 12': 'Grade 12'
}

def normalize_grade(val):
    if pd.isna(val):
        return 'Unknown'
    s = str(val).strip().upper()
    return GRADE_MAPPING.get(s, f"Grade {s}")

def clean_attendance(raw_df):
    """
    Cleans student attendance raw dataframe, performs validation, and flags anomalies.
    Returns: (cleaned_df, audit_stats_dict)
    """
    df = raw_df.copy()
    raw_row_count = len(df)

    # 1. Exact Duplicate Removal
    exact_duplicates_count = df.duplicated().sum()
    df = df.drop_duplicates().reset_index(drop=True)
    dedup_row_count = len(df)

    # 2. Universal Identifiers & Dates
    df = apply_school_id_normalization(df, 'school_id')
    df = apply_date_normalization(df, 'date')

    # 3. Grade Normalization
    df['grade_raw'] = df['grade'].astype(str)
    df['grade_clean'] = df['grade'].apply(normalize_grade)
    df['grade'] = df['grade_clean']

    # 4. Boolean Normalization
    df = apply_boolean_normalization(df, 'teacher_present')

    # 5. Impossible Attendance Detection (present > total)
    df['is_impossible_attendance'] = df['present_students'] > df['total_students']
    impossible_count = df['is_impossible_attendance'].sum()

    # 6. Attendance Rate Calculation (%)
    # For valid records: present / total * 100. Guard against total_students <= 0
    valid_mask = (df['total_students'] > 0) & (~df['is_impossible_attendance'])
    df['attendance_rate'] = np.where(
        valid_mask,
        (df['present_students'] / df['total_students']) * 100.0,
        np.nan
    )

    # 7. Weekend & Proxy Attendance Anomaly Detection
    dt_series = pd.to_datetime(df['date_clean'], errors='coerce')
    df['is_weekend'] = dt_series.dt.dayofweek >= 5  # Saturday=5, Sunday=6
    df['is_sunday'] = dt_series.dt.dayofweek == 6

    # Proxy attendance anomaly: 100% attendance recorded on Sundays/weekends or when present == total on a holiday
    df['is_proxy_attendance'] = (df['is_sunday']) & (df['present_students'] > 0) & (df['attendance_rate'] >= 99.9)
    proxy_count = df['is_proxy_attendance'].sum()

    # 8. Data Quality Status Flag
    conditions = [
        df['is_impossible_attendance'],
        df['is_proxy_attendance'],
        df['total_students'] <= 0,
        df['date_parse_error_flag']
    ]
    choices = [
        'INVALID_IMPOSSIBLE_ATTENDANCE',
        'ANOMALY_PROXY_SUNDAY',
        'INVALID_ZERO_TOTAL',
        'INVALID_DATE_FORMAT'
    ]
    df['data_quality_status'] = np.select(conditions, choices, default='VALID')

    audit_stats = {
        'raw_rows': raw_row_count,
        'exact_duplicates': exact_duplicates_count,
        'retained_rows': len(df),
        'impossible_attendance_count': int(impossible_count),
        'proxy_attendance_count': int(proxy_count),
        'valid_records_count': int((df['data_quality_status'] == 'VALID').sum())
    }

    return df, audit_stats
