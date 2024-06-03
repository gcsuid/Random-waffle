import csv
from sec_downloader import Downloader
from sec_downloader.types import RequestedFilings
from bs4 import BeautifulSoup


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

       
        if metadatas_10q:
            print(f"10-Q Filings for CIK {cik_number}:")
            for metadata in metadatas_10q:
                print(metadata.primary_doc_url)

    except Exception as e:
        print(f"Error processing CIK {cik_number}: {e}")
