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
def export_metrics(data, *args, **kwargs) -> None:
    if isinstance(data, dict):
        report_df = data.get('report', pd.DataFrame())
    else:
        report_df = data

    csv_path = 'iris_metrics.csv'
    report_df.to_csv(csv_path)
    print(f"Metrics written successfully to {csv_path}")

@test
def test_metrics_file(*args, **kwargs) -> None:
    assert os.path.exists('iris_metrics.csv'), 'iris_metrics.csv was not created'
