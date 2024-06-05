#can extract for 10k fails for 10q
import csv
import re
import logging
from sec_downloader import Downloader
from sec_downloader.types import RequestedFilings
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        logging.warning("Table not found with the specified headers. Searching entire document for financial data.")

    # Helper function to find the value by the tag's text
    def find_value(labels, scope=None):
        if isinstance(labels, str):
            labels = [labels]
        for label in labels:
            label_tag = (scope or soup).find(string=re.compile(label, re.IGNORECASE))
            if label_tag:
                value_tag = label_tag.find_next()
                if value_tag:
                    return value_tag.text.strip()
        return None

    # Extract the values from the table if found, else search the entire document
    search_scope = table if table else soup

    financial_data['Total revenue'] = find_value(['Total revenue', 'Revenues', 'Total Revenues', 'Revenue', 'Sales revenue net'], search_scope)
    financial_data['Cost of revenue'] = find_value(['Cost of revenue', 'Cost of revenues'], search_scope)
    financial_data['Gross profit'] = find_value(['Gross profit', 'Profits'], search_scope)
    financial_data['Research and development'] = find_value(['Research and development', 'Research and development expense'], search_scope)
    financial_data['Selling and development'] = find_value(['Selling and development', 'Selling, general and Administrative expenses', 'Selling and marketing expense'], search_scope)
    financial_data['General and administrative'] = find_value(['General and administrative', 'General & administrative', 'General and administrative expenses'], search_scope)
    financial_data['Total operating expenses'] = find_value(['Total operating expenses', 'Operating expense'], search_scope)
    financial_data['Operating loss'] = find_value(['Operating loss', 'Operating income (loss)', 'Operating income', 'Net loss'], search_scope)

    # Extract numeric values and handle conversion
    for key, value in financial_data.items():
        if value is not None:
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

all_financial_data = []

for cik_number in cik_numbers:
    try:
        metadatas_10k = dl.get_filing_metadatas(RequestedFilings(ticker_or_cik=cik_number, form_type="10-K", limit=9999))
        metadatas_10q = dl.get_filing_metadatas(RequestedFilings(ticker_or_cik=cik_number, form_type="10-Q", limit=9999))

        if metadatas_10k:
            logging.info(f"10-K Filings for CIK {cik_number}:")
            for metadata in metadatas_10k:
                logging.info(metadata.primary_doc_url)
                html = dl.download_filing(url=metadata.primary_doc_url).decode()
                financial_data = extract_financial_data_from_html(html)
                logging.info("10-K Financial Data:")
                logging.info(financial_data)
                all_financial_data.append(financial_data)

        if metadatas_10q:
            logging.info(f"10-Q Filings for CIK {cik_number}:")
            for metadata in metadatas_10q:
                logging.info(metadata.primary_doc_url)
                html = dl.download_filing(url=metadata.primary_doc_url).decode()
                financial_data = extract_financial_data_from_html(html)
                logging.info("10-Q Financial Data:")
                logging.info(financial_data)
                all_financial_data.append(financial_data)

    except Exception as e:
        logging.error(f"Error processing CIK {cik_number}: {e}")
