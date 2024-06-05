import pandas as pd
from edgar import Company, set_identity

# Set your EDGAR identity
set_identity("Your Name your.email@example.com")

# Define the XBRL tags we're interested in
xbrl_tags = [
    "us-gaap_SalesRevenueNet",
    "us-gaap_CostOfRevenue",
    "us-gaap_GrossProfit",
    "us-gaap_ResearchAndDevelopmentExpense",
    "us-gaap_SellingAndMarketingExpense",
    "us-gaap_GeneralAndAdministrativeExpense",
    "us-gaap_OperatingExpenses",
    "us-gaap_OperatingIncomeLoss"
]

# Path to the CSV file containing CIK values
cik_file_path = "C:/Users/KIIT/Desktop/programs/pythonn/cik.csv"

# Read CIK values from the CSV file
cik_list = pd.read_csv(cik_file_path)['CIK'].tolist()

# Prepare a list to hold all the data
all_data = []

# Iterate over each CIK and retrieve the financial data
for cik in cik_list:
    company = Company(cik)
    
    # Get all 10-Q and 10-K filings since the company became public
    filings = company.get_filings(form=["10-Q", "10-K"])
    filings.filter(date="2011-01-01:2021-01-01")
    
    for filing in filings:
        xbrl = XBRL(filing)
        
        # Extract the required financial data
        data = {tag: xbrl.get_fact(tag) for tag in xbrl_tags}
        data['CIK'] = cik
        data['Filing Date'] = filing.filing_date
        data['Form Type'] = filing.form_type
        
        # Add the data to our list
        all_data.append(data)

# Convert the list of data to a DataFrame
df = pd.DataFrame(all_data)

# Print the DataFrame
print(df)
