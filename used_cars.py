# libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import us
import plotly.express as px


# web scraping
def scrape_table(url, state_col=0, value_col=1, value_name="Value",
                 is_currency=False, is_percent=False, state_map=None, skip_rows=1):
    """
    General-purpose scraper for most tables.
    
    Args:
        url (str): webpage with <table>
        state_col (int): column index for state
        value_col (int): column index for value
        value_name (str): column name for the value
        is_currency (bool): True if values have $ and commas
        is_percent (bool): True if values have %
        state_map (dict): map abbreviations -> full state names
        skip_rows (int): number of header rows to skip
    """
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    data = []
    table = soup.find("table")
    for row in table.find_all("tr")[skip_rows:]:
        cols = row.find_all(["td", "th"])
        if len(cols) > max(state_col, value_col):
            state = cols[state_col].get_text(strip=True)
            value_raw = cols[value_col].get_text(strip=True)

            # handle state abbreviations
            if state_map:
                state = state_map.get(state, state)

            # clean up values
            if is_currency:
                value_raw = value_raw.replace("$", "").replace(",", "")
            if is_percent:
                value_raw = value_raw.replace("%", "").strip()
                value_raw = (float(value_raw))/100
            try:
                value = float(value_raw)
            except ValueError:
                continue

            data.append({"State": state, value_name: value})
    return pd.DataFrame(data)

# sources
urls = {
    "used_car_price": "https://www.iseecars.com/used-car-prices-by-state-study",
    "doc_fee": "https://caredge.com/guides/car-dealer-doc-fee-by-state",
    "registration_fee": "https://www.compare.com/auto-insurance/resources/vehicle-ownership-costs",
    "sales_tax": "https://www.policygenius.com/auto-insurance/auto-tax-rate-by-state/"
}

# for abbreviated states
state_map = {
    "AK": "Alaska", "AL": "Alabama", "AR": "Arkansas", "AZ": "Arizona", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
}

# scrape each dataset
df_prices = scrape_table(urls["used_car_price"], state_col=1, value_col=2,
                         value_name="Used Car Price", is_currency=True, skip_rows=2)

df_docfees = scrape_table(urls["doc_fee"], state_col=0, value_col=1,
                          value_name="Doc Fee", is_currency=True, state_map=state_map)

df_regfees = scrape_table(urls["registration_fee"], state_col=0, value_col=1,
                            value_name="Registration Fee", is_currency=True, skip_rows=1)

df_tax = scrape_table(urls["sales_tax"], state_col=0, value_col=1,
                      value_name="Sales Tax", is_percent=True)

# load car insurance .csv from world policy
df_temp = pd.read_csv('car-insurance-rates-by-state-2025.csv')
# keep only the state and full coverage insurance rate 
# (also rename columns)
df_insurance = df_temp[['state', 'CarInsuranceRates_AvgAnnualFullCoveragePremium']].rename(
    columns={
        'state': 'State',
        'CarInsuranceRates_AvgAnnualFullCoveragePremium': 'Insurance'
    }
)

# merge everything into one DataFrame
df_final = (
    df_prices
    .merge(df_docfees, on="State", how="outer")
    .merge(df_regfees, on="State", how="outer")
    .merge(df_tax, on="State", how="outer")
    .merge(df_insurance, on="State", how="outer")
)

# remove DC from the dataset
df_final = df_final[~df_final['State'].isin(['District of Columbia', 'DC'])]


# add total fees (not including price of used car)
df_final["Total Fees"] = (
    df_final["Doc Fee"] +
    df_final["Registration Fee"] +
    df_final["Insurance"] +
    df_final["Used Car Price"] * df_final["Sales Tax"]
)

# adding fees to get the total cost
df_final["Total Cost"] = df_final['Used Car Price'] + df_final['Total Fees']


# using these metrics to create our weighted ranked columns
metrics = ["Used Car Price", "Sales Tax", "Doc Fee", "Registration Fee", "Insurance"]
for metric in metrics:
    df_final[f"{metric} Rank"] = df_final[metric].rank(method="min")

weights = {
    "Used Car Price Rank": 0.3,
    "Sales Tax Rank": 0.3,
    "Insurance Rank": 0.3,
    "Doc Fee Rank": 0.05,
    "Registration Fee Rank": 0.05 # all weights add up to 1
}

# compute weighted scores
df_final["Weighted Score"] = sum(df_final[metric] * weight for metric, weight in weights.items())
# get overall rank
df_final["Overall Rank"] = df_final["Weighted Score"].rank(method="min")

# reset index
df_final = df_final.sort_values("State").reset_index(drop=True)

# check data
print(df_final.head())
print(df_final.isnull().sum())
print(df_final.info())

# save into a .csv file
df_final.to_csv("used_car_affordability.csv", index=False)
print('"used_car_affordability.csv" was successfully saved.')



# key insights
# top 10 most affordable states
top10 = df_final.sort_values("Overall Rank").head(10)
print("Top 10 States to Buy a Used Car:\n", top10[["State", "Weighted Score", "Overall Rank"]])

# Bottom 5 least affordable states
bottom10 = df_final.sort_values("Overall Rank", ascending=False).head(10)
print("\nBottom 10 States to Buy a Used Car:\n", bottom10[["State", "Weighted Score", "Overall Rank"]])

# find the averages for each metric across all states
print(f'\nAvg Metrics:\n{df_final[['Used Car Price','Doc Fee','Registration Fee','Sales Tax','Insurance', 'Total Fees', 'Total Cost']].mean()}.2f')

# outliers
def find_outliers(df, column):
    """
    Find states that are outliers for a given column using IQR method.
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    
    outliers = df[(df[column] < lower) | (df[column] > upper)]
    return outliers[["State", column]]

# numeric columns we're checking for outliers
numeric_cols = ["Used Car Price", "Doc Fee", "Registration Fee", "Sales Tax", "Insurance", "Total Fees", "Total Cost"]

for col in numeric_cols:
    print(f"\nOutliers for {col}:")
    print(find_outliers(df_final, col))
    print(f"Min {col}: {df_final[col].min()} ({df_final.loc[df_final[col].idxmin(), 'State']})")
    print(f"Max {col}: {df_final[col].max()} ({df_final.loc[df_final[col].idxmax(), 'State']})")

# another copy with abbreviated states
df_abbr = df_final.copy()
df_abbr['State'] = df_abbr['State'].apply(lambda x: us.states.lookup(x).abbr if us.states.lookup(x) else None)

# create color coded map plot
fig = px.choropleth(
    df_abbr,
    locations='State',
    locationmode='USA-states',
    color='Overall Rank',
    color_continuous_scale="Viridis_r",
    scope="usa",
    labels={'Overall Rank':'Weighted Rank'}
)
fig.update_layout(title_text='Overall Weighted Rank by State', title_x=0.5)
# save html
fig.write_html("weighted_score_map.html")
fig.show()

# another map plot for total costs (for comparison)
fig = px.choropleth(
    df_abbr,
    locations='State',
    locationmode='USA-states',
    color='Total Cost',
    color_continuous_scale="Viridis_r",
    scope="usa",
    labels={'Total Cost':'Total Cost ($)'},
    hover_data={'Total Cost': ':.2f'}
)
fig.update_layout(title_text='Estimated Total Cost by State', title_x=0.5)
fig.write_html("total_cost_map.html")
fig.show()
