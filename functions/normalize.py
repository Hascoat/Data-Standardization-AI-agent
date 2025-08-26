#%%

# normalize.py
import pandas as pd
import dateparser
from openai_ai_sdk_agent import get_column_mapping

def normalize_table(data, column_names, is_list_data=False):
    if is_list_data:
        df_raw = pd.DataFrame(data, columns=column_names)
    else:
        df_raw = data.copy()

    # Appel à l'agent pour le mapping
    mapping_result = get_column_mapping(column_names)
    rename_map = {v: k for k, v in mapping_result.items()}

    df_normalized = df_raw.rename(columns=rename_map)
    valid_cols = [col for col in mapping_result.keys() if col in df_normalized.columns]
    return df_normalized[valid_cols]

def standardize_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "montant" in df.columns:
        df["montant"] = (
            df["montant"]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.replace("€", "", regex=False)
            .str.extract(r"([\d.]+)", expand=False)
            .astype(float)
        )
    if "date_operation" in df.columns:
        df["date_operation"] = df["date_operation"].apply(
            lambda x: dateparser.parse(str(x), languages=["fr", "en"])
        ).dt.date
    if "contrat_id" in df.columns:
        df["contrat_id"] = df["contrat_id"].astype(str).str.strip()
    return df

# %%
