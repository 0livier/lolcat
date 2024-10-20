#!/usr/bin/env python

import csv
import os
import json

# Input CSV file path
csv_file_path = os.path.join(os.path.dirname(__file__), "..", "3_generate_images", "input", "themes_and_captions.csv")

# Output JS file path
js_file_path = os.path.join(os.path.dirname(__file__), "..", "data.js")

# Ensure the output directory exists
os.makedirs(os.path.dirname(js_file_path), exist_ok=True)

# Read CSV and keep only Date, Theme, and Caption columns
data = {}
with open(csv_file_path, 'r') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        data[row["Date"]] = [
            row["Theme"],
            row["Caption"].strip('"')
        ]

# Write the result to a JavaScript file
with open(js_file_path, 'w') as jsfile:
    jsfile.write("const lolcats = ")
    json.dump(data, jsfile, indent=2)
    jsfile.write(";\n\nexport default lolcats;")

print(f"Data has been successfully written to {js_file_path}")
