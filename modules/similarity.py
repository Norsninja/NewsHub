import pickle
from sentence_transformers import SentenceTransformer
import numpy as np
import configparser
from typing import Dict, List, Tuple

# Config parser
config = configparser.ConfigParser()
config.read('modules/suite_config.ini')

# Model config
MODEL_NAME = config.get('Models', 'SimilarityModel')

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