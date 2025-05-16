import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "Virgin Islands, U.S.": "VI",
}

# Invert so Abreviation to State
abbrev_to_us_state = {abbr: state for state, abbr in us_state_to_abbrev.items()}

def main():
    # Read the CSV files
    cases_df = pd.read_csv("covid_confirmed_usafacts.csv")
    deaths_df = pd.read_csv("covid_deaths_usafacts.csv")
    census_df = pd.read_csv("acs2017_county_data.csv")

    # Trim cases_df and deaths_df to only the needed columns: 
    #   County Name, State and 2023-07-23.  
    #   2023-07-23 is the last column in each and provides the final cumulative data available for COVID cases and deaths for each county.
    trim_cases_df = cases_df[['County Name', 'State', '2023-07-23']].copy()
    trim_deaths_df = deaths_df[['County Name', 'State', '2023-07-23']].copy()

    # Trim census_df so that only these columns remain: County, State, TotalPop, IncomePerCap, Poverty, Unemployment
    trim_census_df = census_df[['County', 'State', 'TotalPop', 'IncomePerCap', 'Poverty', 'Unemployment']]
    
    # Show the list of column headers for cases_df, deaths_df and census_df
    print("Cases DataFrame Columns:", trim_cases_df.columns.tolist())
    print()
    print("Deaths DataFrame Columns:", trim_deaths_df.columns.tolist())
    print()
    print("Census DataFrame Columns:", trim_census_df.columns.tolist())

    # remove trailing whitspace from each county name in the cases_df and deaths_df
    trim_cases_df['County Name'] = trim_cases_df['County Name'].str.strip()
    trim_deaths_df['County Name'] = trim_deaths_df['County Name'].str.strip()

    # count how many times "Washington County" appears in the cases_df and deaths_df
    count_cases = trim_cases_df['County Name'].str.contains("Washington County").sum()
    count_deaths = trim_deaths_df['County Name'].str.contains("Washington County").sum()
    print(f"Washington County appears {count_cases} times in cases_df")
    print(f"Washington County appears {count_deaths} times in deaths_df")

    # remove “Statewide Unallocated” County name from the cases_df and deaths_df
    trim_cases_df = trim_cases_df[trim_cases_df['County Name'] != "Statewide Unallocated"]
    trim_deaths_df = trim_deaths_df[trim_deaths_df['County Name'] != "Statewide Unallocated"]

    # count rows in each dataframe after removing “Statewide Unallocated”
    print(f"Number of rows in cases_df after removing 'Statewide Unallocated': {len(trim_cases_df)}")
    print(f"Number of rows in deaths_df after removing 'Statewide Unallocated': {len(trim_deaths_df)}")

    print("\n\n\n")
    print("Step 5, convert Abreviations to full state names")
    print("\n\n\n")

    trim_cases_df['State'] = trim_cases_df['State'].map(abbrev_to_us_state)
    trim_deaths_df['State'] = trim_deaths_df['State'].map(abbrev_to_us_state)

    # print the first few rows of trim_cases_df
    print(trim_cases_df.head())

    # Part 6 - Join data sets with matching keys
    trim_cases_df['key'] = trim_cases_df['County Name'] + ", " + trim_cases_df['State']
    trim_deaths_df['key'] = trim_deaths_df['County Name'] + ", " + trim_deaths_df['State']
    trim_census_df['key'] = trim_census_df['County'] + ", " + trim_census_df['State']

    # Set key as index for each dataframe
    trim_cases_df.set_index('key', inplace=True)
    trim_deaths_df.set_index('key', inplace=True)
    trim_census_df.set_index('key', inplace=True)

    # show frist few rows of census_df
    print(trim_census_df.head())

    # Part 7 - Rename final cumulative count columns
    trim_cases_df.rename(columns={'2023-07-23': 'Cases'}, inplace=True)
    trim_deaths_df.rename(columns={'2023-07-23': 'Deaths'}, inplace=True)

    print("Cases DataFrame Columns:", trim_cases_df.columns.values.tolist())
    print("Deaths DataFrame Columns:", trim_deaths_df.columns.values.tolist())
    
    # Part 8 - Join the dataframes in new dataframe named join_df
    join_df = trim_cases_df.join(trim_deaths_df[['Deaths']])
    join_df = join_df.join(trim_census_df[['TotalPop']])

    join_df['CasesPerCap'] = join_df['Cases'] / join_df['TotalPop']
    join_df['DeathsPerCap'] = join_df['Deaths'] / join_df['TotalPop']

    # count rows in join_df
    print(f"Number of rows in join_df: {len(join_df)}")

    # Part 9 - Construct and Show Correlation Matrix
    corr_df = join_df[['CasesPerCap', 'DeathsPerCap', 'TotalPop']].corr()
    print("Correlation Matrix:")
    print(corr_df)

    # Part 10 - Show the correlation matrix as a heatmap
    sns.heatmap(corr_df, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
    plt.title('Correlation Matrix Heatmap')
    plt.show()


if __name__ == "__main__":
    main()