import os
import configparser
from datetime import datetime
from flask import Flask, render_template
import time
import json

# Load the configuration file
config = configparser.ConfigParser()
config.read('modules/suite_config.ini')

# Access variables
openai_api_key = config['OPENAI']['OPENAI_API_KEY']
ftp_host = config['FTP']['Host']
ftp_user = config['FTP']['User']
ftp_password = config['FTP']['Password']
ftp_directory = config['FTP']['Directory']

cache_directory = config['Cache']['Directory']
max_cache_age_hours = int(config['Cache']['MaxAgeHours'])
weekly_cache_file = config['Cache']['WeeklyCacheFile']


max_summary_length = int(config['Summaries']['MaxSummaryLength'])
max_cache_age_hours = int(config['Summaries']['MaxCacheAgeHours'])

categories = config['Headlines']['Categories'].split(', ')

use_tqdm = config.getboolean('General', 'UseTqdm')

model_categorize_headlines = config['Models']['CategorizeHeadlines']
model_summarize_super_summary = config['Models']['SummarizeSuperSummary']

retries_summarize_articles = config.getint('Retry', 'SummarizeArticlesRetries')
wait_time_seconds_summarize_articles = config.getint('Retry', 'SummarizeArticlesWaitTimeSeconds')
retries_summarize_super_summary = config.getint('Retry', 'SummarizeSuperSummaryRetries')
wait_time_seconds_summarize_super_summary = config.getint('Retry', 'SummarizeSuperSummaryWaitTimeSeconds')
# List of news sources
sources = [
    ("https://news.google.com/rss/search?q=when:24h+allinurl:apnews.com", 3),
    ("http://feeds.bbci.co.uk/news/rss.xml", 3),
    ("https://rss.jpost.com/rss/rssfeedsfrontpage.aspx", 2),
    ("https://www.aljazeera.com/xml/rss/all.xml", 3),
    ("https://www.scmp.com/rss/4/feed", 2),
    ("https://rss.dw.com/rdf/rss-en-all", 3),
    ("https://timesofindia.indiatimes.com/rssfeedstopstories.cms", 2),
    ("https://www.arabnews.com/rss.xml", 2),
    ("https://mg.co.za/feed/", 2),
    ("https://batimes.com.ar/feed", 1),
    ("https://soranews24.com/feed/", 3),
    ("https://www.japantimes.co.jp/feed", 3),
    ("https://www.riotimesonline.com/feed/", 3),
    ("http://feeds.bbci.co.uk/news/world/latin_america/rss.xml", 3),
    ("https://www.cbc.ca/cmlink/rss-canada",3),
    ("https://www.allsides.com/rss/news", 3),
    ("https://www.nationalreview.com/feed/", 5),
    ("https://rss.upi.com/news/news.rss", 3),
    ("https://www.politico.com/rss/politicopicks.xml", 5),
    ("https://www.yahoo.com/news/rss",5),
    ("https://sports.yahoo.com/rss/", 3),
    ("https://news.google.com/rss", 5),
    ("https://www.space.com/feeds/all", 5),
    ("https://feeds.bloomberg.com/markets/news.rss", 5),
    ("https://phys.org/rss-feed/breaking/", 5),
    ("http://feeds.arstechnica.com/arstechnica/index/", 3),
    ("http://rss.sciam.com/ScientificAmerican-Global", 3),
    ("https://www.maritime-executive.com/articles.rss", 3),
    ("https://www.pravda.com.ua/eng/rss/view_news/", 5),
    ("https://www.themoscowtimes.com/rss/news", 3),
    ("https://www.understandingwar.org/feeds-publications.xml", 2)
]
from modules import scraper
from modules import classifier
from modules import summarizer
from modules import cache_files
from modules import ftp_uploader
from modules import super_summary
from modules import locations


app = Flask(__name__)
def format_datetime(value, fmt='%Y-%m-%d %H:%M:%S'):
    if value is None:  # Add this line
        return ''
    elif isinstance(value, time.struct_time):
        value = datetime.fromtimestamp(time.mktime(value))
    return value.strftime(fmt)

app.jinja_env.filters['strftime'] = format_datetime

# def main():
#     if not os.path.exists(cache_directory):
#         os.makedirs(cache_directory)

#     cache_file = os.path.join(cache_directory, 'summaries.p')

#     if cache_files.is_cache_valid(cache_file, max_cache_age=max_cache_age_hours):
#         try:
#             summaries = cache_files.load_cache(cache_file)
#         except Exception as e:
#             print(f"Error while loading cache: {e}")
#             summaries = []
#     else:
#         all_headlines = scraper.scrape_headlines(sources, use_tqdm)
#         categorized_headlines = classifier.categorize_headlines(all_headlines, model_categorize_headlines)
#         summaries = summarizer.summarize_articles(categorized_headlines, retries_summarize_articles, wait_time_seconds_summarize_articles)
#         cache_files.save_cache(cache_file, summaries)

#     cache_files.save_to_weekly_cache(summaries, weekly_cache_file)
#     organized_summaries = summarizer.organize_summaries_by_category(summaries)
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     super_summary_text = super_summary.get_super_summary()

#     # Generate and save HTML
#     with app.app_context():
#         sorted_organized_summaries = dict(sorted(organized_summaries.items(), key=lambda item: categories.index(item[0]) if item[0] in categories else float('inf')))
#         html_string = render_template('home.html', categories=sorted_organized_summaries, timestamp=timestamp, super_summary=super_summary_text)

#     # Create the archive directory if it doesn't exist
#     archive_dir = 'archive'
#     if not os.path.exists(archive_dir):
#         os.makedirs(archive_dir)

#     # Generate a unique file name based on the current date
#     current_date = datetime.now().strftime("%Y-%m-%d")
#     file_name = f'test_home_{current_date}.html'

#     # Define the file path
#     file_path = os.path.join(archive_dir, file_name)

#     # Save the HTML string to the archive folder
#     with open(file_path, 'w', encoding='utf-8') as file:
#         file.write(html_string)
#         ftp_uploader.upload_to_ftp(file_path, ftp_host, ftp_user, ftp_password, ftp_directory, 'index_modular.html')

#     # Return the generated HTML to the user
#     return html_string

def main():
    if not os.path.exists(cache_directory):
        os.makedirs(cache_directory)

    cache_file = os.path.join(cache_directory, 'summaries.p')

    if cache_files.is_cache_valid(cache_file, max_cache_age=max_cache_age_hours):
        try:
            summaries = cache_files.load_cache(cache_file)
        except Exception as e:
            print(f"Error while loading cache: {e}")
            summaries = []
    else:
        all_headlines = scraper.scrape_headlines(sources, use_tqdm)
        categorized_headlines = classifier.categorize_headlines(all_headlines, model_categorize_headlines)
        summaries = summarizer.summarize_articles(categorized_headlines, retries_summarize_articles, wait_time_seconds_summarize_articles)
        cache_files.save_cache(cache_file, summaries)

    # Add this after saving the cache
    extracted_locations = locations.extract_locations(summaries)
    coordinates = locations.get_coordinates(extracted_locations) # Get coordinates

    cache_files.save_to_weekly_cache(summaries, weekly_cache_file)
    organized_summaries = summarizer.organize_summaries_by_category(summaries)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    super_summary_text = super_summary.get_super_summary()
    


    # Generate and save JSON
    news = {
        "timestamp": timestamp,
        "super_summary": super_summary_text,
        "categories": []
    }

    for category, summaries in organized_summaries.items():
        news_category = {
            "name": category,
            "summaries": []
        }
        for summary in summaries:
            news_summary = {
            "headline": summary[0],
            "summary": summary[1],
            "link": summary[2],
            "timestamp": format_datetime(summary[3]),
            "source": summary[4]
}
            news_category["summaries"].append(news_summary)
        news["categories"].append(news_category)

    # Add locations and coordinates to the news summaries
    news = locations.append_locations_to_news_json(news, summaries, extracted_locations, coordinates)

    # Save the updated news data to a JSON file
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)

    # Upload the JSON file to the server
    ftp_uploader.upload_to_ftp('news.json', ftp_host, ftp_user, ftp_password, ftp_directory, 'news.json')

    # Return the generated news data
    return news


if __name__ == "__main__":
    main()
