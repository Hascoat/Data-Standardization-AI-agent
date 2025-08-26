#%%
import pandas as pd
import pdfplumber

def read_excel(file_path):
    """Reads an Excel file and returns a DataFrame."""
    try:
        df = pd.read_excel(file_path)
        print(f"Excel file '{file_path}' loaded with {len(df)} rows.")
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def read_pdf(file_path):
    """Reads a PDF file and returns a list of extracted rows (as lists of strings)."""
    rows = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    rows.extend(table[1:])  
        print(f"PDF file '{file_path}' loaded with {len(rows)} rows.")
        return rows
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None
# %%
