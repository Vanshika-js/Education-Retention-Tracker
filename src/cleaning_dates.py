import re
from datetime import datetime
import pandas as pd

def parse_single_date(val_str):
    """
    Parses a single date string deterministically and flags ambiguities.
    Returns: (parsed_date_iso_str, parse_method, is_ambiguous, is_error)
    """
    if pd.isna(val_str) or not str(val_str).strip():
        return (None, "MISSING", False, True)

    s = str(val_str).strip()

    # 1. ISO format: YYYY-MM-DD or YYYY/MM/DD
    m_iso = re.match(r'^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$', s)
    if m_iso:
        y, m, d = int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3))
        try:
            dt = datetime(y, m, d)
            return (dt.strftime('%Y-%m-%d'), "ISO_FORMAT", False, False)
        except ValueError:
            return (None, "INVALID_ISO", False, True)

    # 2. Text month format: e.g., 10-Apr-2025 or 02-Jun-25
    for fmt in ('%d-%b-%Y', '%d-%b-%y', '%d-%B-%Y'):
        try:
            dt = datetime.strptime(s, fmt)
            return (dt.strftime('%Y-%m-%d'), "TEXT_MONTH", False, False)
        except ValueError:
            pass

    # 3. Dot format: DD.MM.YYYY vs MM.DD.YYYY
    m_dot = re.match(r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$', s)
    if m_dot:
        n1, n2, y = int(m_dot.group(1)), int(m_dot.group(2)), int(m_dot.group(3))
        if n1 > 12:  # Must be DD.MM.YYYY
            try:
                dt = datetime(y, n2, n1)
                return (dt.strftime('%Y-%m-%d'), "DOT_DD_MM_YYYY", False, False)
            except ValueError:
                return (None, "INVALID_DOT", False, True)
        elif n2 > 12:  # Must be MM.DD.YYYY
            try:
                dt = datetime(y, n1, n2)
                return (dt.strftime('%Y-%m-%d'), "DOT_MM_DD_YYYY", False, False)
            except ValueError:
                return (None, "INVALID_DOT", False, True)
        else:
            # Ambiguous (n1 <= 12 and n2 <= 12). Standard Indian dataset convention: DD.MM.YYYY
            try:
                dt = datetime(y, n2, n1)
                return (dt.strftime('%Y-%m-%d'), "DOT_DD_MM_AMBIGUOUS", True, False)
            except ValueError:
                return (None, "INVALID_DOT", False, True)

    # 4. Dash / Slash format: e.g. 07-26-2025 or 21-04-2025
    m_sep = re.match(r'^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$', s)
    if m_sep:
        n1, n2, y = int(m_sep.group(1)), int(m_sep.group(2)), int(m_sep.group(3))
        if n1 > 12:  # Must be DD-MM-YYYY
            try:
                dt = datetime(y, n2, n1)
                return (dt.strftime('%Y-%m-%d'), "DASH_DD_MM_YYYY", False, False)
            except ValueError:
                return (None, "INVALID_DASH", False, True)
        elif n2 > 12:  # Must be MM-DD-YYYY
            try:
                dt = datetime(y, n1, n2)
                return (dt.strftime('%Y-%m-%d'), "DASH_MM_DD_YYYY", False, False)
            except ValueError:
                return (None, "INVALID_DASH", False, True)
        else:
            # Ambiguous (n1 <= 12 and n2 <= 12). Check if MM-DD or DD-MM. Default to MM-DD-YYYY if n2 <= 31
            try:
                dt = datetime(y, n1, n2)
                return (dt.strftime('%Y-%m-%d'), "DASH_MM_DD_AMBIGUOUS", True, False)
            except ValueError:
                try:
                    dt = datetime(y, n2, n1)
                    return (dt.strftime('%Y-%m-%d'), "DASH_DD_MM_AMBIGUOUS", True, False)
                except ValueError:
                    return (None, "INVALID_DASH", False, True)

    # Fallback to pd.to_datetime
    try:
        dt = pd.to_datetime(s, errors='coerce')
        if pd.notna(dt):
            return (dt.strftime('%Y-%m-%d'), "PANDAS_FALLBACK", True, False)
    except Exception:
        pass

    return (None, "UNPARSED_ERROR", False, True)

def apply_date_normalization(df, date_col='date'):
    """
    Applies date normalization while retaining raw value and detailed audit flags.
    """
    raw_col = f"{date_col}_raw"
    clean_col = f"{date_col}_clean"
    method_col = f"{date_col}_parse_method"
    ambig_col = f"{date_col}_ambiguous_flag"
    err_col = f"{date_col}_parse_error_flag"

    df[raw_col] = df[date_col].astype(str)

    results = df[date_col].apply(parse_single_date)
    df[clean_col] = [r[0] for r in results]
    df[method_col] = [r[1] for r in results]
    df[ambig_col] = [r[2] for r in results]
    df[err_col] = [r[3] for r in results]

    df[date_col] = df[clean_col]
    return df
