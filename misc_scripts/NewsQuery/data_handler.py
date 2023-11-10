import pickle
import time

class NewsDocument:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

def load_data(filepath):
    """
    Load data from the given pickle file.

    Parameters:
    - filepath (str): Path to the pickle file.

    Returns:
    - dict: Dictionary containing the raw data.
    """
    with open(filepath, 'rb') as f:
        raw_documents_dict = pickle.load(f)
    return raw_documents_dict

def parse_data(raw_data):
    news_documents = []
    for week_number, week_data in raw_data.items():
        for day_name, day_news in week_data.items():
            for news in day_news:
                # Extract news fields
                headline = news[0]
                category = news[1]
                summary = news[2]
                link = news[3]
                date_time = news[4]
                source = news[5]
                location = news[6]
                coordinates = news[7]

                # Convert date_time to string if it's a struct_time object, else check for None or 'None'
                if isinstance(date_time, time.struct_time):
                    date_time = time.strftime("%Y-%m-%d %H:%M:%S", date_time)
                elif date_time in [None, 'None', 'null']:
                    date_time = 'N/A'

                # Handle coordinates, which should be a list of two floats, or None/null
                if isinstance(coordinates, list) and len(coordinates) == 2:
                    # Ensure that both coordinates are either float/int or None/null
                    coord_str_parts = [str(coord) if coord not in [None, 'null'] else 'N/A' for coord in coordinates]
                    coordinates_str = ", ".join(coord_str_parts)
                else:
                    coordinates_str = 'N/A'

                # Ensure all other metadata fields are strings and handle None/null
                metadata = {
                    'headline': str(headline) if headline not in [None, 'None', 'null'] else 'N/A',
                    'category': str(category) if category not in [None, 'None', 'null'] else 'N/A',
                    'summary': str(summary) if summary not in [None, 'None', 'null'] else 'N/A',
                    'link': str(link) if link not in [None, 'None', 'null'] else 'N/A',
                    'date_time': date_time,
                    'source': str(source) if source not in [None, 'None', 'null'] else 'N/A',
                    'location': str(location) if location not in [None, 'None', 'null'] else 'N/A',
                    'coordinates': coordinates_str
                }

                # Append the news content and metadata as a tuple
                news_documents.append(NewsDocument(summary, metadata))

    return news_documents

