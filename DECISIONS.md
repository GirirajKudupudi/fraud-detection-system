# Technical Decisions

This document explains the reasoning behind every major technical choice I made in this project. I'm writing this because I believe the thinking behind a solution matters as much as the solution itself.

## Why This Dataset?

I tested four different fraud detection datasets before settling on this one. Three of them (including a UPI-specific Indian dataset) turned out to be synthetic data with completely random fraud labels — no feature had a correlation above 0.03 with the target variable. No model can learn from random noise.

The Credit Card Transactions dataset from Kaggle has real, learnable patterns. The transaction amount alone has a 0.22 correlation with fraud, and the engineered features push this even higher. I verified the signal quality before investing time in model building — a lesson I learned the hard way after wasting hours on bad data.

## Why These Features?

I created 30 features from 23 raw columns. Here's why the key ones matter:

**is_high_amount** — I used the 95th percentile as the cutoff because fraud transactions tend to cluster in the tail of the amount distribution. This single feature has a 0.25 correlation with fraud.

**is_night** — I defined night as 10 PM to 6 AM based on the EDA showing fraud rates spike during these hours. This is consistent with real-world fraud patterns where stolen card details are used when the owner is less likely to notice.

**distance** — I calculated the Euclidean distance between customer and merchant coordinates. Fraudsters often operate far from the cardholder's location. I used raw distance rather than haversine because at this scale the difference is negligible and it keeps the feature simpler.

**Category one-hot encoding** — I used full one-hot encoding rather than target encoding because with 14 categories and 1.3M rows, there's enough data for each category. Target encoding would risk data leakage if not done carefully with cross-validation folds.

## Why XGBoost Over the Others?

All three models achieved 93% recall (catching the same percentage of fraud). The difference was precision:

- Logistic Regression: 7% precision — for every real fraud it catches, it falsely flags 13 legitimate transactions
- Random Forest: 42% precision — much better, but still noisy
- XGBoost: 69% precision — for every real fraud it catches, it only falsely flags about 0.5 legitimate transactions

In a real banking system, every false alarm means a blocked card and an angry customer calling support. Going from 7% to 69% precision means roughly 10x fewer false alarms. That's the difference between a system that annoys customers and one that actually works in production.

## Why class_weight='balanced' Instead of SMOTE?

I initially planned to use SMOTE (Synthetic Minority Oversampling). However, I ran into a version compatibility issue between imbalanced-learn and scikit-learn on my system. Instead, I used class_weight='balanced' for Logistic Regression and Random Forest, and scale_pos_weight for XGBoost.

This approach has advantages: it doesn't create synthetic samples that might introduce noise, it's simpler to implement and maintain, and it produced excellent results (0.9988 ROC-AUC). In production, simpler solutions that work well are always preferred over complex ones.

## Why SHAP for Explainability?

I chose SHAP over alternatives like LIME or feature importance for three reasons:

1. SHAP values are theoretically grounded in game theory — they provide consistent and fair attribution of each feature's contribution
2. TreeExplainer is specifically optimized for tree-based models like XGBoost, making it fast even on large datasets
3. SHAP gives both global feature importance (which features matter overall) and local explanations (why this specific transaction was flagged)

In regulated industries like banking, model explainability isn't optional — it's required by law in many jurisdictions. Building explainability into the system from day one shows I understand production ML requirements.

## Why FastAPI Over Flask?

FastAPI is faster, generates automatic API documentation (Swagger UI), has built-in request validation through Pydantic, and is the modern standard for Python APIs. Flask would work too, but FastAPI signals to employers that I follow current best practices.

## Why the Threshold Optimizer?

Most fraud detection projects pick a threshold of 0.5 and call it done. In reality, the optimal threshold depends on the business context:

- A bank might prefer a lower threshold (catch more fraud, accept more false alarms) because missed fraud costs thousands per incident
- An e-commerce platform might prefer a higher threshold (fewer false alarms) because blocked legitimate transactions mean lost sales and angry customers

The threshold optimizer lets the user see exactly how changing the threshold affects fraud caught, false alarms, and dollar impact. This kind of business-aware thinking is what separates junior from senior data scientists.

## What I Would Do Differently

If I were building this for a real company, I would:

- Use time-series cross-validation instead of random splits, since fraud patterns evolve over time
- Add real-time feature computation (rolling averages, velocity checks) that capture temporal patterns
- Build a feedback loop where flagged-and-confirmed fraud gets fed back into model retraining
- Add A/B testing infrastructure to compare model versions in production
- Use a proper ML experiment tracking tool like MLflow or Weights & Biases

These aren't in the project because they require production infrastructure, but knowing they're needed is part of the thinking process.