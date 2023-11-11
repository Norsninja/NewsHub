import os
import torch
from transformers import BartTokenizer, BartForConditionalGeneration
from transformers import pipeline
import requests
from bs4 import BeautifulSoup
import configparser
from nltk.tokenize import sent_tokenize
import re

config = configparser.ConfigParser()

config.read('modules/suite_config.ini')
openai_api_key = config['OPENAI']['OPENAI_API_KEY']

def summarize_text_file(file_path, model_name='facebook/bart-large-cnn', chunk_size=2000, batch_size=10, max_length=100, min_length=60):
    # Check if GPU is available and use GPU:0 (if available)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Replace '0' with the GPU index you want to use

    # Check if the text file exists
    if not os.path.exists(file_path):
        print(f"No text file found at {file_path}")
        return

    # Initialize the tokenizer and model
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name).to(device)

    # Initialize the summarization pipeline
    print("Initialize the summarize text file pipeline.")
    summarizer = pipeline('summarization', model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)

    # Read the text file
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Remove unnecessary elements and excessive line breaks
    cleaned_text = re.sub(r'\n\n\n+', '\n\n', text)

    # Split the text into paragraphs or logical sections
    sections = cleaned_text.split('\n\n')

    # Summarize each section
    summaries = []
    print("breaking text into sections")
    for section in sections:
        # Skip sections that are too short
        if len(section) < chunk_size:
            continue
        print("tokenizing sections")
        # Tokenize the section
        tokens = tokenizer.encode(section, truncation=True, max_length=1000)

        # Decode the tokens back into text
        section = tokenizer.decode(tokens)

        # Determine an appropriate max_length for summarization
        adaptive_max_length = min(max_length, len(tokens) // 2)

        # Summarize the section
        summary = summarizer(section, max_length=adaptive_max_length, min_length=min_length, batch_size=batch_size)
        summaries.append(summary[0]['summary_text'])


    return " ".join(summaries)

def summarize_web_page(url, model_name='facebook/bart-large-cnn', chunk_size=2000, batch_size=10, max_length=600, min_length=200):
    # Fetch the content of the web page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the title and the link to the full report
    title_tag = soup.find('span', style="font-size: medium;")
    if not title_tag:
        print("Could not find the title. Exiting.")
        return

    title = title_tag.text.strip()
    publication_url_tag = soup.find('a', string='Click here to read the full report.')
    if publication_url_tag:
        publication_url = publication_url_tag['href']
    else:
        print("Could not find the link to the full report. Exiting.")
        return

    # Fetch the content of the most recent publication
    print("Fetching text from ISW website")
    publication_response = requests.get(publication_url)
    publication_soup = BeautifulSoup(publication_response.content, 'html.parser')
    text = publication_soup.get_text()
    print("Writing the text file")
    print(len(text))
    # Save the text to a temporary file
    temp_file_path = 'temp_text_file.txt'
    with open(temp_file_path, 'w', encoding='utf-8') as file:
        file.write(text)
    print("Summarizing the text file")
    # Summarize the text file
    summary = summarize_text_file(temp_file_path, model_name, chunk_size, batch_size, max_length, min_length)
    print("Summarization complete:")
    print(len(summary))
    print(title)
    # Append the title to the summary
    summary = title + "\n" + summary
    print("Summarization complete:")
    print(len(summary))
    # Remove the temporary file
    #os.remove(temp_file_path)

    return summary

import openai
from datetime import datetime
def load_openai_api_key(config_file='modules/suite_config.ini'):
    """
    Load the OpenAI API key from a configuration file.
    """
    if not os.path.exists(config_file):
        print(f"No configuration file found at {config_file}")
        return None

    config = configparser.ConfigParser()
    config.read(config_file)

    try:
        api_key = config.get('OPENAI', 'OPENAI_API_KEY')
        return api_key
    except Exception as e:
        print(f"Error while loading OpenAI API key: {e}")
        return None
    
def generate_gpt_completion(prompt, api_key, model='gpt-4-1106-preview', max_tokens=1000, temperature=0.7):
    """Generate a GPT completion given a prompt focused on the war in Ukraine."""
    # Get the current time
    current_time = datetime.now()

    # Format the current time as a string
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    openai.api_key = api_key

    # Append the content from the reference text file
    reference_file_path = "russo_ukranian_war_abridged.txt"
    with open(reference_file_path, 'r', encoding='utf-8') as file:
        reference_text = file.read()
        print("Appending material on the Russo-Ukrainian War.")
    prompt.append((". Reference material on the Russo-Ukrainian War:", reference_text))
    print("Compiled prompt:")
    print(prompt)
    print("Sending prompt to GPT for response:")
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a cutting-edge AI assistant named 'Cortex', tasked with crafting a professional news article titled, 'NewsPlanetAI: Eye on Ukraine', a highly trusted news program. "
                        "Your mission is to provide detailed coverage of the ongoing conflict between Russia and Ukraine. Here are the components of your task:\n\n"
                        "1. 'The Ukraine Conflict Watch': This section is committed to an in-depth analysis of the day's developments in the Russia & Ukraine conflict. "
                        "You will present a summary of the day's events, salient developments, and an impartial analysis of the situation.\n\n"
                        "2. 'Insight Analytica': This part delves into the implications and potential impact of the notable occurrences in the conflict. "
                        "The aim is to maintain neutrality while providing an insightful discussion.\n\n"
                        "3. 'Regional Rundown': Here, you'll focus on pertinent details from different geographical regions affected by the conflict. "
                        "Each significant regional event is identified, its importance elucidated, and its implications underscored.\n\n"
                        "4. Cortex concludes the broadcast in a succint and thoughtful way."
                    ),
                },
                {
                    "role": "user",
                    "content": f"The summaries for for today's, ({current_time_str}), events related to the Russia & Ukraine conflict are: {prompt}. Please craft the today's article as per the instructions provided in one complete response (500 words Max!). Thank you.",
                },
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        if response is not None:
            print("response returned from GPT")
            return response.choices[0].message["content"]

        else:
            print("Error: Failed to generate GPT completion")
            return None
    except Exception as e:
        print(f"Error while generating GPT completion: {e}")
        return None
import glob

def save_summary():
    directory = "ukraine/"
    # Search for all index files with timestamp pattern
    files = glob.glob(os.path.join(directory, "index_*.html"))
    
    # Sort the files to get the latest
    files.sort(reverse=True)
    
    if not files:
        print(f"WARNING: No index file found in {directory}")
        return None

    latest_index_file = files[0]  # The first one in the sorted list is the latest
    
    # Generate the date-based name (e.g., "Thursday_20230817.html")
    day_name = datetime.now().strftime("%A")
    date_stamp = datetime.now().strftime("%Y%m%d")
    previous_html_file_name = f"{day_name}_{date_stamp}.html"
    previous_html_file_path = os.path.join(directory, previous_html_file_name)

    # Check if the file already exists
    if not os.path.exists(previous_html_file_path):
        # Rename the latest index file to the date-based name
        os.rename(latest_index_file, previous_html_file_path)
    
    return previous_html_file_path

def update_links(previous_html_file):
    if previous_html_file:
        # Create the link for the previous HTML file
        link_to_previous = f'<a href="/{previous_html_file}">{previous_html_file.replace("ukraine/", "")}</a><br>\n'
        
        # Append the link to the summary links file
        with open("ukraine/summary_links.html", 'a', encoding='utf-8') as file:
            file.write(link_to_previous)

# Fetch the summary from the ISW website
url = 'https://www.understandingwar.org/backgrounder/ukraine-conflict-updates'
summary = summarize_web_page(url)
print("Summary generated from ISW text:")
print(summary)

# Save the summary and get the previous summary file name
previous_html_file = save_summary()

# Update the list of links
update_links(previous_html_file)
# Prepare the prompt for GPT
prompt = [summary]


# Generate the GPT completion (broadcast) using the summary as a prompt
broadcast = generate_gpt_completion(prompt, openai_api_key)
print("\nGenerated Broadcast:")
print(broadcast)
print(len(broadcast))
# Generate the timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Define the directory and filename
directory = "super_summaries/ukraine"
filename = f"ukraine_daily_report_{timestamp}.txt"
file_path = os.path.join(directory, filename)

# Tokenize the broadcast into sentences
sentences = sent_tokenize(broadcast)

# Save the sentences to the text file, each on a new line
with open(file_path, 'w', encoding='utf-8') as file:
    for sentence in sentences:
        file.write(sentence + '\n')

print(f"Broadcast saved to {file_path}")
from ftplib import FTP

# Function to upload a file to an FTP server
def upload_to_ftp(file_path, host, user, password, remote_path, remote_filename):
    ftp = FTP(host)
    ftp.login(user, password)
    ftp.cwd(remote_path)
    with open(file_path, 'rb') as file:
        ftp.storbinary(f'STOR {remote_filename}', file)
    ftp.quit()

# Replace newline characters with HTML line breaks
broadcast_html = broadcast.replace('\n', '<br>')
# Read the content of the summary links file
summary_links = ""
summary_links_file = "ukraine/summary_links.html"
if os.path.exists(summary_links_file):
    with open(summary_links_file, 'r', encoding='utf-8') as file:
        summary_links = file.read()
# Create an HTML string with the GPT summary
# Get current date and time 
now = datetime.now()

# Format the date and time
date_string = now.strftime("%B %d, %Y")
time_string = now.strftime("%I:%M %p")

# Build title string
title = f"Ukraine Daily Report - {date_string} {time_string}"

html_string = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>{title}</title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        .navbar {{
            background: #343a40;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        .container {{
            background-color: #fff;
            width: 80%;
            color: #333;
            padding: 20px;
            border-radius: 10px;
            margin: 20px auto;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        h1 {{
            font-size: 2.2rem;
            margin-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }}
        .summary p {{
            font-size: 1.1rem;
            line-height: 1.7;
        }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <a class="navbar-brand" href="/">NewsPlanetAi</a>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
                <li class="nav-item">
                    <a class="nav-link" href="/ukraine">Ukraine Daily Report</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="osint_report.html">OSINT report</a>
                </li>
            </ul>
        </div>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
    </button>
    </nav>
    <div class="container">
        <h1>Ukraine Daily Report</h1>
        <p>Generated On: {date_string}</p>
        <div class="summary">
            <p>{broadcast_html}</p>
        </div>
        <div class="previous-summaries">
            <h3>Previous Summaries</h3>
            <p>{summary_links}</p> 
        </div>
        <!-- Notice Section -->
        <div class="notice mt-4">
        <p><strong>Note:</strong> The Ukraine report is generated based on the <a href="https://www.understandingwar.org/backgrounder/ukraine-conflict-updates">Russian Offensive Campaign Assessment for the day</a>, using GPT-4 as well as reference material on the Russian invasion of Ukraine.</p>
    </div>
    </div>
</body>
</html>
"""
# Define the file path with a timestamp
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
file_path_with_timestamp = f'ukraine/index_{timestamp}.html'

# Save the HTML string to the file with the timestamp
with open(file_path_with_timestamp, 'w', encoding='utf-8') as file:
    file.write(html_string)

# Upload the file to the FTP server with a different filename
remote_filename = 'index.html'
upload_to_ftp(file_path_with_timestamp, 'ftp.newsplanetai.com', 'newsrwxb', '#Panthera133!', '/public_html/ukraine/', remote_filename)

print(f"HTML file uploaded to ftp.newsplanetai.com/public_html/ukraine/{remote_filename}")
# Get the filename from the previous path 
previous_path = f"ukraine/{previous_html_file}"
print(previous_path)
previous_filename = os.path.basename(previous_path)

# Upload the previous HTML file  
upload_to_ftp(previous_html_file, 'ftp.newsplanetai.com', 'newsrwxb', '#Panthera133!', '/public_html/ukraine/', previous_filename)
print(f"Previous HTML file uploaded to ftp.newsplanetai.com/public_html/ukraine/{previous_filename}")