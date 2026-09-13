import re
import pandas as pd

def normalize_school_id(val):
    """
    Normalizes messy school IDs to canonical format SCHXXXX.
    Inputs: 'SCH1001', 'SCH-1001', 'sch_1001', 'S1001', '286', 'SCH0050'
    Output: 'SCH0050', 'SCH0286', 'SCH1001'
    """
    if pd.isna(val) or val is None:
        return None
    val_str = str(val).strip().upper()
    # Extract trailing or embedded numeric digits
    match = re.search(r'(\d+)', val_str)
    if match:
        num = int(match.group(1))
        return f"SCH{num:04d}"
    return val_str

def apply_school_id_normalization(df, id_col='school_id'):
    """
    Applies normalize_school_id while preserving raw value and lineage audit flags.
    """
    raw_col = f"{id_col}_raw"
    clean_col = f"{id_col}_clean"
    flag_col = f"{id_col}_changed_flag"

    df[raw_col] = df[id_col].astype(str)
    df[clean_col] = df[id_col].apply(normalize_school_id)
    df[flag_col] = df[raw_col] != df[clean_col]
    df[id_col] = df[clean_col]
    return df
