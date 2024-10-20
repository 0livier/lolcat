#!/usr/bin/env python

import csv
from datetime import datetime
import os
import sys
from openai import OpenAI
from tqdm import tqdm

prompt = """You need to create a prompt to generate a lolcat image with the characteristics below. That prompt must be in the style of TOK lomography fisheye AND be linked to the theme [context].

# Engaging Cat Image:
A high-quality photo of a cat with an expressive facial expression that reflects the context (e.g., surprise for a birthday, curiosity for a new object).
The cat is in a unique or humorous situation related to the context (e.g., wearing a tiny Santa hat for Christmas).

# Clever Caption in Lolspeak:
A humorous caption written in lolspeak, using intentional misspellings and internet slang.
The caption anthropomorphizes the cat's thoughtsęor words related to the context (e.g., "I can haz pumpkin pie?" for Thanksgiving).
The text directly relates to the image and enhances the overall joke.

# Emotional Connection:
The caption reflects a common human experience or emotion associated with the context.
Includes a surprise element or punchline to make it memorable.

# Visual Presentation:
Maintains the traditional lolcat aesthetic for instant recognition.

# Originality and Creativity:
Incorporates unique ideas or a fresh take on the context.
May include timely cultural references or popular trends relevant to the context.

# Simplicity:
Keeps the prompt concise and straightforward.
Keeps the image in the style of TOK lomography fisheye.
Keeps the without too many entity / different elements.
Keeps the caption concise and straightforward.
Focuses on delivering humor without overcomplicating the message.

-----

Example of response with the theme "Halloween":

**Prompt:** Cat tangled in Halloween decorations, puzzled expression, traditional lolcat style. distant perspective. Very wide shot
**Caption:** Halp! I stuck in da spookiez!
"""


def update_prompt(theme):
    return prompt.replace("[context]", theme)


def generate_prompt(client, theme):
    updated_prompt = update_prompt(theme)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a creative assistant that generates lolcat image prompts.",
            },
            {"role": "user", "content": updated_prompt},
        ],
    )

    generated_prompt = response.choices[0].message.content.strip()
    prompt_parts = generated_prompt.split("**Caption:**")
    if len(prompt_parts) == 2:
        image_prompt = prompt_parts[0].replace("**Prompt:**", "").strip()
        caption = prompt_parts[1].strip()
    else:
        print(f"Error splitting the generated prompt: {generated_prompt}")
        image_prompt = generated_prompt
        caption = ""

    image_prompt = image_prompt.replace("\n", " ").strip()
    caption = caption.replace("\n", " ").strip()

    return image_prompt, caption


def load_existing_prompts_by_date(file_path):
    existing_prompts = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)  # Skip header
            for row in csvreader:
                if len(row) >= 4:
                    existing_prompts[row[0]] = (row[1], row[2], row[3])
    return existing_prompts


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

current_dir = os.path.dirname(os.path.abspath(__file__))
output_file_path = os.path.join(
    current_dir, "..", "3_generate_images", "input", "themes_and_captions.csv"
)
input_file_path = os.path.join(current_dir, "themes.csv")

os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

# Load existing prompts
existing_prompts_by_date = load_existing_prompts_by_date(output_file_path)

# Read all themes from the input file
with open(input_file_path, "r") as csvfile:
    csvreader = csv.reader(csvfile, delimiter="\t")
    all_themes = list(csvreader)

with open(output_file_path, "w") as output_csv:
    csv_writer = csv.writer(output_csv)
    csv_writer.writerow(['Date', 'Theme', 'Image Prompt', 'Caption'])
    
    # Use tqdm to show progress
    for row in tqdm(all_themes, desc="Generating prompts", unit="theme"):
        date = row[0]
        theme = row[1]

        # Check if the prompt for this theme already exists or passed as argument
        if date in existing_prompts_by_date and date not in sys.argv[1:]:
            theme, image_prompt, caption = existing_prompts_by_date[date]
        else:
            # Generate new prompt if it doesn't exist
            image_prompt, caption = generate_prompt(client, theme)

        # Write the result to the output CSV
        csv_writer.writerow([date, theme, image_prompt, caption])
