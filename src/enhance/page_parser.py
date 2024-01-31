# from xml.dom.minidom import parse
# from lxml import etree
import constants.constants as ct
import numpy as np
from epr.apply_epr import predict
import os
import json
import numpy as np
from typing import Dict, Any

# class grouping all properties related to a single text block
class Block:
	"""
	Class grouping all properties related to a single text block.

	Attributes:
		image (Union[np.ndarray, None]): The image of the text block (if available).
		block_id (Union[str, None]): The ID of the text block (if available).
		bin_image (Union[np.ndarray, None]): Binary image representation of the text block.
		orig_block_id (Union[str, None]): Original block ID.
		inv_image (Union[np.ndarray, None]): Inverted image of the text block.
		font (Union[str, None]): Font information associated with the text block.
		lines (Union[Any, None]): Lines information associated with the text block.
		ocr (Union[str, None]): OCR output of the text block.
		ocr_words (Union[Any, None]): OCR words information associated with the text block.
		ocr_ori (Union[str, None]): Original OCR output of the text block.
		name (Union[str, None]): Name of the text block.
		page_id (Union[Any, None]): ID of the page associated with the text block.
		ark (Union[str, None]): ARK identifier associated with the text block.
		year (Union[Any, None]): Year information associated with the text block.
		lang_ori (Union[str, None]): Original language information associated with the text block.
		lang_gt (Union[Any, None]): Ground truth language information associated with the text block.
		rotated (bool): Boolean indicating if the text block is rotated.
		coordinates (Union[Any, None]): Coordinates information associated with the text block.
		offset_alto (Union[Any, None]): Offset information in ALTO format associated with the text block.
		tokens_ori (Union[Any, None]): Original tokens information associated with the text block.
		dict_ori (Union[Any, None]): Original dictionary information associated with the text block.
		garbage_ori (Union[Any, None]): Original garbage information associated with the text block.
		trigrams_ori (Union[Any, None]): Original trigrams information associated with the text block.
		enhance (Union[Any, None]): Enhancement information associated with the text block.

	Methods:
		__init__(self, arg): Constructor method for the Block class.
		__str__(self): Returns a string version of the OCR output of the block.

	Note:
		The `arg` parameter in the constructor can be either an np.ndarray representing the image of the text block
		or a str representing the block ID. Other attributes are initialized to None and can be populated as needed.

	Example:
		>>> block = Block('example_block_id')
		>>> print(block)
		example_block_id:
		1:    Line 1 of OCR output
		2:    Line 2 of OCR output
		...
	"""	

	def __init__(self, arg):

		if isinstance(arg, np.ndarray):
			self.image = arg
		elif isinstance(arg, str):
			self.block_id = arg

		self.bin_image = None
		self.orig_block_id = None
		self.inv_image = None
		self.font = None
		self.lines = None
		self.ocr = None
		self.ocr_words = None
		self.ocr_ori = None
		self.name = None
		# self.block_type = None
		self.page_id = None
		self.ark = None
		self.year = None
		self.lang_ori = None
		self.lang_gt = None
		# self.composed = False
		self.rotated = False
		self.coordinates = None
		self.offset_alto = None
		self.tokens_ori = None
		self.dict_ori = None
		self.garbage_ori = None
		self.trigrams_ori = None
		self.enhance = None

	# returns a string version of the ocr output of the block
	def __str__(self):
		"""
		Returns a string version of the OCR output of the block.

		Returns:
			str: String representation of the OCR output.
		"""		
		
		return_str = ""
		if self.ocr != None:
			if self.name != None:
				return_str += self.name + ':\n'
			for i, line in enumerate(self.ocr.split('\n')):
				return_str += str(i+1) + ':\t' + line + '\n'
		return return_str

def process_pages_file(root_path: str, page_file_name: str, block_data: Dict[str, Block], features: Any, required_epr: float, models: Any) -> Dict[str, Block]:
	"""
	Process the content of a specific page file, extracting information for each text block/region.

	Args:
		root_path (str): The root path containing the 'pages' directory.
		page_file_name (str): The name of the page file to be processed.
		block_data (Dict[str, Block]): Dictionary containing information about text blocks.
		features (Any): Features object for text processing (if available).
		required_epr (float): Required enhancement prediction threshold.
		models (Any): Models object containing pre-loaded models for prediction.

	Returns:
		Dict[str, Block]: Updated dictionary containing information about text blocks after processing the page.

	Note:
		The function extracts important information like coordinates, original ocr, etc for each block/region inside the page.
		The 'required_epr' parameter is the threshold for enhancement prediction. Blocks with predictions below this
		threshold will not be enhanced.


	Example:
		>>> processed_blocks = process_pages_file('/path/to/root', 'example_page.json', {}, features_obj, 0.5, loaded_models)
		>>> print(processed_blocks)
		{'block_1': <Block object 1>, 'block_2': <Block object 2>, ...}
	"""	

	page_directory = os.path.join(root_path, 'pages')
	page_file_path = os.path.join(page_directory, page_file_name)
	# Split the path using "-" as the delimiter and get the second element
	year_str = page_file_name.split("-")[1]

	# Convert the extracted year string to an integer
	year = int(year_str)

    # Load JSON file
	with open(page_file_path, 'r', encoding='utf-8') as alto_file:
		alto_json_data = json.load(alto_file)

		new_core_block_name = ''
		for region in alto_json_data.get('r', []):
			coordinates = None   
			coordinates = region.get('c', '')	
			core_block_name = region.get('pOf')
			if new_core_block_name != core_block_name:
				block_index = 1
				new_core_block_name = core_block_name
            
			actual_block_name = f"{core_block_name}-block_{block_index}"
			block_instance = Block(arg=actual_block_name)
			block_instance.page_id = page_file_name
			block_instance.orig_block_id = actual_block_name.split('-block')[0]

			# if block_instance.orig_block_id == region.get('pOf'):
			text_parts_1 = []			
			for para_info in region.get('p', []):

				for line_info in para_info.get('l', []):
					line_text_parts = [text_info.get('tx', '') for text_info in line_info.get('t', [])]
					text_parts_1.extend(line_text_parts)
					text_parts_1.append('\n')

				block_text = " ".join(text_parts_1)

				# Update block instance with coordinates and text
				block_instance.coordinates = coordinates
				block_instance.ocr_ori = block_text
				block_instance.offset_alto = (int(coordinates[0]), int(coordinates[1]))	
				block_instance.year = year

				# Update block_data with the new block instance
				# block_data[unique_block_name] = block_instance
				block_data[actual_block_name] = block_instance

				block_index += 1
						
	if required_epr > -1 and features != None:
		for block_id in block_data:
			block = block_data[block_id]
			block.tokens_ori = features.get_tokens(block.ocr_ori)
			lang_ori, trigrams_ori = features.get_ngrams(block.tokens_ori, block.ocr_ori)
			block.lang_ori = 'de' # assuming german text
			block = features.compute_features_ori(block)
			n_gram_score = features.get_ngram_score(trigrams_ori, models.epr['trigrams'][block.lang_ori])
			x = np.array([block.dict_ori, n_gram_score, block.garbage_ori, features.scale_year(block.year)])
			block.enhance = predict(models.epr, x, models.epr['k'])

	return block_data