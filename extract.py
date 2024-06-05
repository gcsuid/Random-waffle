import csv
import random
from edgar import Company, set_identity
from edgar.entities import EntityFiling

with open("ciks.csv", "r") as f:
    data = [x[0] for x in csv.reader(f)]

# Tell the SEC who you are
set_identity("Michael Mccallum mike.mccalum@indigo.com")

gaaps = ["RevenueFromContractWithCustomerExcludingAssessedTax",
"CostOfRevenue",
"GrossProfit",
"ResearchAndDevelopmentExpense",
"SellingAndMarketingExpense",
"GeneralAndAdministrativeExpense",
"OperatingExpenses",
"OperatingIncomeLoss"]

fieldnames = [f"us-gaap_{gaap}" for gaap in gaaps]
def write_to_csv(data: dict):
    with open("output2.csv", "a") as f:
        writer = csv.DictWriter(f, fieldnames=["CIK Number", "Filing Type", "Accession No.", *fieldnames])
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(data)


def extract_data_from_xbrl(filings: list[EntityFiling]):
    for filing in filings:
        if filing.is_xbrl and (xbrl_data := filing.xbrl()):
            print(filing)
            print(xbrl_data.period)
            df = xbrl_data.gaap
            if df is None:
                print("No GAAP data found")
                continue
            
            filing_data = {}
            for gaap, field in zip(gaaps, fieldnames):
                try:
                    value = df[(df['fact'] == gaap) & (df['period'] == xbrl_data.period)].iloc[-1, 1]
                    try:
                        value = int(value) / 1000
                    except ValueError:
                        pass
                    filing_data[field] = value
                except IndexError:
                    print(f"No {gaap} data found")
                    continue

            print({"CIK Number": filing.cik, "Filing Type": filing.form, **filing_data})
            write_to_csv({"CIK Number": filing.cik, "Filing Type": filing.form, "Accession No.": filing.accession_no, **filing_data})


ciks = ["1617798", "1533932", "1378992", "1512673", "1412270", random.choices(data, k=20)]
for cik in ciks:
    print(cik)
    filings = Company(cik).get_filings(form=["10-Q", "10-K"])

    if not filings:
        print("No 10-Q or 10-K filings found")
        continue

    extract_data_from_xbrl(filings) # type: ignore