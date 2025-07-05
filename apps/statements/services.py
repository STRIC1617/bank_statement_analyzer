# apps/statements/services.py

import os
import pandas as pd
from apps.statements.extract import extract_data
from apps.analysis import (
    summary,
    classify_trans,
    money,
    redundant_trans,
    calculate_balances,
    cash_inflow,
    cash_outflow
)


def analyze_statement(pdf_path):
    """
    Analyzes a single PDF bank statement and returns structured analysis data.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at path: {pdf_path}")

    print(f"[INFO] Starting statement analysis for {pdf_path}")

    # Step 1: Extract account metadata and bank name
    name, acc_no, bank, ifsc = extract_data(pdf_path)

    # Step 2: Load extracted Excel
    excel_path = pdf_path[:pdf_path.find(".")] + ".xlsx"
    data = pd.read_excel(excel_path)

    # Step 3: Basic info
    total_trans, months = summary(data)
    info = {
        "name": name,
        "account_no": acc_no,
        "bank": bank,
        "ifsc": ifsc,
        "total_transactions": total_trans,
        "statement_duration_months": months
    }

    # Step 4: Transaction classification
    data = classify_trans(data)
    data = money(data)

    processed_path = pdf_path.replace(".pdf", "_processed.xlsx")
    data.to_excel(processed_path, index=False)

    # Step 5: Salary estimation
    salary = redundant_trans(processed_path, months)
    info["estimated_salary"] = salary

    # Step 6: Balance analytics
    balance_data = calculate_balances(data, pdf_path)

    # Step 7: Cash flow analysis
    inflow = cash_inflow(data)
    outflow = cash_outflow(data)

    output_fields_path = pdf_path.replace(".pdf", "_outputs.xlsx")
    with pd.ExcelWriter(output_fields_path) as writer:
        inflow.to_excel(writer, sheet_name="Cash Inflow")
        outflow.to_excel(writer, sheet_name="Cash Outflow")

    # Step 8: Final response
    return {
        "basic_info": info,
        "balances": balance_data,
        "cash_inflow": inflow.to_dict(),
        "cash_outflow": outflow.to_dict(),
        "processed_transactions_path": processed_path,
        "output_fields_path": output_fields_path
    }
