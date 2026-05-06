from datetime import datetime
import pandas as pd

def check_for_time_validity(df_column: pd.Series) -> dict:
    results_dict = {
        'Total number of rows': df_column.shape[0],
        'Number of nulls': int(df_column.isnull().sum()),
        'Number of NaNs': int(df_column.isna().sum())
    }
    return results_dict

def is_datetime_column(df_column: pd.Series) -> bool:
    return pd.api.types.is_datetime64_any_dtype(df_column)

def string_to_datetime(date_string: str, format: str = '%Y-%m-%d %H:%M:%S') -> datetime:
    return datetime.strptime(date_string, format)

def check_for_monotonicity(time_column: pd.Series) -> int:
    # Note successive duplicates will not break monotonicity in this method.
    if time_column.is_monotonic_increasing:
        return 1
    elif time_column.is_monotonic_decreasing:
        return -1
    else:
        # no monotonicity found
        return 0

def check_for_duplicate_timestamps(time_column: pd.Series) -> int:
    # Total number of duplicates are returned.
    return int(time_column.duplicated().sum())

def utc_timezone_adjustment(
    time_column: pd.Series,
    original_timezone: str = 'UTC',
    ambiguous: bool | str = False,
) -> pd.Series:
    """
    Adjust the time column to UTC timezone, taking the original timezone of the data into account.

    On DST \"fall back\", the same local wall-clock time can occur twice; `ambiguous` tells pandas
    which instant to use when a value is ambiguous.

    `ambiguous='infer'` only works when those wall-clock times repeat in the Series so pandas can use
    ordering; a single `2018-10-28 02:39:00` in EU zones has no repeated label to infer from, and
    pandas raises ValueError. Prefer `False` (standard-time interpretation) or `True` (DST) for
    device logs, or `'NaT'` if you want ambiguous rows marked missing.

    `nonexistent`: local times skipped on \"spring forward\" are shifted to the next valid instant.

    Args:
        time_column: pandas Series of tz-naive datetime64 values
        original_timezone: timezone the naive values are in (e.g. device local zone)
        ambiguous: False | True | 'NaT' | 'infer' | 'raise' — see pandas `tz_localize`
    Returns:
        pandas Series of datetimes in UTC
    """
    _localized_time = time_column.dt.tz_localize( # using dt accessor to access datetime methods as operating under pandas timestamp type
        original_timezone,  # for an IoT device, this is the timezone of the device
        ambiguous= ambiguous,  # correct duplicates due to clocks going back for DST
        nonexistent='shift_forward',  # correct time jumps forward for DST
        )
    
    _adjusted_time = _localized_time.dt.tz_convert('UTC')
    return _adjusted_time
