#!/usr/bin/env python

import csv
from datetime import datetime
import os
import replicate
from urllib.request import urlretrieve
import re
from tqdm import tqdm
import argparse

def generate_image(prompt, output_filename, format="webp", force=False):
    if os.path.exists(output_path) and not force:
        print(f"Skipping existing image: {output_filename}")
        return

    input={
        "prompt": prompt,
        "aspect_ratio": "16:9",
        "output_format": "webp",
        "output_quality": 80,
        "safety_tolerance": 2,
        "prompt_upsampling": True
    }

    try:
        output = replicate.run(
            "black-forest-labs/flux-1.1-pro",
            input
        )
        urlretrieve(output.url, output_path)
    except Exception as e:
        print(f"Error generating image: {e}")
        print(f"Prompt: {prompt}")
        return

# Add this function to parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Generate images from CSV data")
    parser.add_argument("-n", "--num_rows", type=int, help="Number of rows to process")
    parser.add_argument("-f", "--filter_date", type=str, help="Filter rows by date (e.g., 2024)")
    parser.add_argument("--force", action="store_true", help="Force regeneration of existing images")
    return parser.parse_args()

csv_file_path = os.path.join(os.path.dirname(__file__), "input", "prompts_and_captions.csv")

# Add this line to parse arguments
args = parse_args()

output_dir = os.path.join(os.path.dirname(__file__), "..", "public", "lulz")
os.makedirs(output_dir, exist_ok=True)


with open(csv_file_path, 'r') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    rows = list(csv_reader)
        
    # Filter rows based on the date if specified
    if args.filter_date:
        rows = [row for row in rows if args.filter_date in row['Date']]
    
    rows_to_process = rows[:args.num_rows] if args.num_rows else rows
    
    for row in tqdm(rows_to_process, desc="Generating images", unit="image"):
        output_filename = f"{row['Date']}.webp"
        output_path = os.path.join(output_dir, output_filename)
        generate_image(row['Prompt'], output_filename, force=args.force)
