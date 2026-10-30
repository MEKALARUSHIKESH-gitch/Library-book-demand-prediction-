import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_training_data():
    np.random.seed(42)
    n_samples = 5000
    
    prev_week = np.random.randint(0, 16, n_samples)

    # Use the expected demand directly so zero recent issues yield a zero forecast.
    expected_demand = prev_week.astype(float)
    
    # Classify the underlying expected demand, not noisy demo outcomes, so
    # increasing issue activity produces stable, ordered demand categories.
    categories = []
    for val in expected_demand:
        if val <= 2:
            categories.append("LOW")
        elif val <= 6:
            categories.append("MEDIUM")
        else:
            categories.append("HIGH")
            
    df = pd.DataFrame({
        'Previous_Week_Issues': prev_week,
        'Future_Demand': expected_demand,
        'Demand_Category': categories
    })
    return df

def train_and_save_models():
    df = generate_training_data()
    X = df[['Previous_Week_Issues']]
    
    y_reg = df['Future_Demand']
    y_clf = df['Demand_Category']
    
    # Train Linear Regression
    lr_model = LinearRegression()
    lr_model.fit(X, y_reg)
    
    # Train Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=300,
        min_samples_leaf=2,
        random_state=42,
    )
    rf_model.fit(X, y_clf)
    
    # Save models
    joblib.dump(lr_model, os.path.join(BASE_DIR, 'demand_regression_model.pkl'))
    joblib.dump(rf_model, os.path.join(BASE_DIR, 'demand_classification_model.pkl'))
    print("Models trained and saved successfully!")

if __name__ == "__main__":
    train_and_save_models()