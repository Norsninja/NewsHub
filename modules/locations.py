import os
import pickle
from datetime import datetime
import openai
import time
import json
from tqdm import tqdm

# Import the configuration loader
from configparser import ConfigParser

config = ConfigParser()
config.read('modules/suite_config.ini')

CACHE_FILE = config['Cache']['LocCacheFile']

# OpenAI API key
openai_api_key = config['OPENAI']['OPENAI_API_KEY']

def extract_locations(summaries):
        # Attempt to load cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'rb') as f:
            cache_time, locations = pickle.load(f)
        
        # If the cache is less than an hour old - return the cached data
        if (datetime.now() - cache_time).total_seconds() < 3600:
            return locations
    locations = []
    for summary in tqdm(summaries, desc="Extracting locations"):
        title, category, text, link, timestamp, source = summary
        for _ in range(3):  # Try the API call up to 3 times
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a deterministic AI specializing in Named Entity Recognition, employed by a NewsPlanetAI, a reputable news source. You have been given the task of reading news articles and identifying one location that the news article is most likely about. Your response will be used to geocode the locations of the articles on a map. Give one location ONLY in English, in this format \"City, Country\". If the article does not provide a location, respond \"None\"."
                        },
                        {
                            "role": "user",
                            "content": f"Please give one location for this article per the instructions,  \"{text}\""
                        },
                    ],
                    temperature=0,
                    max_tokens=80,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                # If the API call succeeds, exit the loop
                print(response)
                location = response['choices'][0]['message']['content'].strip()  # remove leading/trailing spaces

                if location.lower() == "none":  # Log if None location
                    print(f"Headline: {title} - Location: {location} (none)")
    
                locations.append(location)

                break
            except openai.error.APIError as e:
                print(f"OpenAI API returned an API Error: {e}. Retrying...")
                time.sleep(2)  # Wait for 2 seconds before retrying
            except openai.error.APIConnectionError as e:
                print(f"Failed to connect to OpenAI API: {e}. Retrying...")
                time.sleep(2)
            except openai.error.RateLimitError as e:
                print(f"OpenAI API request exceeded rate limit: {e}. Retrying after a longer delay...")
                time.sleep(10)  # Wait longer if rate limit has been exceeded
            except openai.error.ServiceUnavailableError as e:
                print(f"OpenAI API service unavailable: {e}. Retrying...")
                time.sleep(10)  # Wait for 10 seconds before retrying
        else:
            # If the API call failed 3 times, add a None location and continue with the next summary
            print("Failed to get location for a summary after 3 attempts. Skipping...")
            locations.append(None)
            continue

    cache_data = (datetime.now(), locations)

    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(cache_data, f)

    return locations


def append_locations_to_news_json(summaries, locations):
    # Open the existing news.json file
    with open('news.json', 'r', encoding='utf-8') as f:
        news = json.load(f)

    # Iterate over the categories in the news
    for category in news['categories']:
        # Iterate over the summaries in each category
        for news_summary in category['summaries']:
            # Find the index of the summary in summaries that matches the news_summary
            indices = [i for i, summary in enumerate(summaries) if summary[0] == news_summary['headline']]
            if indices:
                index = indices[0]
                # Add the location to the news summary
                news_summary['location'] = locations[index]

    # Save the updated news data back to the news.json file
    with open('news.json', 'w') as f:
        json.dump(news, f, indent=4)
