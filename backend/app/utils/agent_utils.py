import os 
from datetime import datetime
import json


def combine_texts(texts: list) -> str:
    """
    Combines multiple texts into a structured format.
    
    Args:
        texts (list): List of text items to combine.
    
    Returns:
        str: Combined text with section separators.
    """
    return "\n\n### Section ###\n\n".join(map(str, texts))


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
