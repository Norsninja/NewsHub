import requests
from goose3 import Goose
import configparser
import feedparser

# Load the configuration file
config = configparser.ConfigParser()
config.read('modules/suite_config.ini')

# Access variables
use_tqdm = config.getboolean('General', 'UseTqdm')
truncate_max_tokens = config.getint('General', 'TruncateMaxTokens')

# Initialize Goose
g = Goose()

def scrape_headlines(source, num_articles):
    headlines = []
    # Parse the RSS feed
    feed = feedparser.parse(source)

    for entry in feed.entries[:num_articles]:
        try:
            article_title = entry.title
            article_url = entry.link
            timestamp = entry.updated_parsed
            article = g.extract(url=article_url)

            headlines.append((article_title, article.final_url, timestamp, source))
        except Exception as e:
            print(f"Error while processing article in source {source}: {e}")
            continue
    return headlines

def get_full_text(url):
    try:
        if 'news.google.com' in url:
            # Use allow_redirects=True to follow redirects automatically
            response = requests.get(url, allow_redirects=True)
            response.raise_for_status()  # Raise an exception if the response contains an HTTP error status code
            final_url = response.url
            url = final_url
        elif 'ycombinator.com' in url:  # Add this line to handle Hacker News specific case
            return ""

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        article = g.extract(url=url)  
     
        
        return article.cleaned_text.strip()

    except (requests.RequestException, TypeError, ValueError, Exception) as e:
        print(f"Error fetching the URL: {url} - {e}")
        return ""

def truncate_text(text, max_tokens=truncate_max_tokens):
    tokens = text.split()
    if len(tokens) > max_tokens:
        return " ".join(tokens[:max_tokens])
    else:
        return text
