from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_and_save_model(df, model_path="saved_xgboost_model.json"):
    features = ['Sweep_High', 'Sweep_Low', 'FVG_Bull', 'FVG_Bear', 'Session_NY', 'Trend', 'RSI']
    X = df[features]
    y = df['Target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    model = XGBClassifier(n_estimators=200, learning_rate=0.01, max_depth=4)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    model.save_model(model_path)
    return accuracy