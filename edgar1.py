from sec_downloader import Downloader
from sec_downloader.types import RequestedFilings
from bs4 import BeautifulSoup
import requests

# Initialize the downloader
dl = Downloader("MyCompanyName", "email@example.com")

# Define the CIK number
cik_number = "0001631761"

# Retrieve metadata for the latest 10-K and 10-Q filings
metadatas_10k = dl.get_filing_metadatas(RequestedFilings(ticker_or_cik=cik_number, form_type="10-K", ))
metadatas_10q = dl.get_filing_metadatas(RequestedFilings(ticker_or_cik=cik_number, form_type="10-Q", ))

# Function to extract financial information from HTML content
def extract_financial_info(html_content):
    # Parse HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find and extract required financial information
    # Example:
    # sales_revenue = soup.find('span', id='us-gaap_SalesRevenueNet').text
    # cost_of_revenue = soup.find('span', id='us-gaap_CostOfRevenue').text
    # Repeat for other financial data

    # Print or return the extracted financial data
    # Example:
    # print("Sales Revenue:", sales_revenue)
    # print("Cost of Revenue:", cost_of_revenue)

# Download the HTML content for the 10-K filing
if metadatas_10k:
    for metadata in metadatas_10k:
        html_content_10k = dl.download_filing(url=metadata.primary_doc_url).decode()
        print("10-K Filing HTML Content (first 500 chars):", html_content_10k[:500])
        # Extract financial information from 10-K filing
        extract_financial_info(html_content_10k)

# Download the HTML content for the 10-Q filing
if metadatas_10q:
    for metadata in metadatas_10q:
        html_content_10q = dl.download_filing(url=metadata.primary_doc_url).decode()
        print("10-Q Filing HTML Content (first 500 chars):", html_content_10q[:500])
        # Extract financial information from 10-Q filing
        extract_financial_info(html_content_10q)
