# scratch/check_csv.py
import pandas as pd
import os

csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data for system', 'electronics_product.csv')
print("CSV path exists:", os.path.exists(csv_path))

try:
    df = pd.read_csv(csv_path, nrows=5)
    print("Columns:")
    print(df.columns.tolist())
    print("\nFirst row:")
    print(df.iloc[0].to_dict())
except Exception as e:
    print("Error reading CSV:", e)
