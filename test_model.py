import pandas as pd
from model import StrokeRiskModel

def test_model():
    print("Testing model initialization...")
    model = StrokeRiskModel()
    
    print("\nTesting prediction...")
    test_data = {
        'gender': 'Male',
        'age': 67.0,
        'hypertension': 0,
        'heart_disease': 1,
        'ever_married': 'Yes',
        'work_type': 'Private',
        'Residence_type': 'Urban',
        'avg_glucose_level': 228.69,
        'bmi': 36.6,
        'smoking_status': 'formerly smoked'
    }
    
    try:
        risk = model.predict(test_data)
        print(f"Prediction successful! Stroke risk: {risk:.2%}")
    except Exception as e:
        print(f"Error during prediction: {str(e)}")

if __name__ == "__main__":
    test_model() 