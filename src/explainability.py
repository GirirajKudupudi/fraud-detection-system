import pandas as pd
import numpy as np
import shap
import joblib
import json


def explain_prediction(transaction_data, model, scaler, feature_names):
    """Explain WHY a transaction was flagged as fraud."""
    # Scale the input
    scaled = scaler.transform([transaction_data])
    
    # Get prediction
    fraud_prob = model.predict_proba(scaled)[0][1]
    
    # Get SHAP values
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(scaled)
    
    # Get top reasons
    shap_dict = dict(zip(feature_names, shap_values[0]))
    top_reasons = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
    
    # Build explanation
    risk_level = "LOW"
    if fraud_prob > 0.3: risk_level = "MEDIUM"
    if fraud_prob > 0.6: risk_level = "HIGH"
    if fraud_prob > 0.85: risk_level = "CRITICAL"
    
    action = "APPROVE"
    if risk_level == "MEDIUM": action = "REVIEW"
    if risk_level in ["HIGH", "CRITICAL"]: action = "BLOCK"
    
    explanation = {
        "fraud_probability": round(float(fraud_prob), 4),
        "risk_level": risk_level,
        "recommended_action": action,
        "top_reasons": [
            {"feature": name, "impact": round(float(val), 4),
             "direction": "increases fraud risk" if val > 0 else "decreases fraud risk"}
            for name, val in top_reasons
        ]
    }
    
    return explanation


def generate_report(df_test, model, scaler, feature_names, n_samples=100):
    """Generate explainability report on test data."""
    print("Generating SHAP explainability report...")
    
    y_test = df_test['is_fraud']
    X_test = df_test.drop(columns=['is_fraud'])
    
    bool_cols = X_test.select_dtypes(include=['bool']).columns
    X_test[bool_cols] = X_test[bool_cols].astype(int)
    
    # Sample for speed
    sample_idx = X_test.sample(n=min(n_samples, len(X_test)), random_state=42).index
    X_sample = X_test.loc[sample_idx]
    X_scaled = scaler.transform(X_sample)
    
    # SHAP values
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_scaled)
    
    # Feature importance (average absolute SHAP)
    importance = pd.DataFrame({
        'feature': feature_names,
        'importance': np.abs(shap_values).mean(axis=0)
    }).sort_values('importance', ascending=False)
    
    print("\nTop 15 Most Important Features (SHAP):")
    print("=" * 50)
    for _, row in importance.head(15).iterrows():
        bar = "█" * int(row['importance'] * 100)
        print(f"{row['feature']:25s} | {row['importance']:.4f} | {bar}")
    
    # Save importance
    importance.to_csv('data/processed/feature_importance.csv', index=False)
    print("\nFeature importance saved to data/processed/feature_importance.csv")
    
    # Example: explain a fraud transaction
    fraud_indices = df_test[df_test['is_fraud'] == 1].index[:3]
    print("\n\nExample Fraud Explanations:")
    print("=" * 50)
    for idx in fraud_indices:
        row = X_test.loc[idx].values
        explanation = explain_prediction(row, model, scaler, feature_names)
        print(f"\nTransaction (actual: FRAUD)")
        print(f"  Fraud probability: {explanation['fraud_probability']:.1%}")
        print(f"  Risk level: {explanation['risk_level']}")
        print(f"  Action: {explanation['recommended_action']}")
        print(f"  Top reasons:")
        for reason in explanation['top_reasons'][:3]:
            print(f"    - {reason['feature']}: {reason['direction']}")
    
    # Example: explain a legit transaction
    legit_indices = df_test[df_test['is_fraud'] == 0].index[:3]
    print("\n\nExample Legit Explanations:")
    print("=" * 50)
    for idx in legit_indices:
        row = X_test.loc[idx].values
        explanation = explain_prediction(row, model, scaler, feature_names)
        print(f"\nTransaction (actual: LEGIT)")
        print(f"  Fraud probability: {explanation['fraud_probability']:.1%}")
        print(f"  Risk level: {explanation['risk_level']}")
        print(f"  Action: {explanation['recommended_action']}")
    
    return importance


if __name__ == "__main__":
    # Load model and data
    model = joblib.load('models/best_model.pkl')
    scaler = joblib.load('models/scaler.pkl')
    feature_names = joblib.load('models/feature_names.pkl')
    
    df = pd.read_csv('data/processed/fraud_features.csv')
    
    # Use last 20% as test
    test_size = int(len(df) * 0.2)
    df_test = df.tail(test_size)
    
    importance = generate_report(df_test, model, scaler, feature_names)