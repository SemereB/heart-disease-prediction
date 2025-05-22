# backend/train_model.py
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier  # Changed to GradientBoosting
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from sklearn.preprocessing import LabelEncoder

def load_and_preprocess_data():
    # Load the dataset
    df = pd.read_csv('heart.csv')
    
    # Convert categorical variables to numerical
    categorical_cols = ['Sex', 'ChestPainType', 'RestingECG', 'ExerciseAngina', 'ST_Slope']
    label_encoders = {}
    
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
    
    # Save the label encoders
    joblib.dump(label_encoders, 'label_encoders.joblib')
    
    # Separate features and target
    X = df.drop('HeartDisease', axis=1)
    y = df['HeartDisease']
    
    return X, y

def train_and_save_model():
    X, y = load_and_preprocess_data()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Gradient Boosting Classifier
    model = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Gradient Boosting Model Accuracy: {accuracy:.2f}")
    
    # Save model
    joblib.dump(model, 'model.joblib')
    print("Model saved as model.joblib")

if name == "main":
    train_and_save_model()