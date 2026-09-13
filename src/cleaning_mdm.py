import re
import pandas as pd
import numpy as np
from src.cleaning_ids import apply_school_id_normalization
from src.cleaning_dates import apply_date_normalization

GRAIN_MAPPING = {
    'RICE': 'Rice', 'CHAWAL': 'Rice', 'RICE/CHAWAL': 'Rice',
    'WHEAT': 'Wheat', 'GEHUN': 'Wheat', 'ATTA': 'Wheat',
    'DAL': 'Pulses', 'DAAL': 'Pulses', 'PULSES': 'Pulses', 'LENTILS': 'Pulses',
    'MUSTARD OIL': 'Oil', 'SARSON TEL': 'Oil', 'OIL': 'Oil', 'COOKING OIL': 'Oil'
}

VENDOR_MAPPING = {
    'KUMAR & CO.': 'Kumar Enterprises',
    'KUMAR GENERAL STORE': 'Kumar Enterprises',
    'KUMAR SUPPLIES': 'Kumar Enterprises',
    'SINGH BROTHERS': 'Singh Agro Group',
    'SINGH AGRO': 'Singh Agro Group',
    'S. AGRO WORKS': 'Singh Agro Group',
    'SHARMA & SONS': 'Sharma Traders',
    'SHARMA TRADERS PVT LTD': 'Sharma Traders',
    'SHARMA TRADERS': 'Sharma Traders',
    'GOYAL ENTERPRISES': 'Goyal Mills',
    'GOYAL MILL': 'Goyal Mills',
    'GOYAL RICE MILL': 'Goyal Mills'
}

def clean_quantity_and_unit(val_qty, val_unit):
    """
    Parses quantity and unit, converting all quantities to Kilograms (KG).
    Rule: 1 Bag / Sack / Bori = 50 KG. 1 Gram = 0.001 KG.
    Returns: (quantity_kg, unit_clean, conversion_method, unit_inferred_flag)
    """
    if pd.isna(val_qty) and pd.isna(val_unit):
        return (np.nan, 'Unknown', 'MISSING_QUANTITY_AND_UNIT', True)

    qty_num = np.nan
    parsed_unit = str(val_unit).strip().lower() if pd.notna(val_unit) else None

    # Parse quantity value (could be float or string like "14.9 kg")
    if pd.notna(val_qty):
        s_qty = str(val_qty).strip()
        match = re.search(r'(\d+\.?\d*)\s*([a-zA-Z]+)?', s_qty)
        if match:
            qty_num = float(match.group(1))
            if match.group(2) and not parsed_unit:
                parsed_unit = match.group(2).lower()

    if pd.isna(qty_num):
        return (np.nan, 'Unknown', 'UNPARSED_QUANTITY', True)

    # Unit conversion logic
    unit_inferred = False
    conversion_method = "DIRECT"

    if parsed_unit in ['kg', 'kgs', 'kilogram', 'kilograms']:
        qty_kg = qty_num
        unit_clean = 'KG'
    elif parsed_unit in ['g', 'gram', 'grams']:
        qty_kg = qty_num * 0.001
        unit_clean = 'KG'
        conversion_method = "GRAMS_TO_KG"
    elif parsed_unit in ['50kg bags', 'bags', 'sacks', 'bori', 'bag', 'sack']:
        qty_kg = qty_num * 50.0
        unit_clean = 'KG'
        conversion_method = "BAGS_50KG_TO_KG"
    else:
        # Unit missing or unrecognized: infer based on quantity range
        unit_inferred = True
        if qty_num > 500:
            qty_kg = qty_num * 0.001
            unit_clean = 'KG'
            conversion_method = "INFERRED_GRAMS_TO_KG"
        elif qty_num <= 10:
            qty_kg = qty_num * 50.0
            unit_clean = 'KG'
            conversion_method = "INFERRED_BAGS_TO_KG"
        else:
            qty_kg = qty_num
            unit_clean = 'KG'
            conversion_method = "INFERRED_ASSUMED_KG"

    return (qty_kg, unit_clean, conversion_method, unit_inferred)

def clean_cost(val_cost):
    """
    Cleans cost text strings into numeric FLOAT values.
    Handles '₹644', 'Rs. 1,600', '336/-', '1,710/-', etc.
    """
    if pd.isna(val_cost) or val_cost is None:
        return np.nan
    s = str(val_cost).replace('₹', '').replace('Rs.', '').replace('Rs', '').replace('/-', '').replace(',', '').strip()
    try:
        return float(s)
    except ValueError:
        return np.nan

def clean_mdm(raw_df):
    """
    Cleans Mid-Day Meal procurement raw dataframe.
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

    # 3. Grain & Vendor Normalization
    df['grain_raw'] = df['grain_type'].astype(str)
    df['grain_clean'] = df['grain_type'].astype(str).str.strip().str.upper().map(GRAIN_MAPPING).fillna('Other')
    df['grain_type'] = df['grain_clean']

    df['vendor_raw'] = df['vendor_name'].astype(str)
    df['vendor_clean'] = df['vendor_name'].astype(str).str.strip().str.upper().map(VENDOR_MAPPING).fillna(df['vendor_name'].astype(str).str.title())
    df['vendor_name'] = df['vendor_clean']

    # 4. Quantity & Unit Normalization
    results = [clean_quantity_and_unit(q, u) for q, u in zip(df['quantity'], df['unit'])]
    df['quantity_raw'] = df['quantity'].astype(str)
    df['unit_raw'] = df['unit'].astype(str)

    df['quantity_kg'] = [r[0] for r in results]
    df['unit_clean'] = [r[1] for r in results]
    df['conversion_method'] = [r[2] for r in results]
    df['unit_inferred_flag'] = [r[3] for r in results]

    # 5. Cost Cleaning
    df['cost_raw'] = df['total_cost'].astype(str)
    df['total_cost_numeric'] = df['total_cost'].apply(clean_cost)
    df['total_cost'] = df['total_cost_numeric']

    # Cost per KG calculation
    df['cost_per_kg'] = np.where(
        (df['quantity_kg'] > 0) & (pd.notna(df['total_cost_numeric'])),
        df['total_cost_numeric'] / df['quantity_kg'],
        np.nan
    )

    # 6. Payment Status Normalization
    status_map = {
        'PAID': 'Paid', 'CLEARED': 'Paid',
        'PENDING': 'Pending', 'DUE': 'Pending'
    }
    df['payment_status_raw'] = df['payment_status'].astype(str)
    df['payment_status_clean'] = df['payment_status'].astype(str).str.strip().str.upper().map(status_map).fillna('Unknown')
    df['payment_status'] = df['payment_status_clean']

    audit_stats = {
        'raw_rows': raw_row_count,
        'exact_duplicates': exact_duplicates_count,
        'retained_rows': len(df),
        'missing_units_count': int(df['unit_raw'].isna().sum() + (df['unit_raw'] == 'nan').sum()),
        'inferred_units_count': int(df['unit_inferred_flag'].sum()),
        'invalid_costs_count': int(df['total_cost_numeric'].isna().sum())
    }

    return df, audit_stats
