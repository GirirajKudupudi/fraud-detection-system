import pandas as pd
import numpy as np

def engineer_features(df):
    """Create advanced features for fraud detection."""
    df = df.copy()
    print(f"Starting feature engineering: {df.shape}")

    # ---- 1. Time features ----
    df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
    df['hour'] = df['trans_date_trans_time'].dt.hour
    df['day_of_week'] = df['trans_date_trans_time'].dt.dayofweek
    df['month'] = df['trans_date_trans_time'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_night'] = df['hour'].isin([0,1,2,3,4,5,22,23]).astype(int)

    # ---- 2. Amount features ----
    df['amt_log'] = np.log1p(df['amt'])
    df['is_high_amount'] = (df['amt'] > df['amt'].quantile(0.95)).astype(int)
    df['is_round_amount'] = (df['amt'] % 50 == 0).astype(int)

    # ---- 3. Location features ----
    df['distance'] = np.sqrt(
        (df['lat'] - df['merch_lat'])**2 +
        (df['long'] - df['merch_long'])**2
    )
    df['is_far_merchant'] = (df['distance'] > df['distance'].quantile(0.90)).astype(int)

    # ---- 4. Age feature ----
    df['dob'] = pd.to_datetime(df['dob'])
    df['age'] = (df['trans_date_trans_time'] - df['dob']).dt.days // 365

    # ---- 5. Category encoding ----
    cat_dummies = pd.get_dummies(df['category'], prefix='cat')
    df = pd.concat([df, cat_dummies], axis=1)

    # ---- 6. Gender encoding ----
    df['is_male'] = (df['gender'] == 'M').astype(int)

    # ---- 7. City population features ----
    df['city_pop_log'] = np.log1p(df['city_pop'])
    df['is_small_city'] = (df['city_pop'] < df['city_pop'].quantile(0.25)).astype(int)

    # ---- 8. Drop columns not needed ----
    drop_cols = ['Unnamed: 0', 'trans_date_trans_time', 'cc_num', 'merchant',
                 'first', 'last', 'gender', 'street', 'city', 'state',
                 'zip', 'dob', 'trans_num', 'unix_time', 'job',
                 'category', 'lat', 'long', 'merch_lat', 'merch_long']
    df = df.drop(columns=drop_cols, errors='ignore')

    print(f"Feature engineering complete: {df.shape}")
    return df


if __name__ == "__main__":
    df = pd.read_csv('data/raw/fraudTrain.csv')
    df_feat = engineer_features(df)
    df_feat.to_csv('data/processed/fraud_features.csv', index=False)
    print(f"\nCorrelations with fraud:")
    corr = df_feat.corr(numeric_only=True)['is_fraud'].abs().sort_values(ascending=False)
    print(corr.head(15))