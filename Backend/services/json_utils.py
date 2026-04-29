import math
from datetime import date, datetime

import numpy as np
import pandas as pd


def to_json_safe(value):
    """
    Recursively convert pandas / NumPy values into plain Python types
    that FastAPI can serialize safely.
    """

    if isinstance(value, dict):
        return {
            str(to_json_safe(key)): to_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [to_json_safe(item) for item in value]

    if isinstance(value, np.generic):
        return value.item()

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()

    if value is pd.NA or value is pd.NaT:
        return None

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value

    return value
