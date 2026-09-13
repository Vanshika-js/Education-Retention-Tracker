import pandas as pd
from src.cleaning_ids import apply_school_id_normalization

def clean_school_master(raw_df):
    """
    Cleans school master dimension table, standardizes district names and casing.
    Returns: (cleaned_df, audit_stats_dict)
    """
    df = raw_df.copy()
    raw_row_count = len(df)

    # 1. Exact Duplicate Removal
    exact_duplicates_count = df.duplicated().sum()
    df = df.drop_duplicates().reset_index(drop=True)

    # 2. Universal Identifiers
    df = apply_school_id_normalization(df, 'school_id')

    # 3. District & Block Casing Normalization
    df['district_raw'] = df['district'].astype(str)
    df['district_clean'] = df['district'].fillna('Unknown District').astype(str).str.strip().str.title()
    df['district'] = df['district_clean']

    df['block_raw'] = df['block'].astype(str)
    df['block_clean'] = df['block'].fillna('Unknown Block').astype(str).str.strip().str.title()
    df['block'] = df['block_clean']

    # 4. School Type & Medium Casing
    df['school_type'] = df['school_type'].fillna('Unknown').astype(str).str.strip().str.title()
    df['medium'] = df['medium'].fillna('Unknown').astype(str).str.strip().str.title()

    # 5. Handle duplicate school_ids if any remain after normalization
    # Keep the record with non-null district/block or highest enrollment
    df = df.sort_values(by=['school_id', 'total_enrolled_students'], ascending=[True, False])
    df = df.groupby('school_id').first().reset_index()

    audit_stats = {
        'raw_rows': raw_row_count,
        'exact_duplicates': exact_duplicates_count,
        'retained_unique_schools': len(df),
        'missing_districts_imputed': int((df['district_raw'] == 'nan').sum() + (df['district_raw'] == 'None').sum())
    }

    return df, audit_stats
