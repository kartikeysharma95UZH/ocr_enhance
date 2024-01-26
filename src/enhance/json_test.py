# import numpy as np
import os
import json
from collections import defaultdict
# import cv2

# class grouping all properties related to a single text block
# class Block:

# 	def __init__(self, arg):

# 		if isinstance(arg, np.ndarray):
# 			self.image = arg
# 		elif isinstance(arg, str):
# 			self.block_id = arg

# 		self.bin_image = None
# 		self.orig_block_id = None
# 		self.inv_image = None
# 		self.font = None
# 		self.lines = None
# 		self.ocr = None
# 		self.ocr_words = None
# 		self.ocr_alto = None
# 		self.ocr_ori = None
# 		self.ocr_gt = None
# 		self.name = None
# 		self.score = None
# 		self.score_ori = None
# 		self.block_type = None
# 		self.page_id = None
# 		self.ark = None
# 		self.year = None
# 		self.lang_ori = None
# 		self.lang_gt = None
# 		self.composed = False
# 		self.rotated = False
# 		self.coordinates = None
# 		self.offset_alto = None
# 		self.tokens_ori = None
# 		self.tokens_gt = None
# 		self.dict_ori = None
# 		self.garbage_ori = None
# 		self.trigrams_gt = None
# 		self.trigrams_ori = None
# 		self.enhance = None

# 	# returns a string version of the ocr output of the block
# 	def __str__(self):
# 		return_str = ""
# 		if self.ocr != None:
# 			if self.name != None:
# 				return_str += self.name + ':\n'
# 			for i, line in enumerate(self.ocr.split('\n')):
# 				return_str += str(i+1) + ':\t' + line + '\n'
# 		return return_str


def parse_pages_structure(root_path):
    pages_directory = os.path.join(root_path, 'pages')
    image_directory = os.path.join(root_path, 'images')

    # Dictionary to store information about each ALTO equivalent file
    pages_data = {}

    # Dictionary to store the frequency of each unique ID
    unique_id_frequency = defaultdict(int)

    # Iterate through each JSON file in the directory
    for json_file_name in os.listdir(root_path):
        # Check if the file is a JSON file
        if json_file_name.endswith('.json'):
            ark_id = json_file_name
            # issues_file_path = os.path.join(root_path, json_file_name)

            # # Load JSON file
            # with open(issues_file_path, 'r', encoding='utf-8') as json_file:
            #     json_data = json.load(json_file)

                # Extract "id" field and store it inside "ark"
                # ark_id = json_data.get('i', [])[0].get('m', {}).get('id', None)
                
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

    return pages_data, ark_id, total_blocks 