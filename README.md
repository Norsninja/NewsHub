
# NewsPlanetAI: AI-Powered News Summarization and Broadcasting

## Overview

NewsPlanetAI is an innovative project that leverages advanced AI technologies for scraping, summarizing, and broadcasting news. The system is designed to automatically fetch news articles from various sources, categorize and summarize them, and then compile these summaries into a concise Super Summary. This Super Summary is converted into an audio format using Eleven Labs Text-to-Speech (TTS) technology, giving it a unique voice similar to a blend of David Attenborough and Morgan Freeman, and is subsequently uploaded to SoundCloud for public access.

## Project Structure

The project comprises several Python scripts, each serving a specific role in the news aggregation and summarization process:

- **scraper.py:** Scrapes headlines from various news sources.
- **classifier.py:** Categorizes headlines using OpenAI's GPT-3 model.
- **cache_files.py:** Provides functions for saving and loading data from cache files.
- **errors.py:** Provides a function for making robust API calls to OpenAI.
- **ftp_uploader.py:** Uploads files to an FTP server.
- **summarizer.py:** Generates summaries for articles and organizes them by category.
- **super_summary.py:** Generates a "super summary" using a list of news summaries.
- **locations.py:** Extracts and appends geographical locations to the news summaries.
- **main.py:** Orchestrates the overall process, from scraping to summarization.

## Process Flow

1. **Scraping Headlines**: Uses Goose3 and Feedparser to extract headlines from various news sources.
2. **Categorizing Headlines**: Employs GPT-3.5 Turbo 1106 to categorize headlines.
3. **Summarizing Articles**: Summarizes articles using GPT-3.5 Turbo 1106.
4. **Caching Summaries**: Stores summaries using the Python `pickle` module.
5. **Grouping Summaries by Category**: Organizes summaries in categories for structured presentation.
6. **Generating Top Articles by Category**: Selects top articles using a Sentence Transformer model.
7. **Summarizing Daily Cache**: Condenses daily news using the BART Large CNN model.
8. **Generating Super Summary**: Compiles a comprehensive summary using GPT-4.
9. **Converting to Audio**: Transforms the Super Summary text into an audio file using Eleven Labs TTS.
10. **Uploading to SoundCloud**: Manually uploads the audio file to SoundCloud.
11. **Social Media Promotion**: Generates promotional content for social media platforms.

## Technologies

- **AI Models**: GPT-3.5 Turbo, GPT-4, BART Large CNN, Sentence Transformers.
- **Text-to-Speech**: Eleven Labs TTS.
- **Data Handling**: Python, PyTorch, Goose3, Feedparser, `pickle`.
- **Geocoding and Mapping**: GeoPy.
- **Social Media Integration**: Custom scripts utilizing GPT models.

## Setup and Configuration

To run NewsPlanetAI, users need to set up their own website with FTP details for uploading content. Additionally, a `suite_config.ini` file must be created in the `modules` folder with the necessary configurations, such as API keys, model details, and category settings.

### Configuration File Structure

```ini
[General]
UseTqdm = True
TruncateMaxTokens = 2000

[FTP]
Host = ftp.fakenews.com
User = cortex
Password = AFancyDerickDotCom
Directory = /public_html/
[Cache]
Directory = cache
MaxAgeHours = 1
WeeklyCacheFile = cache/your_overall_cache.pkl
DailyCacheFile = cache/daily_summaries.p
LocCacheFile = cache/locations.pkl

[Summaries]
MaxSummaryLength = 800
MaxCacheAgeHours = 12

[Headlines]
Categories = World News, US News, ...

[Models]
CategorizeHeadlines = gpt-3.5-turbo-1106
SummarizeArticles = gpt-3.5-turbo-1106
SummarizeSuperSummary = gpt-3.5-turbo-1106
GetSuperSummary = gpt-4-1106-preview
SimilarityModel = sentence-transformers/all-MiniLM-L6-v2

[Retry]
SummarizeArticlesRetries = 3
SummarizeArticlesWaitTimeSeconds = 2
SummarizeSuperSummaryRetries = 3
SummarizeSuperSummaryWaitTimeSeconds = 2

[OPENAI]
OPENAI_API_KEY = YourOpenAIKey

[THRESHOLDS]
SIMILARITY_THRESHOLD = 0.7
TOP_N_ARTICLES = 1

[logging]
level = WARNING

[telegram]
api_id = getyourown
api_id = getyourown
api_hash = getyourown
phone_number = +getyourown

[TWITTER]
api_key = getyourown
api_secret_key = getyourown
access_token = getyourown-getyourown
access_token_secret = getyourown
ini```

### Running the System

The system is designed to be run periodically (e.g., every hour) using a task scheduler that executes the `main.py` script.

## Contributions

NewsPlanetAI is an open-source project. Contributions, suggestions, and feedback are welcome to enhance its functionality and accuracy.

