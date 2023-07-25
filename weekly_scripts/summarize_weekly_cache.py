from transformers import BartForConditionalGeneration, BartTokenizer, pipeline
import pickle
import os
from tqdm import tqdm
import json
import torch
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Replace '0' with the GPU index you want to use
# Check if GPU is available and use GPU:0 (if available)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

if torch.cuda.is_available():
    print("CUDA is available. GPU(s) are accessible.")
    print(f"Number of available GPUs: {torch.cuda.device_count()}")
    print(f"Current GPU name: {torch.cuda.get_device_name(0)}")
else:
    print("CUDA is not available. Using CPU for computations.")


def summarize_weekly_cache(cache_file='cache/weekly_cache.pkl'):
    try:
        # Check if the cache file exists
        if not os.path.exists(cache_file):
            print(f"No cache file found at {cache_file}")
            return

        # Load the weekly cache
        with open(cache_file, 'rb') as f:
            weekly_cache = pickle.load(f)

        # Initialize the tokenizer and model
        model_name = 'facebook/bart-large-cnn'
        tokenizer = BartTokenizer.from_pretrained(model_name)
        model = BartForConditionalGeneration.from_pretrained(model_name).to(device)

        # Initialize the summarization pipeline
        summarizer = pipeline('summarization', model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)


        # Create a dictionary to hold the summarized summaries
        summarized_summaries = {}

        # Iterate over the days of the week
        for day, summaries in tqdm(weekly_cache.items(), desc="Processing days"):
            # Initialize a list to hold the summarized summaries for this day
            day_summaries = []

            # Summarize each summary individually
            for summary in tqdm(summaries, desc=f"Processing summaries for {day}", leave=False):
                # Extract the summary from the tuple
                text = summary[2]

                # Generate a summary of the summary
                summary = summarizer(text, max_length=30, min_length=10, do_sample=False)

                # Add the summary to the list
                day_summaries.append(summary[0]['summary_text'])

            # Save the list of summarized summaries for this day in the dictionary
            summarized_summaries[day] = day_summaries

        return summarized_summaries
    except Exception as e:
        print(f"Error while summarizing weekly cache: {e}")
    


def summarize_day_summaries(summaries, max_length=300, min_length=200, model_name='facebook/bart-large-cnn'):
    """
    Function to summarize a list of summaries for a day into a single summary for the whole day.
    """
    # Initialize the tokenizer and model
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name).to(device)

    # Initialize the summarization pipeline
    summarizer = pipeline('summarization', model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)

    # Join the summaries into one string
    text = ' '.join(summaries)

    # Divide the text into chunks of approximately 10000 characters each
    chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]

    # Initialize a list to hold the summaries of the chunks
    chunk_summaries = []

    # Summarize each chunk and add the summary to the list
    for chunk in chunks:
        chunk_summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
        chunk_summaries.append(chunk_summary[0]['summary_text'])

    # Combine the chunk summaries into one string
    summary = ' '.join(chunk_summaries)

    return summary


def main():
    summarized_summaries = summarize_weekly_cache()

    # Generate a summarized summary for each day and add it to the dictionary
    for day, summaries in summarized_summaries.items():
        day_summary = summarize_day_summaries(summaries)
        summarized_summaries[day] = {"Summaries": summaries, "Summary of the day": day_summary}

    # Save the summarized summaries to a file
    with open('weekly_scripts/final_weekly_summaries.json', 'w', encoding='utf-8') as f:
        json.dump(summarized_summaries, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()




