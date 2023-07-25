# NewsHub
NewsPlanetAi is an advanced news aggregator and summarizer built with Python. It scrapes headlines from various news sources, categorizes them, summarizes the articles, extracts geographical locations, and generates a "super summary". It uses OpenAI's GPT-3 model for text classification and summarization.

## Overview of Modules

- **scraper.py:** Scrapes headlines from various news sources.
- **classifier.py:** Categorizes headlines using OpenAI's GPT-3 model.
- **cache_files.py:** Provides functions for saving and loading data from cache files.
- **errors.py:** Provides a function for making robust API calls to OpenAI.
- **ftp_uploader.py:** Uploads files to an FTP server.
- **summarizer.py:** Generates summaries for articles and organizes them by category.
- **super_summary.py:** Generates a "super summary" using a list of news summaries.
- **locations.py:** Extracts and appends geographical locations to the news summaries.

## Usage

The main functionality of NewsPlanetAi is provided by the `main.py` script. This script coordinates the process of scraping headlines, categorizing them, summarizing the articles, and generating a super summary. It then saves the generated news data to a JSON file and uploads the file to an FTP server.

To run the script, simply execute the `main.py` script (I will update requirements soon)

Make sure to set up the suite_config.ini file with your configuration settings before running the script.

# Example suite_config.ini:

[General]
UseTqdm = True
TruncateMaxTokens = 4096

[FTP]
Host = your_ftp_host
User = your_ftp_username
Password = your_ftp_password
Directory = your_ftp_directory

[Cache]
Directory = cache_directory_path
MaxAgeHours = 24
WeeklyCacheFile = weekly_cache.p
DailyCacheFile = daily_cache.p
LocCacheFile = locations_cache.p

[Summaries]
MaxSummaryLength = 4096
MaxCacheAgeHours = 24

[Headlines]
Categories = Category1, Category2, Category3

[Models]
CategorizeHeadlines = model_name_for_categorizing_headlines
SummarizeArticles = model_name_for_summarizing_articles
SummarizeSuperSummary = model_name_for_summarizing_super_summary
GetSuperSummary = model_name_for_getting_super_summary

[Retry]
SummarizeArticlesRetries = 3
SummarizeArticlesWaitTimeSeconds = 2
SummarizeSuperSummaryRetries = 3
SummarizeSuperSummaryWaitTimeSeconds = 2

[OPENAI]
OPENAI_API_KEY = your_openai_api_key


## Configuration
The suite uses a configuration file (suite_config.ini) to handle various settings. This includes the OpenAI API key, FTP server details, cache settings, and model names for various tasks.

## Note
The suite uses OpenAI's GPT-3 model, which is a powerful language model capable of tasks like text classification and summarization. The quality and effectiveness of the suite largely depend on the performance of the GPT-3 model.

## NewsPlanetAi in Action

You can see NewsPlanetAi in action at [NewsPlanetAi.com](http://www.newsplanetai.com).



