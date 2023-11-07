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
    """
    Parse the raw data into a list of NewsDocument objects.

    Parameters:
    - raw_data (dict): Dictionary containing the raw data.

    Returns:
    - list: List of NewsDocument objects.
    """
    raw_documents = []
    for week_number, week_data in raw_data.items():
        for day_name, day_news in week_data.items():
            for news in day_news:
                headline = news[0]
                if isinstance(news[4], time.struct_time):  # Checking index 4
                    date_time = time.strftime("%Y-%m-%d %H:%M:%S", news[4])  # Convert time.struct_time to string
                elif isinstance(news[4], str):  # Checking index 4
                    date_time = news[4]  # Use it directly
                else:
                    date_time = 'N/A'  # Placeholder string
                link = news[3]
                summary = news[2]
                metadata = {'headline': headline, 'date_time': date_time, 'link': link, 'summary': summary}
                raw_documents.append((news[2], metadata))
                
    return [NewsDocument(text, metadata) for text, metadata in raw_documents]
