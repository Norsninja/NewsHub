import json
import pickle
import time

# Define the path to your pickle file and the desired output JSON file
PICKLE_FILE_PATH = 'cache/test_weekly_cache.pkl'  # Replace with your pickle file path
JSON_FILE_PATH = 'json/test_weekly_cache.json'  # Replace with your desired output path

def load_pickle_file(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    return data

def convert_struct_time_to_string(struct_time):
    """Convert time.struct_time object to a string."""
    return time.strftime('%Y-%m-%d %H:%M:%S', struct_time)

def convert_article(article):
    """Convert each time.struct_time in an article to a string."""
    return tuple(
        convert_struct_time_to_string(item) if isinstance(item, time.struct_time) else item 
        for item in article
    )

def convert_data_structure(data):
    """Recursively convert all time.struct_time objects within the data structure."""
    converted_data = {}
    for week_key, week_data in data.items():
        for day_key, articles in week_data.items():
            converted_articles = [convert_article(article) for article in articles]
            if week_key not in converted_data:
                converted_data[week_key] = {}
            converted_data[week_key][day_key] = converted_articles
    return converted_data

def save_as_json(data, json_file_path):
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def main():
    # Load the pickle file
    pickle_data = load_pickle_file(PICKLE_FILE_PATH)

    # Convert the data structure
    converted_data = convert_data_structure(pickle_data)

    # Save the converted data as JSON
    save_as_json(converted_data, JSON_FILE_PATH)

    print(f"The JSON file has been saved to {JSON_FILE_PATH}")

if __name__ == '__main__':
    main()



