
import os
import pickle
from datetime import datetime, timedelta

def is_cache_valid(filename, max_cache_age):
    if not os.path.exists(filename):
        return False
    file_modified_time = datetime.fromtimestamp(os.path.getmtime(filename))
    return (datetime.now() - file_modified_time) <= timedelta(hours=max_cache_age)

def save_cache(filename, data):
       with open(filename, 'wb') as file:
           pickle.dump(data, file)

def load_cache(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)

def save_to_weekly_cache(summaries, cache_file='cache/modular_weekly_cache.pkl'):
    try:
        # Load the existing cache or create a new one if it doesn't exist
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                weekly_cache = pickle.load(f)
        else:
            weekly_cache = {}

        # Get the current day of the week
        today = datetime.now().strftime('%A')

        # If the list for today has not been populated, add the summaries
        if today not in weekly_cache or not weekly_cache[today]:
            weekly_cache[today] = summaries

            # Save the cache
            with open(cache_file, 'wb') as f:
                pickle.dump(weekly_cache, f)
                
    except Exception as e:
        print(f"Error while saving to weekly cache: {e}")