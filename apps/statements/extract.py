import os
import re
import time
from datetime import datetime

import cv2
import numpy as np
import pandas as pd
import pdf2image
import pytesseract

from pdf2image import convert_from_path
from PIL import Image

import camelot
import tabula


def read_image(image):
    """
    Input: Image path
    Output: Extracted text from Tesseract OCR
    """

    # Comment line below if running app with Docker
    # pytesseract.pytesseract.tesseract_cmd = TESSERACT_FOLDER + r"/tesseract.exe"
    fulltext = pytesseract.image_to_string(image, lang='eng')
    return fulltext


# Takes a pdf path and return list of images path
def pdf_to_images(pdf_path):
    """
    Input: Pdf path
    Output: 1st Page, converted to image
    """

    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    try:
        images = convert_from_path(pdf_path, 200)
        
        return (np.array(images[0]))
    except Exception as e:
        print(e)
        return ""
    '''
    PageNumber = 0
    saved_images = []
    for image in images:
        PageNumber += 1
        image_path = UPLOAD_FOLDER + pdf_name + "_" + str(PageNumber) + ".jpg"
        #image.save(image_path, "JPEG", quality=10)
        saved_images.append(image_path)

    return saved_images
    '''


def classify_bank(text):
    '''
    Takes OCR text from first page and detects IFSC code, to infer the bank by using it
    '''

    banks = {"YES": "YES BANK", "ALLA": "ALLAHABAD BANK", "HDFC": "HDFC BANK"}
    ifsc = get_ifsc(text)
    bank = ""
    for j in banks.keys():
        if j in ifsc:
            bank = banks[j]
            break
    
    return (ifsc, bank)

#### IFSC #####
def get_ifsc(text):
    
    def replace(text):
        return text.replace('?', '7')
    
    ifsc = text.find('IFSC')
    new_text = text[ifsc : ifsc + 30]
    new_text = replace(new_text)

    code = re.findall(r'[A-Z0-9]{11}', new_text)[0]
    

    return code

def get_acc(text):
    '''
    From the extracted text, searches for the Account Number
    '''
    
    if '-' in list(text):
        text = text.replace('-', '')
    
    index = text.lower().find('account n')
    try:
        text = re.findall(r'[0-9]{9,18}', text[index:])[0]
    except:
        return 0
    return text

def get_name(info):
    '''
    From the array of text, searches for the Account Holder Name
    '''

    title = ["mr.", "shri", "ms.", "mrs."]
    for i in info:
        for j in title:
            if j in i.lower():
                return (i.lower().replace(j, "").upper())
    return (-1)

def month_diff(d1, d2):
    '''
    This funtion returns the difference in months between 2 dates passed
    '''

    return abs(d1.month - d2.month + 12 * (d1.year - d2.year))


def extract_data(pdf_path):
    '''
    Takes PDF path, extracts the 1st page of PDF(converted as image) and checks it for the 
    relevant Account Information

    Further, after identifying the bank, it forwards the PDF to the relevant bank
    function for extracting transactions
    '''
    # Calling funtion for image of the 1st page
    try:
        im = pdf_to_images(pdf_path)
    except Exception as e:
        print(e)
    h, w, _ = im.shape

    # Cropping for the relevant area
    crop = im[1:h // 3, :, :]

    # OCR
    info = read_image(crop)

    # Indentify bank
    ifsc, bank = classify_bank(info)
    # Get account name
    name = get_name(info.split("\n"))
    # Get account number
    acc_no = get_acc(info)

    
    print("[INFO] Information:")
    print(acc_no)
    print("IFSC = ", ifsc)
    print("Bank = ", bank)
    print("Name = ", name)
    

    # MOVING FORWARD TO EXTRACTING TRANSACTIONS
    # Each funtion can individually export the transactions in excel

    #### TODO: Make export commmon to a particular folder

    print("[INFO] Exracting transactions...")
    if bank == "YES BANK":
        yes_bank(pdf_path)
    elif bank == "ALLAHABAD BANK":
        all_bank(pdf_path)
    elif bank == "HDFC BANK":
        hdfc_bank(pdf_path)
    else:
        all_bank(pdf_path)
    print("[INFO] Exported Transactions...")

    return(name, acc_no, bank, ifsc)


def yes_bank(pdf_path):
    '''
    Function for the YES BANK transactions
    '''

    # plots = int(input("Select 1 for Balance Trends \n2 for Credit Trends \n3 for Debit trends"))
    page = 2

    df = tabula.read_pdf(pdf_path, pages="1")[0]

    while True:
        p = tabula.read_pdf(pdf_path, pages=str(page))[1]
        if "Unnamed: 0" in p.columns:
            p = p.drop(["Unnamed: 0"], axis=1)
        # print(p.columns)
        if "Description" in p.columns:
            df = pd.concat([df, p], axis=0)
        else:
            break
        page += 1
    df.index = list(range(0, len(df)))

    for i in df.index:
        if type(df["Transaction\rDate"][i]) == float:
            df["Transaction\rDate"][i] = df["Transaction"][i]
    df["Transaction Date"] = df["Transaction\rDate"]
    df = df.drop(["Transaction", "Transaction\rDate"], axis=1)

    delete = []
    headers = ["Date", "Description", "Credit", "Debit", "Balance"]

    for i in df.index:
        row = df.iloc[i, :].tolist()
        nan_c = 0
        # For checking empty rows
        for j in row:
            try:
                if np.isnan(j):
                    nan_c += 1
            except:
                continue
        if nan_c == len(df.columns):
            delete.append(i)

        # For checking headers in between
        for j in headers:
            if j in row:
                delete.append(i)
    df = df.drop(delete, axis=0)

    # For merging multiple lines in one
    last = 0
    delete = []
    for i in df.index:
        if type(df["Value Date"][i]) == float and type(df["Description"][i]) == str:
            buff = df["Description"][last] + df["Description"][i]
            df["Description"][last] = buff
            delete.append(i)
        else:
            last = i
    df = df.drop(delete, axis=0)

    df["Credit"] = df.Credit.apply(lambda x: str(x).replace(",", ""))
    df["Debit"] = df.Debit.apply(lambda x: x.replace(",", ""))

    df["Credit"] = df["Credit"].astype("float64")
    df["Debit"] = df["Debit"].astype("float64")
    df["Value Date"] = df["Value Date"].apply(lambda x: x[3:])

    ###Exporting to excel format
    df = df[["Transaction Date", "Value Date", "Description", "Debit", "Credit", "Balance"]]
    #print(df.head())
    df.to_excel(pdf_path[:pdf_path.find(".")] + ".xlsx", index=False)


def all_bank(pdf_path):
    '''
    Function for ALLAHABAD BANK transactions
    '''

    d = camelot.read_pdf(pdf_path, pages="all")

    df = pd.DataFrame(columns=d[0].df.columns)

    for i in range(len(d)):
        df = pd.concat([df, d[i].df], axis=0)
    df.shape
    df.columns = df.iloc[0, :]
    df = df.drop([0], axis=0)
    df = df.reset_index()
    df = df.drop(["index"], axis=1)
    df.columns = ['Transaction Date', 'Value Date', 'Description', 'Debit', 'Credit', 'Balance']

    for i in df.index:
        try:
            l = df["Value Date"][i].split()
            df["Transaction Date"][i] = l[0]
            df["Value Date"][i] = l[1]
            p = " ".join(l[2:]) + df["Description"][i]
            df["Description"][i] = p
        except:
            continue
    df = df.drop(len(df) - 1)
    df["Balance"] = df["Balance"].apply(lambda x: float(x.lower().replace(" cr", "").replace(" dr", "").strip()))
    # print(df.head())
    df.to_excel(pdf_path[:pdf_path.find(".")] + ".xlsx", index=False)

def extract_month_year(date_str):
    for fmt in ("%d/%m/%y", "%m/%d/%y", "%d-%m-%y", "%m-%d-%y"):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return f"{dt.month:02}/{dt.year:04}"  # returns '04/24' format
        except ValueError:
            continue
    return None

def convert_short_year_to_full(date_str, year_cutoff=30):
    """
    Converts a DD/MM/YY date string to DD/MM/YYYY
    Assumes 2-digit years < 30 belong to 2000s, others to 1900s (adjustable)
    """
    day, month, year = date_str.split('/')
    
    year_int = int(year)
    if year_int <= year_cutoff:
        full_year = f"20{year}"
    else:
        full_year = f"19{year}"

    return f"{day}/{month}/{full_year}"

def parse_hdfc_transactions_with_continuation(lines):
    print("[INFO] Parsing HDFC transactions with line continuation support...")

    transactions = []
    prev_balance = None

    for i, line in enumerate(lines):
        line = line.strip()
        if not line or "Page No." in line or "Contents of this statement" in line:
            continue  # Skip empty/footer lines

        parts = [p.strip() for p in line.split('|')]


        # Try to extract standard fields
        try:
            if len(parts) >= 3:
                print(parts)
                # Format: Date | Description | ValueDate Debit Balance
                combined = parts[2].split()
                value_date_str = combined[0]
                value_date = extract_month_year(value_date_str)
                debit_str = combined[1].replace(',', '') if len(combined) > 1 else ""
                balance_str = combined[-1].replace(',', '') if len(combined) > 2 else ""

                trans_date = convert_short_year_to_full(value_date_str,30)
                description = parts[1]

                # Use Debit from PDF if available; otherwise infer later
                debit = float(debit_str) if debit_str else None
                credit = None
                balance = float(balance_str) if balance_str else None

            elif len(parts) >= 6:
                # Standard format: Date | Value Date | Description | Debit | Credit | Balance
                trans_date = parts[0]
                value_date = parts[1]
                description = parts[2]
                debit_str = parts[3].replace(',', '')
                credit_str = parts[4].replace(',', '')
                balance_str = parts[5].replace(',', '')

                debit = float(debit_str) if debit_str else None
                credit = float(credit_str) if credit_str else None
                balance = float(balance_str) if balance_str else None

            else:
                # Unknown format — skip or log
                # print(f"[WARNING] Skipping line {i} due to unexpected format: {line}")
                continue

            # Infer Debit/Credit based on balance change
            inferred_debit = None
            inferred_credit = None

            if prev_balance is not None and balance is not None:
                diff = balance - prev_balance
                if diff < 0:
                    inferred_debit = abs(diff)
                    inferred_credit = None
                elif diff > 0:
                    inferred_credit = diff
                    inferred_debit = None
                else:
                    inferred_debit = None
                    inferred_credit = None

            # Use original values if they exist; otherwise use inferred ones
        
            final_debit = inferred_debit
            final_credit = inferred_credit

            # Ensure only one of Debit or Credit is set
            if final_debit is not None and final_credit is not None:
                # If both exist, prefer inferred one based on balance
                if prev_balance is not None and balance is not None:
                    diff = balance - prev_balance
                    if diff < 0:
                        final_credit = None
                    elif diff > 0:
                        final_debit = None
                    else:
                        final_debit = final_credit = None

            transactions.append({
                "Transaction Date": trans_date,
                "Value Date": value_date if 'value_date' in locals() else "",
                "Description": description,
                "Debit": final_debit,
                "Credit": final_credit,
                "Balance": balance
            })

            prev_balance = balance

        except Exception as e:
            print(f"[WARNING] Error parsing line {i}: {e}")
            continue

    df = pd.DataFrame(transactions)

    # Ensure all expected columns exist
    expected_columns = ["Transaction Date", "Value Date", "Description", "Debit", "Credit", "Balance"]
    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    # Optional: Filter valid dates
    if not df.empty and 'Transaction Date' in df.columns:
        df = df[df['Transaction Date'].str.contains(r'\d{2}/\d{2}/\d{2}', regex=True, na=True)]

    return df


def hdfc_bank(pdf_path):
    print("[INFO] Extracting HDFC Bank statement using OCR...")
    
    # Step 1: Convert PDF to images and extract text
    images = pdf2image.convert_from_path(pdf_path, dpi=200)
    full_text = []

    for i, image in enumerate(images):
        print(f"[INFO] Extracting text from page {i+1}")
        page_text = pytesseract.image_to_string(image).strip()
        full_text.extend(page_text.split('\n'))

    # Step 2: Parse extracted lines
    df = parse_hdfc_transactions_with_continuation(full_text)

    # Step 4: Clean up column names
    df.rename(columns={
        'Date': 'Transaction Date',
        'Value Dt': 'Value Date',
        'Withdrawal Amt.': 'Debit',
        'Deposit Amt.': 'Credit',
        'Closing Balance': 'Balance'
    }, inplace=True)

    # Step 5: Merge Chq./Ref.No. + Narration into Description
    if 'Chq./Ref.No.' in df.columns and 'Narration' in df.columns:
        df['Description'] = df['Chq./Ref.No.'].astype(str) + ' :- ' + df['Narration'].astype(str)
        df.drop(columns=['Chq./Ref.No.', 'Narration'], inplace=True)


    desired_cols = ['Transaction Date', 'Value Date', 'Description', 'Debit', 'Credit', 'Balance']
    df = df[[col for col in desired_cols if col in df.columns]]
    # Step 11: Save cleaned data to Excel
    output_excel_path = pdf_path[:pdf_path.find(".")] + ".xlsx"
    df.to_excel(output_excel_path, index=False)
    print(f"[INFO] Cleaned data saved to {output_excel_path}")


    return df



