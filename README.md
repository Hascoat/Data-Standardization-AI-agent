# Accounting Data Normalization Agent

## Objective

This project aims to **automatically normalize financial tables** extracted from Excel or PDF files, using a local transformation pipeline.  
The system reads raw data, applies a fixed column mapping, cleans values, and exports everything into a standardized format — ready for analytical or accounting use.

---

## Code Architecture

### Main Pipeline (`main.py`)

The pipeline runs through the following steps:

1. **Read source files** (Excel or PDF)

   - via `read_excel()` or `read_pdf()` in `read_and_extract_data.py`

2. **Normalize columns**

   - via `normalize_table()` in `normalize.py`, using column mappings provided by `get_column_mapping()`

3. **Clean values**

   - via `standardize_values()` (regex for amounts, `dateparser` for dates)

4. **Export standardized data**
   - via `export_standardized_data()` in `export.py` (to `.csv` or `.xlsx`)

---

## Modules

### `read_and_extract_data.py`

- `read_excel()`: loads an Excel file into a DataFrame
- `read_pdf()`: extracts tables from PDF files using `pdfplumber`

### `normalize.py`

- `normalize_table()`: maps input columns to a standard schema (`contrat_id`, `montant`, `date_operation`, `description`)
- `standardize_values()`: applies transformations to clean amounts and dates

### `openai_ai_sdk_agent.py`

- Contains `get_column_mapping()` which analyzes incoming column names and maps them using hard-coded conditional rules

---

## Current Limitations

### Limited flexibility for new variables

- The system only supports **four columns**:  
  `contrat_id`, `montant`, `date_operation`, `description`
- Adding new columns requires manually updating the mapping logic and normalization pipeline

## Recommendations & Future Improvements

1. External, dynamic schema

   Define a standard_schema.json file in a config/ folder

   Associate each target variable with a dynamic list of synonyms

   Enable schema updates without touching the code

2. Integrate an LLM for column mapping

   Use GPT or similar models to semantically recognize column names

   More robust for heterogeneous or multilingual data

3. Configuration interface

   Provide a CLI or GUI to edit mappings or add custom columns interactively

### Guardrails for Production

To make the system more reliable:

    Automatic mapping validation → alert if expected columns are missing

    Manual fallback → allow user corrections before export

    Detailed logs → trace all steps for easier debugging

    Consistency checks → e.g., verify montant contains valid numbers and date_operation valid dates

## Output Format

    Export to CSV or Excel via pandas

    Standardized schema:

        contrat_id → string

        montant → float

        date_operation → YYYY-MM-DD

        description → string
