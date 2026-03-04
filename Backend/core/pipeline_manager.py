from core.data_loader import DataLoader
from core.data_cleaner import data_cleaner
from core.outlier_detector import clean


def run_pipeline(file_path, outlier_method="auto", outlier_action="remove", contamination=0.05):


    # Step 1: Load
    df = DataLoader().load(file_path)[0]

    # Step 2: Clean
    df = data_cleaner(df)

    # Step 3: Outlier detection + handling
    df= clean(df)

    return {
        "data": df,
    }