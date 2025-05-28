import pandas as pd
from bs4 import BeautifulSoup
import warnings
from scipy.stats import binomtest
from scipy.stats import ttest_1samp

warnings.filterwarnings("ignore", category=FutureWarning)   # Getting thousands of warnings saying some feature is going to be deprecated in future versions so I found out I could get rid of them with this line

""" 
Use BeautifulSoup and Pandas to trasnform trimet_stopevents_2022-12-07.html to a DataFrame named stopd_df
The datafram should only contain these columns:
trip_id, vehicle_number, tstamp, location_id, ons, offs
The tstamp column should be a datetime value computed using the arrive_time column in the stop event data
"""

def load_stop_events(file_path):
    with open(file_path, "r") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Extract the table from the HTML using BeautifulSoup
    tables = soup.find_all("table")
    dfs = [pd.read_html(str(tbl), header=0)[0] for tbl in tables]
    stops_df = pd.concat(dfs, ignore_index=True)

    # Select only the required columns
    stops_df = stops_df[['trip_number', 'vehicle_number', 'arrive_time', 'location_id', 'ons', 'offs']]

    # convert time 
    date_str = file_path.rstrip('.html').split('_')[-1]
    base_date = pd.to_datetime(date_str)
    stops_df['arrive_time'] = stops_df['arrive_time'].astype(int)
    stops_df.rename(columns={'arrive_time': 'tstamp'}, inplace=True)
    stops_df['tstamp'] = base_date + pd.to_timedelta(stops_df['tstamp'], unit='s')

    return stops_df

def location_6913(stops_df):
    # print the number of stop events at location 6913
    location_id = 6913
    num_events = stops_df[stops_df['location_id'] == location_id].shape[0]
    print(f"Number of stop events at location {location_id}: {num_events}")

    # print total number of unique busses at location 6913
    unique_vehicles = stops_df[stops_df['location_id'] == location_id]['vehicle_number'].nunique()
    print(f"Number of unique vehicles at location {location_id}: {unique_vehicles}")

    # calculate and print percentage of stops at this location where at least one passenger boarded
    num_boarded = stops_df[(stops_df['location_id'] == location_id) & (stops_df['ons'] >= 1)].shape[0]
    total_stops = stops_df[stops_df['location_id'] == location_id].shape[0]
    percentage_boarded = (num_boarded / total_stops) * 100 if total_stops > 0 else 0
    print(f"Percentage of stop events at location {location_id} with at least one passenger boarding: {percentage_boarded:.2f}%") 

def vehicle_4062(stops_df):
    # Print how many stops made by vehicle 4062
    vehicle_number = 4062
    num_stops = stops_df[stops_df['vehicle_number'] == vehicle_number].shape[0]
    print(f"Number of stop events made by vehicle {vehicle_number}: {num_stops}")

    # in entire dataframe, how many total passengers boarded on vehicle 4062
    total_boarded = stops_df[stops_df['vehicle_number'] == vehicle_number]['ons'].sum()
    print(f"Total passengers boarded on vehicle {vehicle_number}: {total_boarded}")

    # in entire dataframe how many passengers de-boarded from vehicle 4062
    total_offs = stops_df[stops_df['vehicle_number'] == vehicle_number]['offs'].sum()
    print(f"Total passengers de-boarded from vehicle {vehicle_number}: {total_offs}")

    # for what percentage of this vehicles stop events did at least one passenger board
    num_boarded = stops_df[(stops_df['vehicle_number'] == vehicle_number) & (stops_df['ons'] >= 1)].shape[0]
    total_stops = num_stops
    percentage_boarded = (num_boarded / total_stops) * 100 if total_stops > 0 else 0
    print(f"Percentage of stop events made by vehicle {vehicle_number} with at least one passenger boarding: {percentage_boarded:.2f}%")

def step_four(stops_df):
    """
    Count each number of stop events for each bus in systen
    count the number of stop events for which the bus had at least one passenger board 
    determine the percentage of stop events with boardings 
    Use a binomial test to determine p, the probability that the observed proportion of 
    stops-with-boardings might occur given the overall proportion of stops-with-boardings for the entire system (which you calculated in step 2E)   
    """
    # calc overall proportion of stops with boardings
    overall_p = (stops_df['ons'] >= 1).mean()

    # per bus counts
    bus_stats = (
        stops_df
        .groupby('vehicle_number')
        .agg(stop_count = ('ons', 'size'), boarded_count = ('ons', lambda x: (x >= 1).sum()))
        .reset_index()
    )
    bus_stats['pct_boarded'] = 100 * bus_stats['boarded_count'] / bus_stats['stop_count']

    # preform binomial test for each bus
    bus_stats['p_value'] = bus_stats.apply(
        lambda row: binomtest(
            int(row.boarded_count),
            int(row.stop_count),
            overall_p,
            alternative='two-sided'
        ).pvalue,
        axis=1
        )
    
    # print number of stop events for all buses
    print(f"Total number of stop events for all buses: {bus_stats['stop_count'].sum()}")

    # print the number of of stop events for which the bus had at least one passenger board
    print(f"Total number of stop events with at least one passenger boarding: {bus_stats['boarded_count'].sum()}")
    
    # print results
    print("\n\nPer-bus boarding stats (first 10 of {} buses):".format(len(bus_stats)))
    print(bus_stats.head(10).to_string(index=False))
    print(f"\nOverall proportion of stops with boardings: {overall_p:.2%}")

    print("\n\n")
    # list buses with p-value < 0.05 with Veihcle ID Number and p-value
    pvalue_buses = bus_stats[bus_stats['p_value'] < 0.05][['vehicle_number', 'p_value']]
    if not pvalue_buses.empty:
        print("Buses with significant p-values (p < 0.05):")
        print(pvalue_buses.to_string(index=False)) 

def step_five(csv_path="trimet_relpos_2022-12-07.csv"):
    # read from local file trimet_relpos_2022-12-07.csv 
    df = pd.read_csv(csv_path, parse_dates=['TIMESTAMP'])
    relpos_array = df['RELPOS'].values
    global_mean = relpos_array.mean()

    records = []

    for vehicle_number, grp in df.groupby('VEHICLE_NUMBER'):
        vehicle_relpos = grp['RELPOS'].values
        n = len(vehicle_relpos)
        if n < 2:
            continue

        t_stat, p_val = ttest_1samp(vehicle_relpos, popmean=global_mean)

        records.append({
            'vehicle_number': vehicle_number,
            "n_obs": n,
            't_stat': t_stat,
            'p_value': p_val
        })

    res = pd.DataFrame.from_records(records)

    biased = (res[res['p_value'] < 0.05]
              .sort_values(by='p_value')
              .reset_index(drop=True))
    
    # list vehicles ID's with their p-values when p < 0.05
    if not biased.empty:
        print("Vehicles with significant p-values (p < 0.05):")
        print(biased[['vehicle_number', 'p_value']].to_string(index=False))
    else:
        print("No vehicles with significant p-values (p < 0.05) found.")

    
def main():
    file_path = "trimet_stopevents_2022-12-07.html"
    stops_df = load_stop_events(file_path)
    # print total count of stop events in dataframe should be 93912
    print(f"Total count of stop events: {len(stops_df)}")

    # A. print number of vehicles in the dataframe
    num_vehicles = stops_df['vehicle_number'].nunique()
    print(f"Number of unique vehicles: {num_vehicles}")

    # B. print how total amount of unique stop locations in the dataFrame
    num_locations = stops_df['location_id'].nunique()
    print(f"Number of unique stop locations: {num_locations}")

    # C. print the MIN and MAX tstamp in the dataframe
    min_tstamp = stops_df['tstamp'].min()
    max_tstamp = stops_df['tstamp'].max()
    print(f"Minimum timestamp: {min_tstamp}")
    print(f"Maximum timestamp: {max_tstamp}")

    # D. How many stop events in which one passenger boarded. Stop events in which 'ons' is >= 1
    num_boarded = stops_df[stops_df['ons'] >= 1].shape[0]
    print(f"Number of stop events with at least one passenger boarding: {num_boarded}")

    # E. total percentage of stop events in which one passenger boarded
    total_events = len(stops_df)
    percentage_boarded = (num_boarded / total_events) * 100
    print(f"Percentage of stop events with at least one passenger boarding: {percentage_boarded:.2f}%")

    location_6913(stops_df)

    vehicle_4062(stops_df)

    print("\n\n\nStep Four:")
    step_four(stops_df) 

    print("\n\n\nStep Five:")
    step_five()

if __name__ == "__main__":
    main()