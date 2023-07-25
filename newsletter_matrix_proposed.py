import pickle
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import glob
import ftplib
import configparser
from typing import Dict, List, Tuple

# Config parser
config = configparser.ConfigParser()
config.read('config.ini')

# FTP config
FTP_HOST = config.get('FTP', 'FTP_HOST')
FTP_USER = config.get('FTP', 'FTP_USER')
FTP_PASSWORD = config.get('FTP', 'FTP_PASSWORD')
FTP_DIR = config.get('FTP', 'FTP_DIR')
FTP_FILENAME = config.get('FTP', 'FTP_FILENAME')

# Model config
MODEL_NAME = config.get('MODEL', 'MODEL_NAME')

# Thresholds
SIMILARITY_THRESHOLD = config.getfloat('THRESHOLDS', 'SIMILARITY_THRESHOLD')
TOP_N_ARTICLES = config.getint('THRESHOLDS', 'TOP_N_ARTICLES')


def load_data(filepath: str) -> List[Tuple]:
    with open(filepath, 'rb') as f:
        summaries = pickle.load(f)
    print(f"Loaded {len(summaries)} summaries")
    return summaries


def group_by_category(summaries: List[Tuple]) -> Dict[str, List[Tuple]]:
    summaries_by_categories = {}
    for summary in summaries:
        if summary[1] not in summaries_by_categories:
            summaries_by_categories[summary[1]] = [summary]
        else:
            summaries_by_categories[summary[1]].append(summary)
    print(f"Grouped summaries into {len(summaries_by_categories)} categories")
    return summaries_by_categories


def generate_embeddings(summaries: List[Tuple], model: SentenceTransformer) -> np.ndarray:
    corpus = [summary[0] + ' ' + summary[2][:500] for summary in summaries]
    embeddings = model.encode(corpus, convert_to_tensor=True)
    embeddings_np = embeddings.cpu().numpy()
    normalized_embeddings = embeddings_np / np.linalg.norm(embeddings_np, axis=1, keepdims=True)
    return normalized_embeddings


def generate_similarity_matrix(normalized_embeddings: np.ndarray) -> np.ndarray:
    similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)
    np.fill_diagonal(similarity_matrix, -1)
    return similarity_matrix


def get_top_articles(similarity_matrix: np.ndarray, category_summaries: List[Tuple], threshold: float, top_n: int) -> List[Tuple]:
    indices = np.argsort(similarity_matrix.flatten())[::-1]
    top_articles = []
    for index in indices:
        row_index, col_index = np.unravel_index(index, similarity_matrix.shape)
        if row_index >= col_index:
            continue
        if similarity_matrix[row_index][col_index] < threshold:
            continue
        top_articles.append((category_summaries[row_index], category_summaries[col_index]))
        if len(top_articles) >= top_n:
            break
    print(f"Found {len(top_articles)} top articles")
    return top_articles


def generate_top_articles_by_category(summaries_by_categories: Dict[str, List[Tuple]], model: SentenceTransformer, threshold: float, top_n: int) -> Dict[str, List[Tuple]]:
    top_articles_by_category = {}
    for category, category_summaries in summaries_by_categories.items():
        normalized_embeddings = generate_embeddings(category_summaries, model)
        similarity_matrix = generate_similarity_matrix(normalized_embeddings)
        top_articles = get_top_articles(similarity_matrix, category_summaries, threshold, top_n)
        if top_articles:
            top_articles_by_category[category] = top_articles
    return top_articles_by_category


def clean_text(text: str) -> str:
    if isinstance(text, bytes):
        text = text.decode('utf-8', 'ignore')
    else:
        text = text.encode('ascii', 'ignore').decode('ascii')
    return text


def generate_newsletter(top_articles_by_category: Dict[str, List[Tuple]]) -> str:


        newsletter = """
        <html>
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily Newsletter with Cortex</title>
        <style>
        body {
            font-family: Arial, sans-serif;
        }

        h2 {
            color: #333;
        }

        h3 {
            color: #666;
        }

        a {
            color: #1a0dab;
            text-decoration: none;
        }

        hr {
            border: 0;
            height: 1px;
            background: #333;
            margin-top: 2em;
            margin-bottom: 2em;
        }

        .container {
            max-width: 600px;
            margin: auto;
        
        }
        .responsive-image {
        max-width: 100%;
        height: auto;
        }

        .super-summary {
            padding-top: 2em;
            border-top: 1px solid #333;
        }
        </style>
        </head>
        <body>
            <div style="background-color: #343a40; color: #ffffff; padding: 10px;">
                <a style="color: #ffffff; text-decoration: none;" href="https://newsplanetai.com" target="_blank">NewsPlanetAi</a>
                <a style="color: #ffffff; text-decoration: none;" href="https://emailcontent.newsplanetai.com/how_made.html" target="_blank">How it's Made</a>           
                <a style="color: #ffffff; text-decoration: none;" href="https://newsplanetai.com/privacy.html" target="_blank">Privacy</a>
            </div>
        <div class="container">
        <h1 style="font-family: Arial, sans-serif; color: #333;">Daily Briefing with Cortex</h1>
        <div style="text-align: center; background-color: #3da0ae; color: #ffffff; padding: 10px; border-radius: 5px;">
            <h2 style="margin: 0;">Daily Briefing - July 25, 2023 - NewsPlanetAi</h2>
            <a href="https://soundcloud.com/norsninja/daily-briefing-july-25-2023-830-am?si=675d12b175c348e0bd3f48375ba01189&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing" target="_blank" style="color: #ffffff; text-decoration: none; display: inline-block; margin-top: 10px; padding: 10px 20px; background-color: #ffffff; color: #3da0ae; border-radius: 20px;">Listen on SoundCloud</a>
        </div>
        <hr style="border: 0; height: 1px; background: #333; margin-top: 2em; margin-bottom: 2em;">

        """
        newsletter += f"<h1>Top Headlines</h1>"
        for category, pairs in top_articles_by_category.items():
            for pair in pairs:
                headline1, _, summary1, url1, _, _ = pair[0]  # Selects the first article of the pair

                headline1 = clean_text(headline1)
                category = clean_text(category)
                summary1 = clean_text(summary1)

                newsletter += f"<h2>{headline1}</h2>"
                newsletter += f"<h3>Category: {category}</h3>"
                newsletter += f"<p>{summary1}</p>"
                newsletter += f'<p><a href="{url1}" target="_blank">Read more</a></p>'
                newsletter += '<hr>'

        newsletter += """
        <h1 style="font-family: Arial, sans-serif; color: #333;">NewsPlanetAi Interactive Map</h1>
        <div style="text-align: center;">
            <a href="https://emailcontent.newsplanetai.com/map_folio.html" target="_blank">
                <img style="max-width: 100%; height: auto;" src="images/premium_map.png" alt="Premium Map">
            </a>
            <p>
                <a href="https://emailcontent.newsplanetai.com/map_folio.html" target="_blank" style="color: #1a0dab; text-decoration: none;">Click Here</a>
            </p>
        </div>
        <hr style="border: 0; height: 1px; background: #333; margin-top: 2em; margin-bottom: 2em;">
        """
        # Get the list of files in the "super_summaries" directory
        files = glob.glob('super_summaries/*.txt')

        # Find the latest file
        latest_file = max(files, key=os.path.getctime)

        # Read the text from the latest file
        with open(latest_file, 'r', encoding='utf-8', errors='ignore') as f:
            super_summary = f.read()

        # Convert the super summary to HTML
        super_summary_html = "<p>" + super_summary.replace("\n", "<br>") + "</p>"

        # Append the super summary to the newsletter
        newsletter += '''<div style="
                            border: 1px solid #3da0ae;
                            padding: 15px;
                            margin: 10px 0;
                            border-radius: 5px;
                            background-color: #f1f1f1;">
                            <h2 style="
                                color: #3da0ae;
                                text-align: center;
                                padding: 10px 0;">Super Summary</h2>'''

        newsletter += super_summary_html
        newsletter += '</div>'

        newsletter += "</div></body></html>"

        return newsletter


def upload_to_ftp(file_path: str, ftp_host: str, ftp_user: str, ftp_password: str, ftp_dir: str, ftp_filename: str) -> None:
    ftp = ftplib.FTP(ftp_host)
    ftp.login(ftp_user, ftp_password)
    ftp.cwd(ftp_dir)
    with open(file_path, "rb") as file:
        ftp.storbinary(f"STOR {ftp_filename}", file)
    ftp.quit()
    print(f"Finished uploading {file_path} to FTP server {ftp_host}")


def main():
    # Load and preprocess data
    print("Loading and preprocessing data")
    summaries = load_data('cache/summaries.p')
    summaries_by_categories = group_by_category(summaries)

    # Load model
    print("Loading model")
    model = SentenceTransformer(MODEL_NAME)

    # Generate top articles by category
    print("Generating top articles by category")
    top_articles_by_category = generate_top_articles_by_category(summaries_by_categories, model, SIMILARITY_THRESHOLD, TOP_N_ARTICLES)

    # Generate newsletter
    print("Generating newsletter")
    newsletter = generate_newsletter(top_articles_by_category)

    # Write the newsletter to a file
    with open(FTP_FILENAME, 'w', encoding='utf-8') as f:
        f.write(newsletter)
    print(f"Saved newsletter to '{FTP_FILENAME}'")

    # Upload newsletter to FTP
    print("Uploading newsletter to FTP server")
    upload_to_ftp(FTP_FILENAME, FTP_HOST, FTP_USER, FTP_PASSWORD, FTP_DIR, FTP_FILENAME)

if __name__ == "__main__":
    main()

