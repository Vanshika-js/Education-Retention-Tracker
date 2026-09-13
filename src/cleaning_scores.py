import re
import pandas as pd
import numpy as np
from src.cleaning_ids import apply_school_id_normalization
from src.cleaning_dates import apply_date_normalization

LETTER_GRADE_MAP = {
    'A+': 95.0,
    'A': 85.0,
    'B': 75.0,
    'C': 65.0,
    'D': 55.0,
    'E': 45.0,
    'F': 35.0
}

SUBJECT_MAP = {
    'MATH': 'Mathematics',
    'MATHEMATICS': 'Mathematics',
    'GANIT': 'Mathematics',
    'HINDI': 'Hindi',
    'ENGLISH': 'English',
    'PUNJABI': 'Punjabi',
    'EVS': 'EVS',
    'SCIENCE': 'Science'
}

def parse_score_to_percentage(avg_score, grading_scale, max_marks_json=None):
    """
    Parses heterogeneous test scores into score_percentage (0.0 to 100.0).
    Returns: (score_percentage, conversion_method, is_valid)
    """
    if pd.isna(avg_score) or avg_score is None:
        return (np.nan, 'MISSING_SCORE', False)

    s_score = str(avg_score).strip()
    s_scale = str(grading_scale).strip().lower() if pd.notna(grading_scale) else ''

    # 1. Percentage / % / pct
    if '%' in s_score or s_scale in ['pct', '%', 'percentage']:
        cleaned_num = s_score.replace('%', '').strip()
        try:
            val = float(cleaned_num)
            return (val, 'PERCENTAGE_DIRECT', True)
        except ValueError:
            return (np.nan, 'INVALID_PERCENTAGE', False)

    # 2. Letter Grade
    if s_score.upper() in LETTER_GRADE_MAP:
        pct = LETTER_GRADE_MAP[s_score.upper()]
        return (pct, 'LETTER_GRADE_MIDPOINT', True)

    # 3. Raw Marks (e.g. "21.6/50" or "45/50")
    if '/' in s_score:
        parts = s_score.split('/')
        try:
            num = float(parts[0])
            den = float(parts[1])
            if den > 0:
                pct = (num / den) * 100.0
                return (pct, 'RAW_MARKS_RATIO', True)
        except ValueError:
            return (np.nan, 'INVALID_RAW_MARKS', False)

    # 4. CGPA scale (e.g. 7.7 on scale of 10)
    if s_scale == 'cgpa' or (pd.notna(max_marks_json) and str(max_marks_json).strip() == '10'):
        try:
            val = float(s_score)
            pct = val * 9.5  # Project standard: CGPA * 9.5
            return (pct, 'CGPA_MULTIPLY_9_5', True)
        except ValueError:
            return (np.nan, 'INVALID_CGPA', False)

    # 5. Direct Float Fallback
    try:
        val = float(s_score)
        if pd.notna(max_marks_json) and str(max_marks_json).replace('.0', '').isdigit():
            max_m = float(max_marks_json)
            if max_m > 0 and max_m != 100:
                return ((val / max_m) * 100.0, 'RAW_MARKS_WITH_JSON_MAX', True)
        return (val, 'DIRECT_FLOAT', True)
    except ValueError:
        return (np.nan, 'UNPARSED_SCORE_ERROR', False)

def clean_test_scores(raw_df):
    """
    Cleans FLN test scores raw dataframe from JSON source.
    Returns: (cleaned_df, audit_stats_dict)
    """
    df = raw_df.copy()
    raw_row_count = len(df)

    # 1. Exact Duplicate Removal
    exact_duplicates_count = df.duplicated().sum()
    df = df.drop_duplicates().reset_index(drop=True)

    # 2. Universal Identifiers & Dates
    df = apply_school_id_normalization(df, 'school_id')
    df = apply_date_normalization(df, 'date')

    # 3. Subject Normalization
    df['subject_raw'] = df['subject'].astype(str)
    df['subject_clean'] = df['subject'].astype(str).str.strip().str.upper().map(SUBJECT_MAP).fillna(df['subject'].astype(str).str.title())
    df['subject'] = df['subject_clean']

    # 4. Score Parsing Lineage
    results = [
        parse_score_to_percentage(score, scale, max_m)
        for score, scale, max_m in zip(df['avg_score'], df['grading_scale'], df['max_marks'])
    ]

    df['grading_scale_raw'] = df['grading_scale'].astype(str)
    df['avg_score_raw'] = df['avg_score'].astype(str)

    df['score_percentage'] = [r[0] for r in results]
    df['score_conversion_method'] = [r[1] for r in results]
    df['score_valid_flag'] = [r[2] for r in results]

    # Breakdown by scale type
    scale_counts = df['grading_scale_raw'].value_counts().to_dict()

    audit_stats = {
        'raw_rows': raw_row_count,
        'exact_duplicates': exact_duplicates_count,
        'retained_rows': len(df),
        'scale_breakdown': scale_counts,
        'valid_scores_count': int(df['score_valid_flag'].sum()),
        'invalid_scores_count': int((~df['score_valid_flag']).sum())
    }

    return df, audit_stats
