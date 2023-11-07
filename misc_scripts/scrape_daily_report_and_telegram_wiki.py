import requests
from bs4 import BeautifulSoup
import time
import logging
import re
import os
import mwclient

logging.basicConfig(level=logging.INFO)

BASE_URL = "https://newsplanetai.com"
MAIN_URL = f"{BASE_URL}/ukraine/"
TELEGRAM_SUMMARY_PATH = r"E:\Newshub\ukraine"

def fetch_url_content(url):
    """Fetch the content of the provided URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def extract_links_from_main_page(content):
    """Extract summary links from the main page content."""
    soup = BeautifulSoup(content, 'html.parser')
    summary_div = soup.find('div', class_='previous-summaries')
    return [a['href'] for a in summary_div.find_all('a')]

def extract_content_from_link(link):
    """Fetch the content of the provided link and extract the summary."""
    full_url = BASE_URL + link
    content = fetch_url_content(full_url)
    if not content:
        return None

    soup = BeautifulSoup(content, 'html.parser')
    summary_div = soup.find('div', class_='summary')
    return str(summary_div)

def extract_date_from_link(link):
    """Extract the date from the link filename."""
    date_pattern = re.compile(r"\w+_(\d{8})\.html")
    match = date_pattern.search(link)
    if match:
        date = match.group(1)  # Extract the YYYYMMDD format date
        logging.info(f"Extracted date from link: {date}")  # Add logging here
        return date
    return None

def extract_telegram_content(date):
    """Extract content from the local Telegram summary for the given date."""
    formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:]}"  # Corrected to YYYY-MM-DD format
    
    filename_prefix = f"telegram_html_summary_{formatted_date}_"
    
    logging.info(f"Looking for files with prefix: {filename_prefix}")
    
    all_files = os.listdir(TELEGRAM_SUMMARY_PATH)
    logging.info(f"All files in the directory: {all_files}")  # Log all files in the directory
    
    matching_files = [f for f in all_files if f.startswith(filename_prefix)]
    
    logging.info(f"Matching files: {matching_files}")
    
    if not matching_files:
        logging.warning(f"No Telegram summary found for {formatted_date}")
        return None

    with open(os.path.join(TELEGRAM_SUMMARY_PATH, matching_files[0]), 'r', encoding='utf-8') as file:
        content = file.read()
    soup = BeautifulSoup(content, 'html.parser')
    summary_div = soup.find('div', class_='summary')
    return str(summary_div)



def create_or_update_page(site, title, content, category):
    """Create or update a wiki page."""
    page = site.Pages[title]
    page_text = content + "\n\n[[Category:" + category + "]]"
    page.save(page_text, summary='Updated by bot')

def update_recent_digests_on_main_page(site, recent_dates):
    """Update the 'Recent Digests' section on the main page."""
    
    # Fetch the current main page content
    main_page = site.Pages["Main Page"]
    content = main_page.text()
    
    # Construct the new 'Recent Digests' list
    new_digest_list = "\n".join([f"* [[Ukraine War Daily Digest {date}|{date[:4]}-{date[4:6]}-{date[6:]}]]" for date in recent_dates])
    
    # Replace the existing 'Recent Digests' list with the new list
    start_marker = ";Latest Reports:"
    end_marker = "== Browse =="
    start_pos = content.find(start_marker) + len(start_marker)
    end_pos = content.find(end_marker)
    new_content = content[:start_pos] + "\n" + new_digest_list + "\n" + content[end_pos:]
    
    # Save the updated content to the main page
    main_page.save(new_content, summary="Updated Recent Digests section")



def main():
    # Establish MediaWiki connection
    site = mwclient.Site('newsplanetai.com/newswiki/', path='/')
    site.login('Wgxjp@NewsPlanetAI_Internal_Bot', 'o2k03jsti211skm9794iqf3cdd3q5j3a')
    
    # Check if the path exists
    if not os.path.exists(TELEGRAM_SUMMARY_PATH):
        logging.error(f"Directory not found: {TELEGRAM_SUMMARY_PATH}")
        return

    main_page_content = fetch_url_content(MAIN_URL)
    if not main_page_content:
        logging.error("Failed to fetch main page content.")
        return

    links = extract_links_from_main_page(main_page_content)

    for link in links:
        logging.info(f"Processing link: {link}")
        ukraine_content = extract_content_from_link(link)
        date = extract_date_from_link(link)
        telegram_content = extract_telegram_content(date)

        # Generate page content for MediaWiki
        combined_content = f'''
        ==NewsPlanetAI: Eye on Ukraine==
        {ukraine_content}
        
        ==Telegram OSINT Briefing for {date}==
        {telegram_content if telegram_content else "No Telegram content for this date."}
        '''
        title = f"Ukraine War Daily Digest {date}"
        create_or_update_page(site, title, combined_content, 'Ukraine War Digest')

        time.sleep(1)  # Rate limit: Wait for 1 second between requests

    logging.info("Daily digests uploaded to MediaWiki.")
    # Generate list of the 10 most recent dates from the links
    # After processing all links, extract the dates from the links
    all_dates = [extract_date_from_link(link) for link in links]
    
    # Sort the dates in descending order to get the most recent dates first
    recent_dates = sorted(all_dates, reverse=True)[:10]

    # Update the "Recent Digests" section on the main page
    update_recent_digests_on_main_page(site, recent_dates)
    
    logging.info("Updated Recent Digests on the main page.")


if __name__ == "__main__":
    main()
