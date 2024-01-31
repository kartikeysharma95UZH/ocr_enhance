import os
import json
from collections import defaultdict

def parse_pages_structure(root_path: str):
    """
    Parses the structure of pages in an issue.

    Args:
        root_path (str): The root path of the issue containing 'pages' and 'images' directories.

    Returns:
        Tuple[Dict[str, Dict[str, Optional[str]]], int]:
            A tuple containing:
                - A dictionary with region information about each pages.
                - The total number of blocks across all pages.

    Raises:
        Any exceptions raised during the parsing.

    Note:
        This function takes the original path of the issue as input, parses each page of the issue,
        extracts the 'pOf' IDs, and appends 'block_1', 'block_2', etc., depending on their frequency
        inside each page. Image paths and page file paths are also extracted and stored in the dictionary.
        The function prepares the entire structure of all the pages and how many blocks are present inside each page.

    Example:
        >>> parse_pages_structure('/path/to/issue')
    """    
    pages_directory = os.path.join(root_path, 'pages')
    image_directory = os.path.join(root_path, 'images')

    # Dictionary to store information about each ALTO equivalent file
    pages_data = {}

    # Dictionary to store the frequency of each unique ID
    unique_id_frequency = defaultdict(int)
                
    total_blocks = 0
    # Iterate through each JSON file in the directory
    for pages_file_name in os.listdir(pages_directory):
        # Check if the file is a JSON file
        if pages_file_name.endswith('.json'):
            pages_file_path = os.path.join(pages_directory, pages_file_name)

            # Load JSON file
            with open(pages_file_path, 'r', encoding='utf-8') as alto_file:
                pages_json_data = json.load(alto_file)

                # Extract unique IDs from the ALTO equivalent file
                unique_ids = []
                for region_info in pages_json_data.get('r', []):
                    part_id = region_info.get('pOf')
                    if part_id:
                        unique_ids.append(part_id)

                # Create a dictionary to store information about each article ID
                articles_info = {}
                 
                for unique_id in unique_ids:
                    unique_id_frequency[unique_id] += 1
                    block_name = f"{unique_id}-block_{unique_id_frequency[unique_id]}"
                    articles_info[block_name] = {}
                    total_blocks += 1  

                print(total_blocks)

                # Add JSON file information to the pages_data dictionary
                pages_data[pages_file_name] = {
                    'image': os.path.join(image_directory, f"{pages_json_data['id']}.png"),
                    'page': pages_file_path,
                    'blocks': articles_info,
                    # Add other relevant attributes based on your data structure
                }

                # Include previous block information
                for block_name, block_info in pages_json_data.get('blocks', {}).items():
                    pages_data[pages_file_name]['blocks'][block_name] = block_info

    return pages_data, total_blocks 