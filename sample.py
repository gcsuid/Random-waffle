from bs4 import BeautifulSoup

# Path to the local HTML file
html_file_path = "C:/Users/KIIT/Downloads/2011tym.html"

# Function to extract financial data from HTML content
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

    # Helper function to find the value by the tag's text
    def find_value(label):
        label_tag = soup.find(text=label)
        if label_tag:
            value_tag = label_tag.find_next()
            if value_tag:
                return value_tag.text.strip()
        return None

    # Extract the values
    financial_data['Total revenue'] = find_value('Total revenue')
    financial_data['Cost of revenue'] = find_value('Cost of revenue')
    financial_data['Gross profit'] = find_value('Gross profit')
    financial_data['Research and development'] = find_value('Research and development')
    financial_data['Selling and development'] = find_value('Selling and development')
    financial_data['General and administrative'] = find_value('General and administrative')
    financial_data['Total operating expenses'] = find_value('Total operating expenses')
    financial_data['Operating loss'] = find_value('Operating loss')

    return financial_data

# Read the HTML content from the local file with a different encoding
with open(html_file_path, "r", encoding="latin-1") as file:
    html_content = file.read()

# Extract financial data from the HTML content
financial_data = extract_financial_data_from_html(html_content)

# Print the extracted financial data
print("Financial Data:")
print(financial_data)
