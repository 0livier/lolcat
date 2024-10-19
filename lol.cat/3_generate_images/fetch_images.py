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
    output_dir = os.path.join(os.path.dirname(__file__), "..", "public", "lulz")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    
    if os.path.exists(output_path) and not force:
        print(f"Skipping existing image: {output_filename}")
        return

    output = replicate.run(
        "levelsio/lomography:3e4d07d16e49be22c9158b6e4864d54c3fb6f676353d49c26c0646771703ddd5",
        input={
            "model": "dev",
            "prompt": prompt,
            "lora_scale": 1,
            "num_outputs": 1,
            "aspect_ratio": "16:9",
            "output_format": format,
            "guidance_scale": 3.54,
            "output_quality": 80,
            "prompt_strength": 0.8,
            "extra_lora_scale": 1,
            "num_inference_steps": 28,
        },
    )

    urlretrieve(output[0].url, output_path)

# Add this function to parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Generate images from CSV data")
    parser.add_argument("-n", "--num_rows", type=int, help="Number of rows to process")
    parser.add_argument("-f", "--filter_date", type=str, help="Filter rows by date (e.g., 2024)")
    parser.add_argument("--force", action="store_true", help="Force regeneration of existing images")
    return parser.parse_args()

csv_file_path = os.path.join(os.path.dirname(__file__), "input", "themes_and_captions.csv")

# Add this line to parse arguments
args = parse_args()

with open(csv_file_path, 'r') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    rows = list(csv_reader)
    
    # Filter rows based on the date if specified
    if args.filter_date:
        rows = [row for row in rows if args.filter_date in row['Date']]
    
    rows_to_process = rows[:args.num_rows] if args.num_rows else rows
    
    for row in tqdm(rows_to_process, desc="Generating images", unit="image"):
        output_filename = f"{row['Date']}.webp"
        generate_image(row['Image Prompt'], output_filename, force=args.force)
