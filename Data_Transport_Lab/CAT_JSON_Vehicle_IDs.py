import requests
import json

# List of vehicle IDs provided
vehicle_ids = [
    2901, 2914, 2922, 2938, 3009, 3010, 3016, 3018, 3019, 3021, 3023, 3031,
    3032, 3033, 3034, 3038, 3042, 3045, 3102, 3104, 3108, 3112, 3113, 3117,
    3118, 3123, 3124, 3125, 3127, 3130, 3134, 3139, 3140, 3143, 3145, 3153,
    3157, 3160, 3163, 3202, 3203, 3206, 3209, 3210, 3220, 3224, 3225, 3229,
    3233, 3234, 3240, 3241, 3242, 3243, 3245, 3246, 3248, 3249, 3251, 3257,
    3261, 3262, 3264, 3268, 3305, 3314, 3321, 3404, 3409, 3410, 3415, 3416,
    3419, 3501, 3502, 3504, 3505, 3506, 3507, 3509, 3511, 3513, 3514, 3516,
    3519, 3523, 3524, 3533, 3535, 3537, 3542, 3543, 3544, 3545, 3546, 3547,
    3553, 3559, 3566, 3567, 3569, 3572, 3576, 3602, 3606, 3608, 3610, 3620,
    3622, 3625, 3630, 3634, 3640, 3644, 3648, 3702, 3707, 3715, 3716, 3719,
    3721, 3724, 3725, 3727, 3731, 3732, 3734, 3737, 3745, 3747, 3748, 3750,
    3802, 3805, 3907, 3913, 3917, 3918, 3919, 3920, 3921, 3930, 3931, 3932,
    3935, 3936, 3938, 3941, 3942, 3943, 3949, 3957, 3960, 3961, 3964, 4002,
    4004, 4005, 4007, 4012, 4013, 4014, 4017, 4019, 4026, 4031, 4034, 4035,
    4037, 4038, 4039, 4041, 4042, 4049, 4051, 4057, 4058, 4060, 4062, 4064,
    4071, 4201, 4202, 4204, 4207, 4216, 4218, 4227, 4231, 4234, 4235, 4237,
    4302, 4513, 4516, 4519, 4520, 4521, 4531
]

# Define the target date
target_date = "14DEC2022:00:00:00"

# Base URL (the vehicle_id will be appended)
base_url = "https://busdata.cs.pdx.edu/api/getBreadCrumbs?vehicle_id="

# Master list that will hold all data that passes the date check.
master_data = []

# Iterate over the vehicle IDs
for vid in vehicle_ids:
    url = base_url + str(vid)
    print(f"Processing vehicle_id {vid} ...")
    
    try:
        # Perform the download of the JSON file
        response = requests.get(url)
        response.raise_for_status()  # raise an error if the download fails
        
        # Decode the response as JSON
        data = response.json()
    except Exception as e:
        print(f"  Error downloading data for vehicle_id {vid}: {e}")
        continue
    
    # Ensure data is a list. Sometimes the response may be a single dict.
    if not isinstance(data, list):
        data = [data]
    
    # Find all unique OPD_DATE values in the file
    dates = {entry.get("OPD_DATE") for entry in data}
    
    # Check that every entry in the file has the target date
    if len(dates) == 1 and target_date in dates:
        print(f"  Data from vehicle_id {vid} matches the target date. Appending to master data.")
        master_data.extend(data)
    else:
        print(f"  Skipping vehicle_id {vid}: inconsistent dates found: {dates}")

# Write the combined master data to a new JSON file
output_filename = "master.json"
with open(output_filename, "w") as f:
    json.dump(master_data, f, indent=2)

print(f"\nMaster JSON file created with {len(master_data)} records and saved as '{output_filename}'.")
