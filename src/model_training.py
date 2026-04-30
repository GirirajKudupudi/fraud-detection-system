import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, roc_auc_score,
                             precision_recall_curve, auc)
from xgboost import XGBClassifier
import joblib
import os
import warnings
warnings.filterwarnings('ignore')


def prepare_data(df):
    """Split and scale the data."""
    y = df['is_fraud']
    X = df.drop(columns=['is_fraud'])

    # Convert booleans to int
    bool_cols = X.select_dtypes(include=['bool']).columns
    X[bool_cols] = X[bool_cols].astype(int)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train: {X_train.shape[0]:,} | Test: {X_test.shape[0]:,}")
    print(f"Train fraud: {y_train.sum():,} ({y_train.mean()*100:.2f}%)")

    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, X.columns.tolist()


def train_models(X_train, X_test, y_train, y_test):
    """Train and compare 3 models."""
    results = {}

    # ---- Model 1: Logistic Regression ----
    print("\n" + "=" * 60)
    print("MODEL 1: Logistic Regression")
    print("=" * 60)
    lr = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
    lr.fit(X_train, y_train)
    y_prob_lr = lr.predict_proba(X_test)[:, 1]
    roc_lr = roc_auc_score(y_test, y_prob_lr)
    prec, rec, _ = precision_recall_curve(y_test, y_prob_lr)
    pr_auc_lr = auc(rec, prec)
    print(f"ROC-AUC: {roc_lr:.4f}")
    print(f"PR-AUC:  {pr_auc_lr:.4f}")
    y_pred_lr = (y_prob_lr > 0.5).astype(int)
    print(classification_report(y_test, y_pred_lr, target_names=['Legit', 'Fraud']))
    results['Logistic Regression'] = {'model': lr, 'roc_auc': roc_lr, 'pr_auc': pr_auc_lr}

    # ---- Model 2: Random Forest ----
    print("\n" + "=" * 60)
    print("MODEL 2: Random Forest")
    print("=" * 60)
    rf = RandomForestClassifier(
        n_estimators=200, max_depth=15, min_samples_split=10,
        class_weight='balanced', random_state=42, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    y_prob_rf = rf.predict_proba(X_test)[:, 1]
    roc_rf = roc_auc_score(y_test, y_prob_rf)
    prec, rec, _ = precision_recall_curve(y_test, y_prob_rf)
    pr_auc_rf = auc(rec, prec)
    print(f"ROC-AUC: {roc_rf:.4f}")
    print(f"PR-AUC:  {pr_auc_rf:.4f}")
    y_pred_rf = (y_prob_rf > 0.5).astype(int)
    print(classification_report(y_test, y_pred_rf, target_names=['Legit', 'Fraud']))
    results['Random Forest'] = {'model': rf, 'roc_auc': roc_rf, 'pr_auc': pr_auc_rf}

    # ---- Model 3: XGBoost ----
    print("\n" + "=" * 60)
    print("MODEL 3: XGBoost")
    print("=" * 60)
    fraud_ratio = (y_train == 0).sum() / (y_train == 1).sum()
    xgb = XGBClassifier(
        n_estimators=300, max_depth=8, learning_rate=0.1,
        scale_pos_weight=fraud_ratio, eval_metric='auc',
        random_state=42, use_label_encoder=False, n_jobs=-1
    )
    xgb.fit(X_train, y_train)
    y_prob_xgb = xgb.predict_proba(X_test)[:, 1]
    roc_xgb = roc_auc_score(y_test, y_prob_xgb)
    prec, rec, _ = precision_recall_curve(y_test, y_prob_xgb)
    pr_auc_xgb = auc(rec, prec)
    print(f"ROC-AUC: {roc_xgb:.4f}")
    print(f"PR-AUC:  {pr_auc_xgb:.4f}")
    y_pred_xgb = (y_prob_xgb > 0.5).astype(int)
    print(classification_report(y_test, y_pred_xgb, target_names=['Legit', 'Fraud']))
    results['XGBoost'] = {'model': xgb, 'roc_auc': roc_xgb, 'pr_auc': pr_auc_xgb}

    # ---- Compare ----
    print("\n" + "=" * 60)
    print("FINAL COMPARISON")
    print("=" * 60)
    for name, res in results.items():
        print(f"{name:25s} | ROC-AUC: {res['roc_auc']:.4f} | PR-AUC: {res['pr_auc']:.4f}")

    best_name = max(results, key=lambda x: results[x]['roc_auc'])
    print(f"\nBest model: {best_name}")

    return results, results[best_name]['model'], best_name


def save_model(model, scaler, feature_names, model_name):
    """Save model artifacts."""
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/best_model.pkl')
    joblib.dump(scaler, 'models/scaler.pkl')
    joblib.dump(feature_names, 'models/feature_names.pkl')
    print(f"\nSaved: {model_name} -> models/best_model.pkl")


if __name__ == "__main__":
    print("Loading featured data...")
    df = pd.read_csv('data/processed/fraud_features.csv')
    print(f"Loaded: {len(df):,} rows, {df.shape[1]} features\n")

    X_train, X_test, y_train, y_test, scaler, features = prepare_data(df)
    results, best_model, best_name = train_models(X_train, X_test, y_train, y_test)
    save_model(best_model, scaler, features, best_name)

    print("\n\nTraining complete!")