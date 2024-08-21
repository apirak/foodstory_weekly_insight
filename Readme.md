# Convert Sales Data

poetry run python sales_data_processor_2.py sale_rawdata_21_aug.csv
processed_sales_data.json

# Run web

poetry run python -m http.server 8000
