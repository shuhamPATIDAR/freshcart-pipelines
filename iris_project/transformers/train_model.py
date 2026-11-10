import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

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
def train(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    max_depth = int(kwargs.get('max_depth', 3))
    
    # Identify target column name safely
    target_col = 'target' if 'target' in df.columns else df.columns[-2]
    
    train_df = df[df['split'] == 'train']
    test_df = df[df['split'] == 'test'].copy()
    
    feature_cols = [c for c in df.columns if c not in [target_col, 'split']]
    X_train, y_train = train_df[feature_cols], train_df[target_col]
    X_test, y_test = test_df[feature_cols], test_df[target_col]
    
    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))
    print(f"DecisionTree (max_depth={max_depth}) -> Test Accuracy: {acc:.4f}")
    
    # Explicitly ensure target and predicted_target are attached
    test_df['target'] = y_test.values
    test_df['predicted_target'] = y_pred
    
    return test_df

@test
def test_accuracy(output: pd.DataFrame, *args) -> None:
    acc = accuracy_score(output['target'], output['predicted_target'])
    assert acc >= 0.90, f"Model accuracy {acc:.4f} is below the 0.90 threshold"
