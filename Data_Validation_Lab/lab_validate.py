import csv
import datetime
from collections import Counter
import sys
import numpy as np
import matplotlib.pyplot as plt

# Goal is to validate csv file data 
# this is achieved by deleting rows of data that have a null value as a firstname

def name_validate_csv(input_file, output_file):
    # Check to see if 'name' column exists in entire csv file
    # write to new file to prseverse original data
    with open(input_file, mode='r', newline='') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        # Check if 'firstname' is in the fieldnames
        if 'name' not in fieldnames:
            raise ValueError("The input CSV file does not contain a 'name' column.")
        
        valid_rows = [row for row in reader if row['name']]  # Filter out rows with null 'firstname'
    
    with open(output_file, mode='w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(valid_rows)

def validate_years(input_file, output_file):
    # Assertion: each employee has been employed between 0 and 10 years
    # meaning that the years of employment is between 0 and 10 which remove any rows that is greater than 10 years
    # compare with todays date
    today = datetime.datetime.now().date()
    valid_rows = []

    with open(input_file, mode='r', newline='') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
    
        for row in reader:
            hire_str = row.get('hire_date', '').strip()
            try:
                hire_date = datetime.datetime.strptime(hire_str, '%Y-%m-%d').date()
            except ValueError:
                continue

            years_employed = (today - hire_date).days // 365
            if 0 <= years_employed <= 10:
                valid_rows.append(row)

    with open(output_file, mode='w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(valid_rows)

def verify_birth_hire(input_file, output_file):
    valid_rows = []

    with open(input_file, mode='r', newline='') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
    
        for row in reader:
            hire_str = row.get('hire_date', '').strip()
            try:
                hire_date = datetime.datetime.strptime(hire_str, '%Y-%m-%d').date()
            except ValueError:
                continue

            birth_str = row.get('birth_date', '').strip()
            try:
                birth_date = datetime.datetime.strptime(birth_str, '%Y-%m-%d').date()
            except ValueError:
                continue

            if birth_date < hire_date:
                valid_rows.append(row)
            
    with open(output_file, mode='w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(valid_rows) 

def validate_manager(input_file, output_file):
    valid_rows = []

    with open(input_file, mode='r', newline='') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        rows = list(reader)

        # Create a set of all employee IDs for quick lookup
        all_eids = { row['eid'].strip() for row in rows if row.get('eid') }

        for row in rows:
            manager_id = row.get('reports_to', '').strip()
            if manager_id and manager_id in all_eids:
                valid_rows.append(row)
            
    with open(output_file, mode='w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(valid_rows) 

def validate_city(input_file, output_file):
    # ensure each city has more than one employee
    # check to see if city exists more than once
    with open(input_file, mode='r', newline='') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        rows = list(reader)

    city_counts = Counter(row['city'].strip() for row in rows if row.get('city') and row['city'].strip())

    valid_cities = {city for city, count in city_counts.items() if count > 1}

    valid_rows = [
        row for row in rows 
        if row.get('city', '').strip() in valid_cities
    ]
 
    with open(output_file, mode='w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(valid_rows) 

def salary_his(input_file):
    # Read and parse salaries as integers
    salaries = []
    with open(input_file, mode='r', newline='') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            val = row.get('salary', '').strip()
            try:
                salaries.append(int(val))
            except ValueError:
                continue

    if not salaries:
        print("No valid salaries found.")
        return

    # plot histogram
    plt.figure()       
    plt.hist(salaries, bins=10)
    plt.xlabel('Salary')
    plt.ylabel('Frequency')
    plt.title('Histogram of Employee Salaries')
    plt.show()

def extract_salaries(input_file, output_file):
    salaries = []
    
    with open(input_file, mode='r', newline='') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                salaries.append(row['salary'].strip())
            except KeyError:
                continue
    
    with open(output_file, mode='w', newline='') as outfile:
        outfile.write(', '.join(salaries))

def count_salries(input_file):
    counts = Counter()

    with open(input_file, newline="") as f:
        for row in csv.DictReader(f):
            salary = row.get("salary", "").strip()
            if salary:               # ignore blank / missing cells
                counts[salary] += 1

    if not counts:
        print("No salary data found.")
        return

    for salary in sorted(counts, key=int):   # numeric ascending
        print(f"{salary} = {counts[salary]}")

def main():
    input_file = 'valid_cities_employees.csv'
    output_file = 'salaries.csv'
    
    try:
        # name_validate_csv(input_file, output_file)
        # validate_years(input_file, output_file) 
        # verify_birth_hire(input_file, output_file)
        # validate_manager(input_file, output_file)
        # salary_his(input_file)
        #extract_salaries(input_file, output_file)
        count_salries(input_file)
        # print(f"Validation complete. Valid data written to {output_file}.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()