import csv
import re
from sec_downloader import Downloader
from sec_downloader.types import RequestedFilings
from bs4 import BeautifulSoup

def extract_financial_data_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    financial_data = {
        'Total revenue': None,
        'Cost of revenue': None,
        'Gross profit': None,
        'Research and development': None,
        'Selling and development': None,
        'General and administrative': None,
        'Total operating expenses': None,
        'Operating loss': None
    }

    # Possible table headers to search for
    possible_headers = [
        "Consolidated Statements of Operations Data",
        "Condensed Consolidated Statements of Operations",
        "Consolidated Statements of Income",
        "Condensed Consolidated Statements of Income",
        "Consolidated Statements of Earnings",
        "Condensed Consolidated Statements of Earnings",
        "Consolidated Statements of Operations and Comprehensive Loss Data",
        "Statement of Comprehensive Income",
        "Statement of Operations Data",
        "Consolidated Statements of Operations and Comprehensive Loss",
    ]

    # Locate the table by its specific header
    table = None
    for header in possible_headers:
        header_tag = soup.find('font', string=re.compile(header, re.IGNORECASE))
        if header_tag:
            table = header_tag.find_parent('table')
            break

    if not table:
        return financial_data

    # Helper function to find the value by the tag's text within the table
    def find_value(labels):
        if isinstance(labels, str):
            labels = [labels]
        for label in labels:
            label_tag = table.find(string=re.compile(label, re.IGNORECASE))  # Changed to regex search with re.IGNORECASE
            if label_tag:
                value_tag = label_tag.find_next()
                if value_tag:
                    return value_tag.text.strip()
        return None

    # Extract the values
    financial_data['Total revenue'] = find_value(['Total revenue', 'Revenues', 'Total Revenues', 'Revenue'])
    financial_data['Cost of revenue'] = find_value(['Cost of revenue', 'Cost of revenues'])
    financial_data['Gross profit'] = find_value(['Gross profit', 'Profits'])
    financial_data['Research and development'] = find_value(['Research and development'])
    financial_data['Selling and development'] = find_value(['Selling and development', 'Selling, general and Administrative expenses'])
    financial_data['General and administrative'] = find_value(['General and administrative', 'General & administrative', 'General and administrative expenses'])
    financial_data['Total operating expenses'] = find_value('Total operating expenses')
    financial_data['Operating loss'] = find_value(['Operating loss', 'Operating income (loss)', 'Operating income', 'Net loss'])

    # Extract numeric values and handle conversion
    for key, value in financial_data.items():
        if value is not None:
            # Use regex to find numeric values
            numeric_value = re.findall(r"[-+]?\d*\.\d+|\d+", value.replace(',', ''))
            if numeric_value:
                try:
                    financial_data[key] = float(numeric_value[0])  # Use float for more general case
                except ValueError:
                    financial_data[key] = None
            else:
                financial_data[key] = None

    return financial_data

dl = Downloader("MyCompanyName", "email@example.com")

csv_file_path = "C:/Users/KIIT/Desktop/programs/pythonn/cik.csv" 

cik_numbers = []
with open(csv_file_path, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        cik_numbers.append(row['CIK'])

for cik_number in cik_numbers:
    try:
        metadatas_10k = dl.get_filing_metadatas(RequestedFilings(ticker_or_cik=cik_number, form_type="10-K", limit=9999))
        metadatas_10q = dl.get_filing_metadatas(RequestedFilings(ticker_or_cik=cik_number, form_type="10-Q", limit=9999))

        if metadatas_10k:
            print(f"10-K Filings for CIK {cik_number}:")
            for metadata in metadatas_10k:
                print(metadata.primary_doc_url)
                html = dl.download_filing(url=metadata.primary_doc_url).decode()
                financial_data = extract_financial_data_from_html(html)

                # Print the extracted financial data
                print("Financial Data:")
                print(financial_data)

        if metadatas_10q:
            print(f"10-Q Filings for CIK {cik_number}:")
            for metadata in metadatas_10q:
                print(metadata.primary_doc_url)
                html = dl.download_filing(url=metadata.primary_doc_url).decode()
                financial_data = extract_financial_data_from_html(html)
                print("Financial Data:")
                print(financial_data)

    except Exception as e:
        print(f"Error processing CIK {cik_number}: {e}")
