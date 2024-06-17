import csv
import re
from bs4 import BeautifulSoup
from edgar import Company, set_identity

set_identity("Michael Mccallum mike.mccalum@indigo.com")

def find_value(search_terms, search_scope):
    
    for term in search_terms:
        if term in search_scope:
            return search_scope[search_scope.index(term):].split('\n')[0]
    return None

def extract_financial_data(html_content):
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

    soup = BeautifulSoup(html_content, 'html.parser')
    search_scope = soup.text

    financial_data['Total revenue'] = find_value(['Total revenue', 'Revenues', 'Total Revenues', 'Revenue', 'Sales revenue net'], search_scope)
    financial_data['Cost of revenue'] = find_value(['Cost of revenue', 'Cost of revenues'], search_scope)
    financial_data['Gross profit'] = find_value(['Gross profit', 'Profits'], search_scope)
    financial_data['Research and development'] = find_value(['Research and development', 'Research and development expense'], search_scope)
    financial_data['Selling and development'] = find_value(['Selling and development', 'Selling, general and Administrative expenses', 'Selling and marketing expense'], search_scope)
    financial_data['General and administrative'] = find_value(['General and administrative', 'General & administrative', 'General and administrative expenses'], search_scope)
    financial_data['Total operating expenses'] = find_value(['Total operating expenses', 'Operating expense'], search_scope)
    financial_data['Operating loss'] = find_value(['Operating loss', 'Operating income (loss)', 'Operating income', 'Net loss'], search_scope)

    
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

with open("cik.csv", "r") as f:
    cik_data = [row[0] for row in csv.reader(f)]

for cik in cik_data:
    print(cik)
    
    filings_q = Company(cik).get_filings(form=["10-Q"])
    for filing in filings_q:
        html_content = filing.html()  
        financial_data = extract_financial_data(html_content)
        print({"CIK Number": filing.cik, "Filing Type": filing.form})
        print(financial_data)

    filings_k = Company(cik).get_filings(form=["10-K"])
    for filing in filings_k:
        html_content = filing.html()  
        financial_data = extract_financial_data(html_content)
        print({"CIK Number": filing.cik, "Filing Type": filing.form})
        print(financial_data)
