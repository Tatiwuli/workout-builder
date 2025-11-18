import os 
from datetime import datetime
import json
import hashlib


def combine_texts(texts: list) -> str:
    """
    Combines multiple texts into a structured format.
    
    Args:
        texts (list): List of text items to combine.
    
    Returns:
        str: Combined text with section separators.
    """
    return "\n\n### Section ###\n\n".join(map(str, texts))


def generate_cache_key(content: str, max_length: int = 64) -> str:
    """
    Generate a consistent cache key from content string.
    
    Args:
        content (str): The content to generate a cache key from (e.g., shared_prefix)
        max_length (int): Maximum length of the cache key (OpenAI supports up to 64 chars)
    
    Returns:
        str: A hash-based cache key
    """
    # Generate SHA256 hash and take first max_length characters
    hash_obj = hashlib.sha256(content.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    return hash_hex[:max_length]


def save_output_to_json( output_data: dict, file_prefix: str, model_used: str = None):
    """
    Saves the llm output to a JSON file.

    Args:
        output_data (dict): Data to save.
        file_prefix (str): Prefix for the JSON file name.

    Returns:
        str: Path to the saved JSON file.
    """
    # Get absolute path to backend directory (backend/app/utils/)
    backend_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    folder_path = os.path.join(
        backend_dir, "data", f"{file_prefix}_json")
    os.makedirs(folder_path, exist_ok=True)
    timestamp = datetime.now().strftime("%m_%d_%H_%M_%S")
    file_path = os.path.join(
        folder_path, f"{file_prefix}_{timestamp}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)
    return file_path
