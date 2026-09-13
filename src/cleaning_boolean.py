import pandas as pd

TRUE_VARIANTS = {
    'TRUE', '1', 'Y', 'YES', 'H', 'HAI', 'HAAN', 
    'WORKING', 'FUNCTIONAL', 'AVAILABLE'
}

FALSE_VARIANTS = {
    'FALSE', '0', 'N', 'NO', 'NAHI', 'NAHI HAI', 'NA', 
    'KHARAB', 'BROKEN', 'UNDER REPAIR', 'NOT AVAILABLE'
}

def normalize_boolean(val):
    """
    Standardizes messy/multilingual boolean representations to True, False, or None (UNKNOWN).
    Never silently converts unknown or missing values to False.
    """
    if pd.isna(val) or val is None:
        return None
    val_str = str(val).strip().upper()
    if val_str in TRUE_VARIANTS:
        return True
    elif val_str in FALSE_VARIANTS:
        return False
    else:
        return None

def apply_boolean_normalization(df, col_name):
    """
    Applies boolean normalization to a specified column in a DataFrame while retaining audit lineage.
    """
    raw_col = f"{col_name}_raw"
    clean_col = f"{col_name}_clean"
    unknown_flag = f"{col_name}_is_unknown_flag"

    df[raw_col] = df[col_name].astype(str)
    df[clean_col] = df[col_name].apply(normalize_boolean)
    df[unknown_flag] = df[clean_col].isna()
    df[col_name] = df[clean_col]
    return df
