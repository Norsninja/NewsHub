
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
    # Get the current week number
    current_week_number = datetime.now().isocalendar()[1]

    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            cache = pickle.load(f)
    else:
        cache = {}

    # Get today's name (e.g., 'Monday')
    today = datetime.now().strftime('%A')

    # If this week's data doesn't exist in the cache, create it
    if current_week_number not in cache:
        cache[current_week_number] = {}

    # Add today's summaries to this week's data
    cache[current_week_number][today] = summaries

    with open(cache_file, 'wb') as f:
        pickle.dump(cache, f)

# Proposed Monthly Cache
# in summarize weekly cache file