# backend/app.py
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import joblib
import numpy as np
from datetime import datetime
import os

# Get the directory where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(file))

app = Flask(name)

# Allow CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": ["*", "null"]}}) # "null" for local file testing

# Load model and label encoders
try:
    model_path = os.path.join(BASE_DIR, 'model.joblib')
    encoders_path = os.path.join(BASE_DIR, 'label_encoders.joblib')

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    if not os.path.exists(encoders_path):
        raise FileNotFoundError(f"Encoders file not found at {encoders_path}")

    model = joblib.load(model_path)
    label_encoders = joblib.load(encoders_path)
except Exception as e:
    # Log this error properly in a real application
    print(f"Critical error: Failed to load model or encoders: {str(e)}")
    # For a production app, you might want to exit or have a fallback
    # For now, we'll let it run and it will fail on predict if models aren't loaded.
    # Or, raise a runtime error to prevent the app from starting incorrectly:
    raise RuntimeError(f"Failed to load model or encoders: {str(e)}")


@app.route("/predict", methods=['POST'])
def predict():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Basic validation for required fields (Pydantic did this automatically)
    required_fields = [
        'Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol',
        'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        # Prepare input data
        input_data = {
            'Age': int(data['Age']),
            'Sex': label_encoders['Sex'].transform([str(data['Sex'])])[0],
            'ChestPainType': label_encoders['ChestPainType'].transform([str(data['ChestPainType'])])[0],
            'RestingBP': int(data['RestingBP']),
            'Cholesterol': int(data['Cholesterol']),
            'FastingBS': int(data['FastingBS']),
            'RestingECG': label_encoders['RestingECG'].transform([str(data['RestingECG'])])[0],
            'MaxHR': int(data['MaxHR']),
            'ExerciseAngina': label_encoders['ExerciseAngina'].transform([str(data['ExerciseAngina'])])[0],
            'Oldpeak': float(data['Oldpeak']),
            'ST_Slope': label_encoders['ST_Slope'].transform([str(data['ST_Slope'])])[0]
        }

        # Convert to numpy array for prediction
        input_array = np.array([list(input_data.values())])

        # Make prediction
        prediction = model.predict(input_array)[0]
        probability = model.predict_proba(input_array)[0][1]

        # Create explanation
        explanation_base = ""
        if prediction == 1:
            explanation_base = "High risk of heart disease"
        else:
            explanation_base = "Low risk of heart disease"

        explanation_detail = ""
        if probability is not None:
            prob_for_predicted_class = probability # Using probability of the predicted class
            if prediction == 1: # High risk
                if prob_for_predicted_class > 0.7:
                    explanation_detail = "(strong indication)"
                elif prob_for_predicted_class > 0.5:
                    explanation_detail = "(moderate indication)"
                else: # This case might be less common if prediction is 1 and prob is low
                    explanation_detail = "(weak indication)"else: # Low risk (prediction == 0)
                # For low risk, we look at the probability of class 0.
                # If predict_proba returns [[P(0), P(1)]], then P(0) = 1 - P(1)
                # If model.predict_proba(input_array)[0][int(prediction)] gives P(0) when prediction is 0:
                if prob_for_predicted_class > 0.7: # High probability of being class 0 (low risk)
                    explanation_detail = "(very low risk)"
                elif prob_for_predicted_class > 0.5:
                    explanation_detail = "(likely low risk)"
                else: # Lower probability of being class 0
                    explanation_detail = "(slight risk remains, but classified low)"

        explanation = f"{explanation_base} {explanation_detail}".strip()


        return jsonify({
            "prediction": int(prediction),
            "probability": float(probability) if probability is not None else "N/A",
            # "probability_of_heart_disease": float(probability_class1) if hasattr(model, 'predict_proba') else "N/A", # If you want this specifically
            "explanation": explanation,
            "timestamp": datetime.now().isoformat()
        })
    except KeyError as e: # Specific error for missing keys in label_encoders or data
        return jsonify({"error": f"Invalid input value or unknown category for feature: {str(e)}"}), 400
    except ValueError as e: # For issues like transforming non-seen labels
        return jsonify({"error": f"Value error during processing: {str(e)}"}), 400
    except Exception as e:
        # Log the full error for debugging
        app.logger.error(f"Prediction error: {str(e)}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route("/")
def root():
    return jsonify({"message": "Heart Disease Prediction API - Kaggle Dataset Version (Flask)"})

# For PythonAnywhere or other WSGI servers, they will typically look for an 'application' callable.
# In Flask, the 'app' object itself is the WSGI application.
# So, if your WSGI config file directly imports 'app' from this file, you might not need this line.
# e.g., in your PythonAnywhere WSGI config: from backend.app import app as application
# However, if it expects 'application' to be defined *in* this file:
application = app

if name == 'main':
    # This is for local development testing only
    # For production, use a proper WSGI server like Gunicorn or Waitress
    app.run(debug=True, port=5000)