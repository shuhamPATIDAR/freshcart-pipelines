import pandas as pd
from sklearn.model_selection import train_test_split

# Safe decorator loading: works inside Mage AND outside in pytest
if 'transformer' not in globals():
    try:
        from mage_ai.data_preparation.decorators import transformer
    except ImportError:
        def transformer(func):
            return func

if 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test
    except ImportError:
        def test(func):
            return func

@transformer
def transform(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    df = df.copy()
    test_size = float(kwargs.get('test_size', 0.2))
    train_idx, test_idx = train_test_split(df.index, test_size=test_size, random_state=42)
    df['split'] = 'train'
    df.loc[test_idx, 'split'] = 'test'
    print(f"Data prepared: {sum(df['split']=='train')} train rows, {sum(df['split']=='test')} test rows")
    return df

@test
def test_split_proportions(output, *args) -> None:
    assert 'split' in output.columns, 'Split column not found'
    assert (output['split'] == 'train').sum() > 0, 'No training rows found'
    assert (output['split'] == 'test').sum() > 0, 'No testing rows found'