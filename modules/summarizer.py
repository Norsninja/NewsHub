import configparser
import openai
from datetime import datetime
import os
from modules.errors import robust_api_call
from tqdm import tqdm
from modules.scraper import truncate_text, get_full_text
from transformers import BartForConditionalGeneration, BartTokenizer, pipeline
import pickle
import torch

# Load the configuration file
config = configparser.ConfigParser()
config.read('modules/suite_config.ini')

# Access variables
use_tqdm = config.getboolean('General', 'UseTqdm')
openai_api_key = config['OPENAI']['OPENAI_API_KEY']
summarize_articles_model = config['Models']['SummarizeArticles']
summarize_super_summary_model = config['Models']['SummarizeSuperSummary']
cache_file = config['Cache']['DailyCacheFile']
categories_order = config.get('Headlines', 'Categories').split(', ')

openai.api_key = openai_api_key

def summarize_articles(categorized_headlines, retries=3, wait_time_seconds=2):
    summaries = []
    for headline, category, url, timestamp, source in tqdm(categorized_headlines):
        full_text = get_full_text(url)
        truncated_full_text = truncate_text(full_text)
        if truncated_full_text:
            # Prepare the prompt for GPT-3.5-turbo
            prompt = f"Please provide a neutral and concise summary of the following text, focusing on the salient information. Avoid including minor details or background information that doesn't contribute directly to the central message or main events. Remain objective and refrain from including personal opinion or bias:\n\n{truncated_full_text}\n"

            # Print additional info for debugging
            print(f"Headline: {headline}")
            print(f"Prompt: {prompt}")

            # Generate the summary
            response = robust_api_call(lambda: openai.ChatCompletion.create(
                model=summarize_articles_model,
                messages=[
                    {"role": "system", "content": "You are an AI tasked with summarizing news articles in a professional manner"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=180 # Summary Length                
            ), retries=retries, delay=wait_time_seconds)

            if response is not None:
                summary = response['choices'][0]['message']['content']
                summaries.append((headline, category, summary, url, timestamp, source))
            else:
                print(f"Failed to generate summary for {headline} after all retries. Skipping...")
        else:
            print(f"Could not extract full text for: {headline}")
    return summaries

def organize_summaries_by_category(summaries):
    cat_summaries = {cat: [] for cat in categories_order}

    for summary in summaries:
        headline, category, text, link, timestamp, source, location, coordinates = summary
        if category in cat_summaries:
            cat_summaries[category].append((headline, text, link, timestamp, source, location, coordinates))

    return cat_summaries




def summarize_super_summary(super_summary_text):
    truncated_text = truncate_text(super_summary_text)

    if truncated_text:
        prompt = f"Please provide a neutral and concise summary of the following text, focusing on key points and isolating the most important information. Avoid including minor details or background information that doesn't contribute directly to the central message or main events. Remain objective and refrain from including personal opinion or bias:\n\n{truncated_text}\n"

        response = robust_api_call(lambda: openai.ChatCompletion.create(
            model=summarize_super_summary_model,
            messages=[
                {"role": "system", "content": "You are an AI tasked with summarizing news articles in a professional manner."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600                
        ))

        if response is not None:
            summary = response['choices'][0]['message']['content']
        else:
            print("Could not generate a summary for the super summary.")
            return ""
    else:
        print("No text provided to summarize.")
        return ""

    return summary.strip()

def save_super_summary(super_summary):
    # Create the directory if it doesn't exist
    folder_path = 'super_summaries'
    os.makedirs(folder_path, exist_ok=True)

    # Generate a unique file name based on the current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f'module_super_summary_{current_time}.txt'

    # Save the super summary to the text file with the 'utf-8' encoding
    with open(os.path.join(folder_path, file_name), 'w', encoding='utf-8') as file:
        file.write(super_summary)

 
def summarize_daily_cache(cache_file, batch_size=10):
    print("Summarizing Daily cache with BART")
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Replace '0' with the GPU index you want to use
    # Check if GPU is available and use GPU:0 (if available)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    try:
        # Check if the cache file exists
        if not os.path.exists(cache_file):
            print(f"No cache file found at {cache_file}")
            return

        # Load the daily cache
        with open(cache_file, 'rb') as f:
            daily_cache = pickle.load(f)

        # Initialize the tokenizer and model
        model_name = 'facebook/bart-large-cnn'
        tokenizer = BartTokenizer.from_pretrained(model_name)
        model = BartForConditionalGeneration.from_pretrained(model_name).to(device)

        # Initialize the summarization pipeline
        summarizer = pipeline('summarization', model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)

        # Summarize each summary individually
        summarized_summaries = []
        for i in tqdm(range(0, len(daily_cache), batch_size), desc="Processing summaries"):
            batch = daily_cache[i:i+batch_size]
            texts = [summary[2] for summary in batch]  # index 1 assuming this is where the summary text is in your tuple

            summaries = summarizer(texts, max_length=45, min_length=10, do_sample=False)

            for summary in summaries:
                summarized_summaries.append(summary['summary_text'])

        return summarized_summaries
    except Exception as e:
        print(f"Error while summarizing daily cache: {e}")
