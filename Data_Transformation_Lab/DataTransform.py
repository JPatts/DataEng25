import csv
import pandas as pd

def decode(row):
    # create datetime value from OPD_DATE
    dt = pd.to_datetime(row['OPD_DATE'], format='%d%b%Y:%H:%M:%S')
    # create timedelta from ACT_TIME
    td = pd.to_timedelta(row['ACT_TIME'], unit='s')
    return dt + td

def read_csv_file():
    # define cols to keep 
    keep_cols = ['EVENT_NO_TRIP','OPD_DATE',
                 'VEHICLE_ID','METERS','ACT_TIME',
                 'GPS_LONGITUDE','GPS_LATITUDE']
    """ 
    EVENT_NO_TRIP   EVENT_NO_STOP   OPD_DATE
    VEHICLE_ID      METERS          ACT_TIME
    GPS_LONGITUDE   GPS_LATITUDE    GPS_SATELLITES  GPS_HDOP 
    """

    CSV = pd.read_csv('bc_trip259172515_230215.csv',usecols=keep_cols)
    df = pd.DataFrame(CSV)
    
    df["TIMESTAMP"] = df.apply(decode, axis=1)

    # calc diff
    df['dMETERS'] = df['METERS'].diff()
    df['dTIME'] = df['TIMESTAMP'].diff().dt.total_seconds()

    # calc SPEED as DMETERS / DTIME
    df['SPEED'] = df.apply(lambda row: row['dMETERS'] / row['dTIME'] if row['dTIME'] and row['dTIME'] != 0 else 0, axis=1)

    df.drop(columns=['OPD_DATE','ACT_TIME'], inplace=True)

    print("Columns:", df.columns)
    print("\nRecords:")
    print(df)
    print("\nTotal  breadcrumbs:", df.shape[0])

    min_speed = df['SPEED'].min()
    max_speed = df['SPEED'].max()
    avg_speed = df['SPEED'].mean().round(2)
    print("\nSpeed stats:")
    print("\nMin speed:", min_speed)
    print("Max speed:", max_speed)
    print("Avg speed:", avg_speed)

def main():
    read_csv_file()

if __name__ == "__main__":
    main()
