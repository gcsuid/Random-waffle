import csv
import requests
from bs4 import BeautifulSoup
import pathlib
import time

# Define the directory for storing HTML documents.
sec_directory = pathlib.Path.cwd().joinpath('sec_documents')
sec_directory.mkdir(exist_ok=True)

# Read the CIK numbers from the CSV file.
csv_file_path = "C:/Users/KIIT/Desktop/programs/pythonn/cik.csv"
cik_numbers = []
with open(csv_file_path, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        cik_numbers.append(row['CIK'])

# Function to extract financial data from HTML content.
def extract_financial_data(soup):
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

    # Look for relevant tables and rows in the HTML content.
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['th', 'td'])
            if len(cells) > 1:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True).replace('$', '').replace(',', '').replace('(', '-').replace(')', '')
                if key in financial_data:
                    financial_data[key] = value

    return financial_data

# Function to save financial data to a CSV file.
def save_to_csv(cik_number, filing_type, filing_date, financial_data):
    output_file = sec_directory.joinpath(f'{cik_number}_financial_data.csv')
    file_exists = output_file.exists()
    with open(output_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['CIK', 'Filing Type', 'Filing Date', 'Metric', 'Value'])
        for key, value in financial_data.items():
            writer.writerow([cik_number, filing_type, filing_date, key, value])

# Function to fetch and process filings for a given CIK and form type.
def fetch_and_process_filings(cik_number, form_type):
    try:
        base_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik_number}&type={form_type}&dateb=&owner=exclude&count=100"
        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all filings.
        filings_table = soup.find('table', class_='tableFile2')
        if filings_table:
            rows = filings_table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cols = row.find_all('td')
                if len(cols) > 3:
                    filing_date = cols[3].get_text(strip=True)
                    doc_url = "https://www.sec.gov" + cols[1].find('a')['href']
                    
                    # Fetch the document page
                    doc_response = requests.get(doc_url)
                    doc_soup = BeautifulSoup(doc_response.content, 'html.parser')

                    # Find the primary document URL
                    primary_doc_url = None
                    for link in doc_soup.find_all('a'):
                        if '.htm' in link.get('href', ''):
                            primary_doc_url = "https://www.sec.gov" + link['href']
                            break

                    if primary_doc_url:
                        # Fetch the primary document
                        primary_response = requests.get(primary_doc_url)
                        primary_soup = BeautifulSoup(primary_response.content, 'html.parser')
                        financial_data = extract_financial_data(primary_soup)
                        save_to_csv(cik_number, form_type, filing_date, financial_data)

                    # Respect rate limiting
                    time.sleep(1)
    except Exception as e:
        print(f"Error processing CIK {cik_number}: {e}")

# Iterate through the list of CIK numbers and fetch filings.
for cik_number in cik_numbers:
    fetch_and_process_filings(cik_number, "10-K")
    fetch_and_process_filings(cik_number, "10-Q")
