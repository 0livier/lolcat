import openai
import os
import argparse
import csv
from datetime import datetime, timedelta
from tqdm import tqdm
import requests
import urllib.parse

openai.api_key = os.environ.get("OPENAI_API_KEY")


def generate_themes_for_range(start_date, num_days):
    results = {}
    batch_size = 5
    for batch_start in tqdm(range(0, num_days, batch_size), desc="Processing batches"):
        current_batch_size = min(batch_size, num_days - batch_start)
        date_list = [
            (start_date + timedelta(days=batch_start + i)).strftime("%Y-%m-%d")
            for i in range(current_batch_size)
        ]
        dates_str = "\n".join(date_list)
        tqdm.write(f"Processing dates: {date_list[0]} to {date_list[-1]}")

        prompt = (
            f"For each of the following dates, suggest one real cultural, social, or historical event or theme that is celebrated or recognized globally or in a specific country. "
            f"Prioritize official observances recognized by the UN, UNESCO, or international organizations."
            f"Avoid events that are too obscure or niche. Avoid events that are linked to violence, discrimination, or illegal activities."
            f"Prioritize official observances recognized by the UN, UNESCO, or international organizations."
            f"Prioritize events that are celebrated or recognized in France, Catalonia, or Spain."
            f"Prioritize events that are linked to the LGBTQ+ community or are related to human rights."
            f"Only suggest events that have an existing English Wikipedia page. "
            f"For each date, provide exactly one entry in this format:\n"
            f"YYYY-MM-DD,[event title in English],[event title in Catalan],[URL to English Wikipedia page]\n"
            f"If you are not sure the URL exists, leave it empty.\n"
            f"Do not include any explanation.\n\n"
            f"Dates:\n{dates_str}"
        )

        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=2000,
            temperature=0.5,
        )
        lines = response.choices[0].text.strip().splitlines()
        for line in lines:
            if line.count(",") >= 2:
                date, title, catalan_title, url = line.split(",", 3)
                url = url.strip()
                if url and not is_url_valid(url):
                    url = fallback_google_search_url(title)
                results[date.strip()] = (title.strip(), catalan_title.strip(), url)
    return results


def is_url_valid(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def fallback_google_search_url(query):
    encoded = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?q={encoded}"


# Parse command line arguments
parser = argparse.ArgumentParser(description="Generate themes for dates")
parser.add_argument(
    "--output",
    default="2_generate_prompts/themes_input.csv",
    help="Output CSV file path",
)
parser.add_argument(
    "--start-date",
    type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
    default=datetime.today(),
    help="Start date in YYYY-MM-DD format (default: today)",
)
parser.add_argument(
    "--days",
    type=int,
    default=200,
    help="Number of days to generate (default: 200)",
)
args = parser.parse_args()

start_date = args.start_date
themes = generate_themes_for_range(args.start_date, args.days)

with open(args.output, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["date", "theme", "catalan_theme", "url"])  # Header
    for date, (title, catalan_title, url) in themes.items():
        writer.writerow([date, title, catalan_title, url])
