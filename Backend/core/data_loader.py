import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any


class DataLoader:
    """
    Responsible only for loading datasets.
    Supports CSV, Excel, and JSON.
    Returns DataFrame + metadata.
    """

    SUPPORTED_FORMATS = {".csv", ".xlsx", ".xls", ".json"}

    def __init__(self, encoding: str = "utf-8"):
        self.encoding = encoding

    def load(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Load dataset and return:
        - DataFrame
        - Metadata dictionary
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file format: {path.suffix}. "
                f"Supported formats: {self.SUPPORTED_FORMATS}"
            )

        if path.suffix.lower() == ".csv":
            df = self._load_csv(path)

        elif path.suffix.lower() in [".xlsx", ".xls"]:
            df = self._load_excel(path)

        elif path.suffix.lower() == ".json":
            df = self._load_json(path)

        if df.empty:
            raise ValueError("Loaded dataset is empty.")

        metadata = self._generate_metadata(df, path)

        return df, metadata

    # ---------- Private Loaders ---------- #

    def _load_csv(self, path: Path) -> pd.DataFrame:
        try:
            return pd.read_csv(path, encoding=self.encoding)
        except UnicodeDecodeError:
            # Fallback encoding
            return pd.read_csv(path, encoding="latin1")
        except Exception as e:
            raise ValueError(f"Failed to load CSV file: {e}")

    def _load_excel(self, path: Path) -> pd.DataFrame:
        try:
            return pd.read_excel(path)
        except Exception as e:
            raise ValueError(f"Failed to load Excel file: {e}")

    def _load_json(self, path: Path) -> pd.DataFrame:
        try:
            return pd.read_json(path)
        except ValueError:
            # Try lines=True format (common in logs / big data)
            return pd.read_json(path, lines=True)
        except Exception as e:
            raise ValueError(f"Failed to load JSON file: {e}")

    # ---------- Metadata ---------- #

    def _generate_metadata(self, df: pd.DataFrame, path: Path) -> Dict[str, Any]:
        return {
            "file_name": path.name,
            "file_size_mb": round(path.stat().st_size / (1024 * 1024), 2),
            "rows": df.shape[0],
            "columns": df.shape[1],
            "column_names": df.columns.tolist(),
            "memory_usage_mb": round(
                df.memory_usage(deep=True).sum() / (1024 * 1024), 2
            ),
        }
