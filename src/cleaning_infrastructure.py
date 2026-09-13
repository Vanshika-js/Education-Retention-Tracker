import pandas as pd
import numpy as np
from src.cleaning_ids import apply_school_id_normalization
from src.cleaning_dates import apply_date_normalization
from src.cleaning_boolean import apply_boolean_normalization

INFRA_COLS = [
    'has_electricity',
    'has_drinking_water',
    'has_functional_toilet',
    'has_boundary_wall',
    'has_playground'
]

def clean_infrastructure(raw_df):
    """
    Cleans school infrastructure raw dataframe, standardizes booleans,
    computes deficit scores, and produces historical vs current dataframes.
    Returns: (history_df, current_df, audit_stats_dict)
    """
    df = raw_df.copy()
    raw_row_count = len(df)

    # 1. Exact Duplicate Removal
    exact_duplicates_count = df.duplicated().sum()
    df = df.drop_duplicates().reset_index(drop=True)

    # 2. Universal Identifiers & Dates
    df = apply_school_id_normalization(df, 'school_id')
    df = apply_date_normalization(df, 'date')

    # 3. Boolean Normalization across all 5 infrastructure fields
    for col in INFRA_COLS:
        df = apply_boolean_normalization(df, col)

    # 4. Score & Deficit Calculations
    # Count of TRUE amenities
    true_counts = np.zeros(len(df))
    false_counts = np.zeros(len(df))
    valid_counts = np.zeros(len(df))

    for col in INFRA_COLS:
        is_true = (df[col] == True).astype(int)
        is_false = (df[col] == False).astype(int)
        is_valid = df[col].notna().astype(int)

        true_counts += is_true
        false_counts += is_false
        valid_counts += is_valid

    df['amenities_functional_count'] = true_counts
    df['amenities_deficit_count'] = false_counts
    df['infrastructure_score'] = np.where(valid_counts > 0, (true_counts / 5.0) * 100.0, np.nan)
    df['infrastructure_deficit_pct'] = np.where(valid_counts > 0, (false_counts / 5.0) * 100.0, np.nan)

    # 5. Build infrastructure_history
    history_df = df.copy()

    # 6. Build infrastructure_current (latest valid inspection date per school)
    # Sort by school_id and date_clean descending
    sorted_df = df.sort_values(by=['school_id', 'date_clean'], ascending=[True, False])
    current_df = sorted_df.groupby('school_id').first().reset_index()

    audit_stats = {
        'raw_rows': raw_row_count,
        'exact_duplicates': exact_duplicates_count,
        'history_rows': len(history_df),
        'unique_schools_current': len(current_df),
        'normalized_booleans_count': int((len(history_df) * len(INFRA_COLS)))
    }

    return history_df, current_df, audit_stats
