# Fraud Detection System

I built this project to solve a real problem — financial fraud costs billions every year, and most detection systems are black boxes that flag transactions without explaining why. I wanted to build something that not only catches fraud accurately but also tells you the exact reasons behind every decision.

## What I Built

This is a complete fraud detection pipeline — from raw transaction data to a working API and investigation dashboard. It's not just a model in a notebook. It's a system that can actually be used.

The model analyzes 1.3 million credit card transactions and achieves a 99.88% ROC-AUC score using XGBoost. It catches 93% of fraudulent transactions while keeping false alarms low. Every prediction comes with SHAP-powered explanations showing exactly which factors triggered the fraud alert.

## Screenshots

![Home Page](assets/home.png)
![Dashboard](assets/dashboard.png)
![Transaction Scanner](assets/scanner.png)
![API Documentation](assets/api-docs.png)

## How It Works

I started with raw transaction data containing 23 columns — things like transaction amount, time, merchant location, customer age, and spending category. From there, I engineered 30 features that capture fraud patterns the raw data doesn't show directly. For example:

- **Distance between customer and merchant** — fraudsters often use cards far from the owner's location
- **Time-based features** — fraud spikes at night and during certain hours
- **Amount anomalies** — unusually high amounts or round numbers can signal fraud
- **Category risk scores** — some merchant categories like online shopping and gas stations see more fraud

I trained three models — Logistic Regression, Random Forest, and XGBoost — and compared them properly. XGBoost won with the best balance of catching fraud (93% recall) and not annoying legitimate customers with false alarms (69% precision vs only 7% for Logistic Regression).

The part I'm most proud of is the explainability layer. Using SHAP, every single prediction comes with a breakdown of the top factors that influenced the decision. So instead of just saying "this is fraud," the system says "this is fraud because the amount is unusually high, it happened at 3 AM, and the merchant is far from the customer's usual location." That's what real production systems need — banks and regulators require explanations, not just predictions.

## The System Has Four Components

**1. ML Pipeline** — Data loading, cleaning, feature engineering, model training, and evaluation. Everything runs end-to-end with one command.

**2. FastAPI Endpoint** — A REST API where you POST a transaction and get back the fraud probability, risk level (LOW/MEDIUM/HIGH/CRITICAL), recommended action (APPROVE/REVIEW/BLOCK), and the top reasons for the decision.

**3. Investigation Dashboard** — A Streamlit app with five pages:
- Home page with system overview and architecture
- Analytics dashboard showing fraud patterns by time, category, and amount
- Transaction scanner where you can test any transaction and see the AI explanation
- Threshold optimizer that lets you balance fraud detection vs false alarms with real dollar impact
- Model performance page with ROC curves, confusion matrix, and model comparison

**4. SHAP Explainability** — Every prediction is transparent. The system shows which features increased fraud risk and which decreased it, with visual impact bars.

## What I Found

Some interesting patterns from the analysis:

- Transaction amount is by far the strongest fraud signal — high-value transactions are significantly more likely to be fraudulent
- Nighttime transactions (10 PM to 6 AM) have noticeably higher fraud rates
- Online shopping and gas station categories see the most fraud
- The distance between a customer's location and the merchant matters — farther transactions are riskier
- XGBoost dramatically outperforms simpler models on this kind of imbalanced data (0.58% fraud rate)

## Tech Stack

- **Python** — primary language for the entire pipeline
- **Pandas** — data manipulation and feature engineering
- **Scikit-learn** — preprocessing, train-test split, evaluation metrics
- **XGBoost** — the winning model for fraud classification
- **SHAP** — explainable AI for every prediction
- **FastAPI** — REST API for real-time fraud scoring
- **Streamlit** — investigation dashboard with dark theme
- **Plotly** — interactive visualizations

## Project Structure

- **data/raw/** — original dataset (download from Kaggle, not in repo due to size)
- **data/processed/** — engineered features and model outputs
- **src/data_loader.py** — loads the raw transaction data
- **src/feature_engineering.py** — creates 30 features from 23 raw columns
- **src/model_training.py** — trains and compares 3 models, saves the best one
- **src/explainability.py** — SHAP explanations and feature importance
- **src/api.py** — FastAPI endpoint for real-time predictions
- **src/styles.py** — consistent dark theme styling for the dashboard
- **pages/** — Streamlit dashboard pages (Dashboard, Scanner, Optimizer, Performance)
- **models/** — saved XGBoost model, scaler, and feature names
- **app.py** — main Streamlit entry point
- **DECISIONS.md** — why I made each technical choice

## How to Run

```bash
# Clone the repo
git clone https://github.com/GirirajKudupudi/fraud-detection-system.git
cd fraud-detection-system

# Install dependencies
pip install -r requirements.txt

# Download the dataset from Kaggle and place in data/raw/
# https://www.kaggle.com/datasets/kartik2112/fraud-detection

# Run the full pipeline
python -m src.feature_engineering
python -m src.model_training
python -m src.explainability

# Start the API
python -m src.api
# API docs at http://localhost:8000/docs

# Start the dashboard
streamlit run app.py
```

## Dataset

Credit Card Transactions Fraud Detection Dataset from Kaggle
- 1.3 million transactions across multiple months
- 23 raw features including amount, time, location, merchant, and customer details
- 0.58% fraud rate — realistic class imbalance

Source: https://www.kaggle.com/datasets/kartik2112/fraud-detection

## About Me

I'm Giriraj Kudupudi. I have a Master's in Data Analytics and I'm building production-grade data and AI systems. This project is part of my portfolio demonstrating end-to-end ML engineering — from raw data to deployed APIs with explainable AI.

- [GitHub](https://github.com/GirirajKudupudi)
- [LinkedIn](https://linkedin.com/in/giriraj-kudupudi-6469ba192)