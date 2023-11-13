from flask import Flask, jsonify, request
import json
from datetime import datetime
from fuzzywuzzy import process
import feedparser

app = Flask(__name__)

# Load the news.json file
with open("news.json", "r", encoding="utf-8") as file:
    news_data = json.load(file)

@app.route('/')
def index():
    return "Welcome to the NewsPlanetAI API!"

def fuzzy_search(query, field, threshold=60):
    """Perform a fuzzy search in the specified field of articles."""
    results = []
    for category in news_data["categories"]:
        for article in category["summaries"]:
            text_to_search = article.get(field, '')
            matches = process.extract(query, [text_to_search], limit=None)
            for match, score in matches:
                if score >= threshold:
                    results.append(article)
                    break  # Break after the first match for each article
    return results

@app.route('/search', methods=['GET'])
def search_articles():
    query = request.args.get('query', '').lower()
    field = request.args.get('field', 'headline')  # default to searching in headline
    threshold = int(request.args.get('threshold', 60))  # default threshold
    matching_articles = fuzzy_search(query, field, threshold)
    return jsonify(matching_articles)
# Endpoint to get news by category
@app.route('/category', methods=['GET'])
def get_news_by_category():
    category = request.args.get('category', '').lower()
    filtered_news = [item for item in news_data['categories'] if item['name'].lower() == category]
    return jsonify(filtered_news)

# Endpoint to get news by timestamp
@app.route('/timestamp', methods=['GET'])
def get_news_by_timestamp():
    date_str = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    results = []
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    for category in news_data["categories"]:
        for article in category["summaries"]:
            # Check if timestamp is not empty and correctly formatted
            if article["timestamp"]:
                try:
                    article_date = datetime.strptime(article["timestamp"].split(" ")[0], "%Y-%m-%d").date()
                    if article_date == target_date:
                        results.append(article)
                except ValueError:
                    # Handle the exception for articles with incorrect date format
                    pass
    return jsonify(results)

@app.route('/top-headlines', methods=['GET'])
def get_top_headlines():
    top_headlines = []
    for category in news_data["categories"]:
        for article in category["summaries"]:
            if article.get('top_headline', False):
                top_headlines.append(article)
    return jsonify(top_headlines)
# Endpoint to get the super summary

def get_latest_soundcloud_track():
    # URL of your SoundCloud RSS feed
    rss_url = "https://feeds.soundcloud.com/users/soundcloud:users:1269122767/sounds.rss"
    
    # Parse the RSS feed
    feed = feedparser.parse(rss_url)

    # Check if the feed entries exist
    if not feed.entries:
        return {"error": "No tracks found."}

    # Get the latest track
    latest_track = feed.entries[0]

    # Extract relevant information about the track
    track_info = {
        "title": latest_track.title,
        "published": latest_track.published,
        "link": latest_track.link
    }

    return track_info

@app.route('/daily-briefing', methods=['GET'])
def get_super_summary():

    # Get the latest SoundCloud track information
    soundcloud_track_info = get_latest_soundcloud_track()
    # Get the super summary from the news data
    super_summary = news_data.get("super_summary", "No summary available.")
    # Check if there was an error fetching the SoundCloud track
    if 'error' in soundcloud_track_info:
        summary_with_soundcloud = {
            "super_summary": super_summary,
            "latest_soundcloud_track_error": soundcloud_track_info['error']
        }
    else:
        # Append the SoundCloud track info to the super summary
        summary_with_soundcloud = {
            "latest_soundcloud_track": soundcloud_track_info,
            "super_summary": super_summary
        }
    return jsonify(summary_with_soundcloud)

if __name__ == "__main__":
    app.run()