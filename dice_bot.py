from dotenv import load_dotenv
import os
import time
import csv
load_dotenv()

def create_csv_file():
    current_date = time.strftime("%Y-%m-%d")
    csv_filename = f"job_applications_{current_date}.csv"

    if not os.path.exists(csv_filename):
        with open(csv_filename, mode="w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Job Title", "Company", "Location", "Job URL"])

if __name__=="__main__":
    create_csv_file()