from core.data_loader import DataLoader
from core.data_cleaner import data_cleaner
from core.outlier_detector import OutlierDetector
from ml.imputers import DataImputer

load_data = lambda file_path: DataLoader().load(file_path)[0]

def run_pipeline(file_path):

    df = load_data(file_path)

    df = data_cleaner(df)

    imputer = DataImputer(strategy="knn")
    df, impute_report = imputer.fit_transform(df)

    outlier_detector = OutlierDetector(contamination=0.05)
    df, outlier_report = outlier_detector.detect(df)

    return {
        "data": df,
        "imputation": impute_report,
        "outliers": outlier_report
    }
