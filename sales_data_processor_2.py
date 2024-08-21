import pandas as pd
import json
import argparse
from datetime import datetime, timedelta
import numpy as np


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def process_sales_data(csv_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Convert 'วันที่เปิดบิล' column to datetime
    df["วันที่เปิดบิล"] = pd.to_datetime(
        df["วันที่เปิดบิล"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
    )

    # Check if the conversion was successful
    if df["วันที่เปิดบิล"].isnull().all():
        raise ValueError("Unable to convert 'วันที่เปิดบิล' column to datetime")

    # Get the date of the most recent entry
    most_recent_date = df["วันที่เปิดบิล"].max()

    # Filter data for the last 7 days
    seven_days_ago = most_recent_date - timedelta(days=7)
    df = df[df["วันที่เปิดบิล"] > seven_days_ago]

    # Convert 'เวลาสั่ง' column to datetime
    df["เวลาสั่ง"] = pd.to_datetime(
        df["วันที่เปิดบิล"].dt.date.astype(str) + " " + df["เวลาสั่ง"]
    )

    # Convert 'ราคารวม' column to numeric
    df["ราคารวม"] = pd.to_numeric(df["ราคารวม"].str.replace(",", ""), errors="coerce")
    df["จำนวน"] = pd.to_numeric(df["จำนวน"].str.replace(",", ""), errors="coerce")

    # Create day of week column
    df["วันในสัปดาห์"] = df["วันที่เปิดบิล"].dt.day_name()

    # Create 30-minute time intervals
    time_intervals = pd.date_range("00:00", "23:59", freq="30min").time

    # Create an empty DataFrame to store results
    result = []

    # Loop through each time interval
    for interval in time_intervals:
        interval_end = (
            datetime.combine(datetime.today(), interval) + timedelta(minutes=30)
        ).time()
        row = {"time": interval.strftime("%H:%M")}

        # Calculate sales for each day of the week
        for day in df["วันในสัปดาห์"].unique():
            sales = df[
                (df["วันในสัปดาห์"] == day)
                & (df["เวลาสั่ง"].dt.time >= interval)
                & (df["เวลาสั่ง"].dt.time < interval_end)
            ]["จำนวน"].sum()
            row[day] = float(round(sales, 2))  # Convert to float for JSON serialization

        result.append(row)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Process sales data from CSV and save as JSON."
    )
    parser.add_argument("input", help="Path to the input CSV file")
    parser.add_argument("output", help="Path to save the output JSON file")
    args = parser.parse_args()

    try:
        processed_data = process_sales_data(args.input)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(
                processed_data, f, ensure_ascii=False, indent=2, default=json_serial
            )
        print(f"Data processed successfully. Output saved to {args.output}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
