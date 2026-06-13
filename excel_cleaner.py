"""
Excel / CSV Data Cleaner
========================
A beginner-friendly automation script for freelance projects.
Usage: python excel_cleaner.py --input your_file.csv --output cleaned_file.csv
"""

import pandas as pd
import argparse
import os
import re

def clean_dataframe(df):
    print("🧹 Starting data cleaning...")

    # 1. Remove completely empty rows and columns
    df.dropna(how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)
    print(f"  ✅ Removed empty rows/columns")

    # 2. Strip whitespace from column names
    df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
    print(f"  ✅ Cleaned column names: {list(df.columns)}")

    # 3. Strip whitespace from string cells
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace('nan', '')
    print(f"  ✅ Stripped whitespace from text columns")

    # 4. Remove duplicate rows
    before = len(df)
    df.drop_duplicates(inplace=True)
    after = len(df)
    print(f"  ✅ Removed {before - after} duplicate rows")

    # 5. Clean phone numbers (remove special chars, keep digits)
    phone_cols = [c for c in df.columns if 'phone' in c or 'mobile' in c or 'contact' in c]
    for col in phone_cols:
        df[col] = df[col].apply(lambda x: re.sub(r'[^\d+]', '', str(x)))
    if phone_cols:
        print(f"  ✅ Cleaned phone columns: {phone_cols}")

    # 6. Clean email columns (lowercase)
    email_cols = [c for c in df.columns if 'email' in c or 'mail' in c]
    for col in email_cols:
        df[col] = df[col].str.lower()
    if email_cols:
        print(f"  ✅ Cleaned email columns: {email_cols}")

    # 7. Try to convert numeric columns
    for col in df.columns:
        try:
            converted = pd.to_numeric(df[col], errors='coerce')
            if converted.notna().sum() > len(df) * 0.5:
                df[col] = converted
        except:
            pass
    print(f"  ✅ Auto-detected and converted numeric columns")

    return df


def generate_report(original_df, cleaned_df, output_path):
    report = f"""
==================================================
        EXCEL CLEANER - REPORT
==================================================
Original Rows    : {len(original_df)}
Cleaned Rows     : {len(cleaned_df)}
Duplicates Removed: {len(original_df) - len(cleaned_df)}
Columns          : {list(cleaned_df.columns)}
Output Saved To  : {output_path}
==================================================
"""
    print(report)


def main():
    parser = argparse.ArgumentParser(description='Clean Excel/CSV files automatically')
    parser.add_argument('--input', required=True, help='Input file path (.csv or .xlsx)')
    parser.add_argument('--output', required=True, help='Output file path (.csv or .xlsx)')
    args = parser.parse_args()

    # Load file
    print(f"\n📂 Loading file: {args.input}")
    if args.input.endswith('.xlsx') or args.input.endswith('.xls'):
        original_df = pd.read_excel(args.input)
    else:
        original_df = pd.read_csv(args.input, encoding='utf-8', on_bad_lines='skip')

    df = original_df.copy()

    # Clean
    cleaned_df = clean_dataframe(df)

    # Save
    if args.output.endswith('.xlsx'):
        cleaned_df.to_excel(args.output, index=False)
    else:
        cleaned_df.to_csv(args.output, index=False)

    generate_report(original_df, cleaned_df, args.output)
    print("🎉 Done! File saved successfully.")


if __name__ == "__main__":
    main()
