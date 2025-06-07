#!/usr/bin/env python

import csv
import os
import json
import openai
from tqdm import tqdm
import hashlib

prompts_and_captions = os.path.join(
    os.path.dirname(__file__),
    "..",
    "3_generate_images",
    "input",
    "prompts_and_captions.csv",
)
urls = os.path.join(
    os.path.dirname(__file__), "..", "2_generate_prompts", "themes_input.csv"
)

# Output JS file path
js_file_path = os.path.join(os.path.dirname(__file__), "..", "data.js")

# Cache directory
cache_dir = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(cache_dir, exist_ok=True)


def get_cache_path(text, language="en"):
    """Generate a cache file path based on the input text and language"""
    # Create a hash of the text to use as filename
    text_hash = hashlib.md5(f"{text}_{language}".encode()).hexdigest()
    return os.path.join(cache_dir, f"{text_hash}.txt")


def get_cached_description(text, language="en"):
    """Try to get a cached description, return None if not found"""
    cache_path = get_cache_path(text, language)
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return f.read().strip()
    return None


def cache_description(text, description, language="en"):
    """Cache a description for future use"""
    cache_path = get_cache_path(text, language)
    with open(cache_path, "w") as f:
        f.write(description)


# Ensure the output directory exists
os.makedirs(os.path.dirname(js_file_path), exist_ok=True)

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Read CSV and keep only Date, Theme, and Caption columns
data = {}

# Read URLs and merge with existing data
with open(urls, "r") as csvfile:
    csv_reader = csv.DictReader(csvfile)
    total_rows = sum(1 for row in csv.DictReader(open(urls, "r")))
    csvfile.seek(0)
    next(csv_reader)  # Skip header

    for row in tqdm(csv_reader, total=total_rows, desc="Processing themes"):
        date = row["date"]
        # Add URL as the third element in the array
        data[date] = [row["url"], row["theme"], row["catalan_theme"]]

        # Check cache for English description
        if "description" not in row:
            cached_desc = get_cached_description(row["theme"])
            if cached_desc:
                data[date].append(cached_desc)
            else:
                response = openai.Completion.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt="Describe the following event in one or two sentences: "
                    + row["theme"],
                    max_tokens=1000,
                    temperature=0.5,
                )
                description = response.choices[0].text.strip()
                cache_description(row["theme"], description)
                data[date].append(description)

        # Check cache for Catalan description
        if "catalan_description" not in row:
            cached_desc = get_cached_description(row["theme"], "ca")
            if cached_desc:
                data[date].append(cached_desc)
            else:
                response = openai.Completion.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt="Describe the following event in a one or two sentences in Catalan: "
                    + row["theme"],
                    max_tokens=1000,
                    temperature=0.5,
                )
                description = response.choices[0].text.strip()
                cache_description(row["theme"], description, "ca")
                data[date].append(description)


with open(prompts_and_captions, "r") as csvfile:
    csv_reader = csv.DictReader(csvfile)
    total_rows = sum(1 for row in csv.DictReader(open(prompts_and_captions, "r")))
    csvfile.seek(0)
    next(csv_reader)  # Skip header

    for row in tqdm(csv_reader, total=total_rows, desc="Processing captions"):
        data[row["Date"]].append(row["Caption"])
        data[row["Date"]].append(row["CatalanCaption"])


# Write the result to a JavaScript file
with open(js_file_path, "w") as jsfile:
    jsfile.write("const lolcats = ")
    json.dump(data, jsfile, indent=2)
    jsfile.write(";\n\nexport default lolcats;")

print(f"Data has been successfully written to {js_file_path}")
