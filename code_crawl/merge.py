import csv

def merge_csv_files(file1, file2, output_file):
    data = {}

    # Read data from the first CSV file
    with open(file1, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            library = row['Library']
            if library not in data:
                data[library] = row
            else:
                # Update Date_First_Used with the earlier date
                if row['Date_First_Used'] < data[library]['Date_First_Used']:
                    data[library]['Date_First_Used'] = row['Date_First_Used']
                
                # Update Total_Files with the highest value
                if int(row['Total_Files']) > int(data[library]['Total_Files']):
                    data[library]['Total_Files'] = row['Total_Files']

    # Read data from the second CSV file
    with open(file2, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            library = row['Library']
            if library not in data:
                data[library] = row
            else:
                # Update Date_First_Used with the earlier date
                if row['Date_First_Used'] < data[library]['Date_First_Used']:
                    data[library]['Date_First_Used'] = row['Date_First_Used']
                
                # Update Total_Files with the highest value
                if int(row['Total_Files']) > int(data[library]['Total_Files']):
                    data[library]['Total_Files'] = row['Total_Files']

    # Write the merged data to the output CSV file
    with open(output_file, 'w', newline='') as csv_file:
        fieldnames = ['Library', 'Date_First_Used', 'Total_Files', 'Category', 'Label']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data.values():
            writer.writerow(row)

# Usage example
file1 = 'libraries.csv'
file2 = 'github.csv'
output_file = 'merged_libraries.csv'
merge_csv_files(file1, file2, output_file)