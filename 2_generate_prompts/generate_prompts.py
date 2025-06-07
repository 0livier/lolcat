#!/usr/bin/env python

import csv
from datetime import datetime
import os
import sys
import openai
from tqdm import tqdm

prompt = """You need to create a prompt to generate a lolcat image with the characteristics below. The image prompt must be linked to the theme: [context].

# Image Prompt (1-2 sentences):
Describe the scene with vivid style. Keep it funny, playful, and cat-centered. The cat must reflect the context with its posture, costume, or environment. Avoid cluttered scenes and too many elements. Prompt should include 'In the style of lomography fisheye with vivid colors'

# Caption in Lolspeak inspired from English:
Write a humorous caption in lolspeak. It must feel like the cat is speaking. It should relate to the theme and the scene. Be clever, use internet meme tone, and keep it concise (max 15 words).

# Caption in Lolspeak inspired from Catalan:
Write a humorous caption in Catalan but with strong lolspeak influence. It must feel like the cat is speaking. It should relate to the theme and the scene. Be clever, use internet meme tone, and keep it concise (max 15 words).

# Emotional Layer:
The image and caption should reflect a human emotion or situation in a funny way: e.g. embarrassment, pride, jealousy, confusion, etc.

# Cultural Reference:
If relevant, include a tasteful pop culture or seasonal reference that makes the scene unique.

# Example (Theme: Halloween):
**Prompt:** Cat tangled in Halloween string lights, wide-angle lomography lens look, startled face, jack-o-lanterns nearby. In the style of lomography fisheye with vivid colors
**Caption:** Halp! I tangled in da spoopiez!
**Catalan Caption:** Ajudaaaa! M'he enredat amb els espantijòs!

Return only:
**Prompt:** ...  
**Caption:** ...
**Catalan Caption:** ...
"""


def update_prompt(theme):
    return prompt.replace("[context]", theme)


def generate_prompt(theme):
    updated_prompt = update_prompt(theme)
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        max_tokens=1000,
        temperature=0.9,
        messages=[
            {
                "role": "system",
                "content": "You are a creative assistant that generates funny and imaginative prompts for lolcat-style images.",
            },
            {"role": "user", "content": updated_prompt},
        ],
    )

    generated_prompt = response.choices[0].message.content.strip()

    # Split the response into its components
    parts = generated_prompt.split("**")
    image_prompt = ""
    caption = ""
    catalan_caption = ""

    for i in range(len(parts)):
        if parts[i].strip() == "Prompt:":
            image_prompt = parts[i + 1].strip()
        elif parts[i].strip() == "Caption:":
            caption = parts[i + 1].strip()
        elif parts[i].strip() == "Catalan Caption:":
            catalan_caption = parts[i + 1].strip()

    # Clean up the text
    image_prompt = image_prompt.replace("\n", " ").strip()
    caption = caption.replace("\n", " ").strip()
    catalan_caption = catalan_caption.replace("\n", " ").strip()

    return image_prompt, caption, catalan_caption


def load_existing_prompts_by_date(file_path):
    existing_prompts = {}
    if os.path.exists(file_path):
        with open(file_path, "r") as csvfile:
            csvreader = csv.reader(csvfile)
            try:
                next(csvreader)  # Skip header
            except StopIteration:
                pass
            for row in csvreader:
                if len(row) >= 4:
                    existing_prompts[row[0]] = (row[1], row[2], row[3])
    return existing_prompts


openai.api_key = os.environ.get("OPENAI_API_KEY")

current_dir = os.path.dirname(os.path.abspath(__file__))
output_file_path = os.path.join(
    current_dir, "..", "3_generate_images", "input", "prompts_and_captions.csv"
)
input_file_path = os.path.join(current_dir, "themes_input.csv")

os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

# Load existing prompts
existing_prompts_by_date = load_existing_prompts_by_date(output_file_path)

# Read all themes from the input file
with open(input_file_path, "r") as csvfile:
    csvreader = csv.reader(csvfile, delimiter=",")
    next(csvreader)  # Skip first line
    all_themes = list(csvreader)
with open(output_file_path, "w") as output_csv:
    csv_writer = csv.writer(output_csv)
    csv_writer.writerow(["Date", "Prompt", "Caption", "CatalanCaption"])

    # Use tqdm to show progress
    for row in tqdm(all_themes, desc="Generating prompts", unit="theme"):
        date = row[0]
        theme = row[1]

        # Check if the prompt for this theme already exists or passed as argument
        if date in existing_prompts_by_date and date not in sys.argv[1:]:
            theme, image_prompt, caption, catalan_caption = existing_prompts_by_date[
                date
            ]
        else:
            # Generate new prompt if it doesn't exist
            image_prompt, caption, catalan_caption = generate_prompt(theme)

        csv_writer.writerow([date, image_prompt, caption, catalan_caption])
        output_csv.flush()  # Flush writes
