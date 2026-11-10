from sklearn.metrics import confusion_matrix, classification_report
import pandas as pd

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
def evaluate(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    # Safely find actual target and predicted columns
    target_col = 'target' if 'target' in df.columns else [c for c in df.columns if 'target' in c and c != 'predicted_target'][0]
    pred_col = 'predicted_target' if 'predicted_target' in df.columns else df.columns[-1]
    
    y_test = df[target_col]
    y_pred = df[pred_col]
    
    cm = confusion_matrix(y_test, y_pred)
    cr = classification_report(y_test, y_pred, output_dict=True)
    report_df = pd.DataFrame(cr).transpose()
    
    print("Confusion Matrix:\n", cm)
    print("Classification Report:\n", report_df)
    return report_df

@test
def test_evaluation(output: pd.DataFrame, *args) -> None:
    assert not output.empty, 'Evaluation report DataFrame is empty'
