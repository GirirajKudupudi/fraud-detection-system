import pandas as pd

def load_data(train_path='data/raw/fraudTrain.csv', test_path='data/raw/fraudTest.csv'):
    """Load the credit card fraud dataset."""
    df_train = pd.read_csv(train_path)
    df_test = pd.read_csv(test_path)
    print(f"Train loaded: {df_train.shape[0]:,} rows")
    print(f"Test loaded: {df_test.shape[0]:,} rows")
    print(f"Train fraud rate: {df_train['is_fraud'].mean()*100:.2f}%")
    return df_train, df_test

if __name__ == "__main__":
    df_train, df_test = load_data()
    print(df_train.head())