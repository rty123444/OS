import csv

def transfer():
    with open('thread_info.csv', mode='r', newline='') as file:
        reader = csv.DictReader(file)

        filtered_rows = [row for row in reader if row['RIP'] != 'N/A' and row["State"] != "Unknown"]
        
    with open('filtered_thread_info.csv', mode='w', newline='') as file:
        if filtered_rows:
            writer = csv.DictWriter(file, fieldnames=filtered_rows[0].keys())
            writer.writeheader()
            writer.writerows(filtered_rows)

#transfer()