# pip install imblearn
# #conda install -c conda-forge imbalanced-learn

import subprocess
import sys
import os
import tempfile
import numpy as np
import pandas as pd
import math

# install libraries
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# load the requirements
def install_requirements():
    with open('/opt/ml/processing/input/req/requirements.txt', 'r') as f:
        for line in f.readlines():
            install(line.strip())

if __name__ == "__main__":
    base_dir = "/opt/ml/processing"

    install_requirements()

    # Read Data
    df = pd.read_csv(
        f"{base_dir}/input/payment_1503.csv"
    )

    # Create a new column distance
    df.insert(5, "distance", 0)
    for ind in df.index:
        p1 = [0, 0]
        p2 = [df['coord_x'][ind], df['coord_y'][ind]]
        distance = math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))
        df["distance"][ind] = distance

    # Cleaning and econding
    from sklearn.preprocessing import OrdinalEncoder

    ord_enc = OrdinalEncoder()
    df["terminal_code"] = ord_enc.fit_transform(df[["terminal_name"]])
    df["mcc_code"] = ord_enc.fit_transform(df[["mcc"]])
    df["card_number_code"] = ord_enc.fit_transform(df[["card_number"]])

    df["ts_payment_at"] = pd.to_datetime(df['payment_at'])
    print(df.ts_payment_at.dtype)
    df["hour"] = df.ts_payment_at.dt.hour

    df = df.filter(['fraud',
                    'hour',
                    'terminal_code',
                    'distance',
                    'mcc_code',
                    'amount',
                    'tx_1d',
                    'avg_1d',
                    'tx_7d',
                    'avg_7d',
                    'tx_30d',
                    'avg_30d',
                    'time_btw_cc_tx'], axis=1)

    # Convert to int and reorder columns
    df['fraud'] = df['fraud'].astype(int)

    # Split in Train, Test and Validation Datasets
    train_data, validation_data, test_data = np.split(df.sample(frac=1, random_state=1729), [int(0.7 * len(df)), int(0.9 * len(df))])

    print("train_data: ", train_data.shape)
    print("validation_data: ", validation_data.shape)
    print("test_data: ", test_data.shape)

    tr_value_counts = train_data["fraud"].value_counts()
    print("Fraudulent transactions are %.2f%% of the train_data." % (tr_value_counts[1] * 100 / len(train_data)))
    tst_value_counts = test_data["fraud"].value_counts()
    print("Fraudulent transactions are %.2f%% of the test_data." % (tst_value_counts[1] * 100 / len(test_data)))
    val_value_counts = validation_data["fraud"].value_counts()
    print("Fraudulent transactions are %.2f%% of thevalidation_data." % (tst_value_counts[1] * 100 / len(validation_data)))

    x_train = train_data.iloc[:, train_data.columns != "fraud"]
    y_train = train_data.iloc[:, train_data.columns == "fraud"]
    x_test = test_data.iloc[:, test_data.columns != "fraud"]
    y_test = test_data.iloc[:, test_data.columns == "fraud"]
    x_validation = validation_data.iloc[:, validation_data.columns != "fraud"]
    y_validation = validation_data.iloc[:, validation_data.columns == "fraud"]

    from imblearn.over_sampling import SMOTE
    x_train_smote, y_train_smote = SMOTE(random_state=1234).fit_resample(x_train, y_train)
    smote_value_counts = y_train_smote["fraud"].value_counts()

    print("Fraudulent transactions AFTER SMOTE are %.2f%% of the train_data." % (smote_value_counts[0] * 100 / len(y_train_smote)))

    # Save the Dataframes as csv files
    train_data.to_csv(f"{base_dir}/train/train_data.csv", header=False, index=False)
    x_train.to_csv(f"{base_dir}/train/x_train.csv", header=False, index=False)
    y_train.to_csv(f"{base_dir}/train/y_train.csv", header=False, index=False)
    x_train_smote.to_csv(f"{base_dir}/train/x_train_smote.csv", header=False, index=False)
    y_train_smote.to_csv(f"{base_dir}/train/y_train_smote.csv", header=False, index=False)

    validation_data.to_csv(f"{base_dir}/validation/validation_data.csv", header=False, index=False)
    x_validation.to_csv(f"{base_dir}/validation/x_validation.csv", header=False, index=False)
    y_validation.to_csv(f"{base_dir}/validation/y_validation.csv", header=False, index=False)

    test_data.to_csv(f"{base_dir}/test/test_data.csv", header=False, index=False)
    x_test.to_csv(f"{base_dir}/test/x_test.csv", header=False, index=False)
    y_test.to_csv(f"{base_dir}/test/y_test.csv", header=False, index=False)

    print("## Processing completed. Exiting.")
