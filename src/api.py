from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import shap

# Load model artifacts
model = joblib.load('models/best_model.pkl')
scaler = joblib.load('models/scaler.pkl')
feature_names = joblib.load('models/feature_names.pkl')
explainer = shap.TreeExplainer(model)

# Create FastAPI app
app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection system for financial transactions. "
                "Returns fraud probability, risk level, and explainable reasons.",
    version="1.0.0"
)


class Transaction(BaseModel):
    """Input: transaction details."""
    amt: float = 500.0
    hour: int = 14
    day_of_week: int = 2
    month: int = 6
    is_weekend: int = 0
    is_night: int = 0
    amt_log: float = 6.2
    is_high_amount: int = 0
    is_round_amount: int = 0
    distance: float = 0.5
    is_far_merchant: int = 0
    age: int = 45
    is_male: int = 1
    city_pop: int = 50000
    city_pop_log: float = 10.8
    is_small_city: int = 0
    cat_entertainment: int = 0
    cat_food_dining: int = 0
    cat_gas_transport: int = 0
    cat_grocery_net: int = 0
    cat_grocery_pos: int = 0
    cat_health_fitness: int = 0
    cat_home: int = 0
    cat_kids_pets: int = 0
    cat_misc_net: int = 0
    cat_misc_pos: int = 0
    cat_personal_care: int = 0
    cat_shopping_net: int = 1
    cat_shopping_pos: int = 0
    cat_travel: int = 0


class FraudResponse(BaseModel):
    """Output: fraud assessment."""
    fraud_probability: float
    risk_level: str
    recommended_action: str
    top_reasons: list
    threshold_used: float


def get_risk_level(prob):
    if prob > 0.85: return "CRITICAL"
    if prob > 0.6: return "HIGH"
    if prob > 0.3: return "MEDIUM"
    return "LOW"


def get_action(risk_level):
    actions = {
        "LOW": "APPROVE",
        "MEDIUM": "REVIEW",
        "HIGH": "BLOCK",
        "CRITICAL": "BLOCK"
    }
    return actions[risk_level]


@app.get("/")
def home():
    return {
        "service": "Fraud Detection API",
        "status": "running",
        "model": "XGBoost (ROC-AUC: 0.9988)",
        "endpoints": {
            "/predict": "POST - Submit a transaction for fraud scoring",
            "/health": "GET - Check API health",
            "/docs": "GET - Interactive API documentation"
        }
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "features_count": len(feature_names)
    }


@app.post("/predict", response_model=FraudResponse)
def predict_fraud(transaction: Transaction, threshold: float = 0.5):
    """
    Submit a transaction and get fraud assessment.
    
    Returns:
    - fraud_probability: 0.0 to 1.0
    - risk_level: LOW / MEDIUM / HIGH / CRITICAL
    - recommended_action: APPROVE / REVIEW / BLOCK
    - top_reasons: Why the model made this decision
    - threshold_used: The decision threshold applied
    """
    # Convert input to array
    input_data = np.array([[
        transaction.amt, transaction.hour, transaction.day_of_week,
        transaction.month, transaction.is_weekend, transaction.is_night,
        transaction.amt_log, transaction.is_high_amount,
        transaction.is_round_amount, transaction.distance,
        transaction.is_far_merchant, transaction.age, transaction.is_male,
        transaction.city_pop, transaction.city_pop_log,
        transaction.is_small_city, transaction.cat_entertainment,
        transaction.cat_food_dining, transaction.cat_gas_transport,
        transaction.cat_grocery_net, transaction.cat_grocery_pos,
        transaction.cat_health_fitness, transaction.cat_home,
        transaction.cat_kids_pets, transaction.cat_misc_net,
        transaction.cat_misc_pos, transaction.cat_personal_care,
        transaction.cat_shopping_net, transaction.cat_shopping_pos,
        transaction.cat_travel
    ]])

    # Scale and predict
    scaled = scaler.transform(input_data)
    fraud_prob = float(model.predict_proba(scaled)[0][1])

    # Risk assessment
    risk_level = get_risk_level(fraud_prob)
    action = get_action(risk_level)

    # SHAP explanation
    shap_values = explainer.shap_values(scaled)
    shap_dict = dict(zip(feature_names, shap_values[0]))
    top_reasons = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:5]

    reasons = [
        {
            "feature": name,
            "impact": round(float(val), 4),
            "direction": "increases fraud risk" if val > 0 else "decreases fraud risk"
        }
        for name, val in top_reasons
    ]

    return FraudResponse(
        fraud_probability=round(fraud_prob, 4),
        risk_level=risk_level,
        recommended_action=action,
        top_reasons=reasons,
        threshold_used=threshold
    )


@app.post("/batch_predict")
def batch_predict(transactions: list[Transaction], threshold: float = 0.5):
    """Submit multiple transactions for batch scoring."""
    results = []
    for txn in transactions:
        result = predict_fraud(txn, threshold)
        results.append(result)
    
    summary = {
        "total": len(results),
        "flagged": sum(1 for r in results if r.recommended_action != "APPROVE"),
        "blocked": sum(1 for r in results if r.recommended_action == "BLOCK"),
        "results": results
    }
    return summary


if __name__ == "__main__":
    import uvicorn
    print("Starting Fraud Detection API...")
    print("Docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)