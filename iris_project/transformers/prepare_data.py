import pandas as pd
from sklearn.model_selection import train_test_split

def transform(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    df = df.copy()
    train_idx, test_idx = train_test_split(df.index, test_size=0.2, random_state=42)
    df["split"] = "train"
    df.loc[test_idx, "split"] = "test"
    return df
