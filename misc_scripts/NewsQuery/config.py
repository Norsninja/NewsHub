import configparser
import os

def load_config(filepath):
    """
    Load configuration settings from the given file path.

    Parameters:
    - filepath (str): Path to the configuration file.

    Returns:
    - dict: Dictionary containing configuration settings.
    """
    config = configparser.ConfigParser()
    config.read(filepath)
    
    # Extracting the OpenAI API key and setting it as an environment variable
    os.environ['OPENAI_API_KEY'] = config['OPENAI']['OPENAI_API_KEY']
    
    return {
        'openai_api_key': os.environ['OPENAI_API_KEY']
    }
