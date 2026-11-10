import os
import pandas as pd

if 'data_exporter' not in globals():
    try:
        from mage_ai.data_preparation.decorators import data_exporter
    except ImportError:
        def data_exporter(func):
            return func

if 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test
    except ImportError:
        def test(func):
            return func

@data_exporter
def export_data(data, *args, **kwargs) -> None:
    # If a dict was passed, extract 'predictions'; otherwise data is already the DataFrame
    if isinstance(data, dict):
        df = data.get('predictions', pd.DataFrame())
    else:
        df = data

    csv_path = 'iris_predictions.csv'
    df.to_csv(csv_path, index=False)
    print(f"Exported predictions successfully to {csv_path}")

@test
def test_export(*args, **kwargs) -> None:
    assert os.path.exists('iris_predictions.csv'), 'iris_predictions.csv was not created'
