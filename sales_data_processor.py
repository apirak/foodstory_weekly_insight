import pandas as pd
import json
import argparse
from datetime import datetime, timedelta


def process_sales_data(csv_file_path):
    df = pd.read_csv(csv_file_path)

    df["วันที่เปิดบิล"] = pd.to_datetime(
        df["วันที่เปิดบิล"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
    )

    if df["วันที่เปิดบิล"].isnull().all():
        raise ValueError("ไม่สามารถแปลงคอลัมน์ 'วันที่เปิดบิล' เป็น datetime ได้")

    df["เวลาสั่ง"] = pd.to_datetime(
        df["วันที่เปิดบิล"].dt.date.astype(str) + " " + df["เวลาสั่ง"]
    )

    df["ราคารวม"] = pd.to_numeric(df["ราคารวม"].str.replace(",", ""), errors="coerce")
    df["จำนวน"] = pd.to_numeric(df["จำนวน"].str.replace(",", ""), errors="coerce")

    df["วันในสัปดาห์"] = df["วันที่เปิดบิล"].dt.day_name()

    time_intervals = pd.date_range("00:00", "23:59", freq="30min").time

    result = []

    for interval in time_intervals:
        interval_end = (
            datetime.combine(datetime.today(), interval) + timedelta(minutes=30)
        ).time()
        row = {"time": interval.strftime("%H:%M")}

        for day in df["วันในสัปดาห์"].unique():
            sales = df[
                (df["วันในสัปดาห์"] == day)
                & (df["เวลาสั่ง"].dt.time >= interval)
                & (df["เวลาสั่ง"].dt.time < interval_end)
            ]["ราคารวม"].sum()
            row[day] = round(sales, 2)

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
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        print(f"Data processed successfully. Output saved to {args.output}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
