#%%

# main.py
import os
from read_and_extract_data import read_excel, read_pdf
from normalize import normalize_table, standardize_values
from export import export_to_csv

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
excel_path = os.path.join(base_dir, "data", "Transactions_Contrats.xlsx")
pdf_path = os.path.join(base_dir, "data", "BETA_Corp_Accounting_Export.pdf")
pdf_columns = ["Contract Ref", "Description", "Amount", "Date", "Notes"]

def process_excel(path):
    if not os.path.exists(path):
        print("Excel file not found.")
        return
    df = read_excel(path)
    df_norm = normalize_table(df, df.columns.tolist())
    df_std = standardize_values(df_norm)
    print("Excel standardisé :")
    print(df_std.head())
    export_to_csv(df_std, "standardized_excel")

def process_pdf(path):
    if not os.path.exists(path):
        print("PDF file not found.")
        return
    rows = read_pdf(path)
    df_norm = normalize_table(rows, pdf_columns, is_list_data=True)
    df_std = standardize_values(df_norm)
    print("PDF standardisé :")
    print(df_std.head())
    export_to_csv(df_std, "standardized_pdf")

if __name__ == "__main__":
    process_excel(excel_path)
    process_pdf(pdf_path)

# %%
