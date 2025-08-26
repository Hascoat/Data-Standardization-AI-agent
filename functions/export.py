# export.py
import os

def export_to_csv(df, filename, directory="output"):
    os.makedirs(directory, exist_ok=True)
    full_path = os.path.join(directory, f"{filename}.csv")
    df.to_csv(full_path, index=False)
    print(f"✅ File saved: {full_path}")
