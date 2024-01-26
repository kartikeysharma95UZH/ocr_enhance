# from xml.dom.minidom import parse
# from lxml import etree
import constants.constants as ct
import numpy as np
from epr.apply_epr import predict

# adds text and image coordinate information to the text block objects
# def get_block_data(alto_path, blocks_dict, features, required_epr, models):

# 	correct_block = False
# 	counter = 0
# 	block_id = None
# 	tree = None

# 	try:
# 		parser = etree.XMLParser(remove_blank_text=True, encoding='utf-8')
# 		tree = etree.parse(alto_path, parser).getroot()
# 	except:
# 		print('could not parse ALTO file at ' + alto_path)
# 	if tree != None:
# 		etree.indent(tree, space="	")
# 		for e in tree.iter():
# 			if e.tag.endswith('TextBlock') or e.tag.endswith('ComposedBlock'):
# 				block_id = e.get("ID")
# 				if block_id != None and block_id in blocks_dict:
# 					blocks_dict[block_id].ocr_ori = ""
# 					correct_block = True
# 					coords = [e.get("HPOS"), e.get("VPOS"), e.get("WIDTH"), e.get("HEIGHT")]
# 					for c in coords:
# 						try:
# 							val = int(c)
# 							if val < 0:
# 								print('negative integer coordinate detected in ' + alto_path)
# 								return None
# 						except ValueError:
# 							print('non integer coordinate detected in ' + alto_path)
# 							return None
# 					x = int(round(300.0/254.0*float(coords[0])))
# 					y = int(round(300.0/254.0*float(coords[1])))
# 					w = int(round(300.0/254.0*float(coords[2])))
# 					h = int(round(300.0/254.0*float(coords[3])))
# 					coordinates = (x, y, w, h)
# 					blocks_dict[block_id].coordinates = coordinates
# 					blocks_dict[block_id].offset_alto = (int(coords[0]), int(coords[1]))
# 					if e.tag == 'ComposedBlock':
# 						blocks_dict[block_id].composed = True
# 					rotated = e.get('ROTATION')
# 					if rotated != None:
# 						blocks_dict[block_id].rotated = True
# 					counter += 1
# 				else:
# 					correct_block = False
# 			elif e.tag.endswith('TextLine'):
# 				if correct_block:
# 					if blocks_dict[block_id].ocr_ori != "":
# 						blocks_dict[block_id].ocr_ori += '\n'
# 			elif e.tag.endswith('SP'):
# 				if correct_block:
# 						blocks_dict[block_id].ocr_ori += ' '
# 			elif e.tag.endswith('String'):
# 				if correct_block:
# 					new_text = e.get('CONTENT')
# 					if isinstance(new_text, str):
# 						blocks_dict[block_id].ocr_ori += new_text
# 					else:
# 						print('CONTENT missing in ' + alto_path)
# 	if counter != len(blocks_dict):
# 		print('could not find all blocks in ' + alto_path)
# 		return (None, None)

# 	if required_epr > -1 and features != None:
# 		for block_id in blocks_dict:
# 			block = blocks_dict[block_id]
# 			block.tokens_ori = features.get_tokens(block.ocr_ori)
# 			lang_ori, trigrams_ori = features.get_ngrams(block.tokens_ori, block.ocr_ori)
# 			block.lang_ori = lang_ori
# 			if block.lang_ori in ct.SUPPORTED_LANGS and block.lang_ori in models.epr['trigrams']:
# 				block = features.compute_features_ori(block)
# 				n_gram_score = features.get_ngram_score(trigrams_ori, models.epr['trigrams'][block.lang_ori])
# 				x = np.array([block.dict_ori, n_gram_score, block.garbage_ori, features.scale_year(block.year)])
# 				block.enhance = predict(models.epr, x, models.epr['k'])

# 	return (blocks_dict, tree)

import os
import json

import numpy as np

# class grouping all properties related to a single text block
class Block:

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
		self.ocr_alto = None
		self.ocr_ori = None
		self.ocr_gt = None
		self.name = None
		self.score = None
		self.score_ori = None
		self.block_type = None
		self.page_id = None
		self.ark = None
		self.year = None
		self.lang_ori = None
		self.lang_gt = None
		self.composed = False
		self.rotated = False
		self.coordinates = None
		self.offset_alto = None
		self.tokens_ori = None
		self.tokens_gt = None
		self.dict_ori = None
		self.garbage_ori = None
		self.trigrams_gt = None
		self.trigrams_ori = None
		self.enhance = None

	# returns a string version of the ocr output of the block
	def __str__(self):
		return_str = ""
		if self.ocr != None:
			if self.name != None:
				return_str += self.name + ':\n'
			for i, line in enumerate(self.ocr.split('\n')):
				return_str += str(i+1) + ':\t' + line + '\n'
		return return_str

def process_alto_file(root_path, alto_file_name, block_data, features, required_epr, models):
	alto_directory = os.path.join(root_path, 'pages')
	alto_file_path = os.path.join(alto_directory, alto_file_name)
	# Split the path using "-" as the delimiter and get the second element
	year_str = alto_file_name.split("-")[1]

	# Convert the extracted year string to an integer
	year = int(year_str)

    # Load JSON file
	with open(alto_file_path, 'r', encoding='utf-8') as alto_file:
		alto_json_data = json.load(alto_file)

        # Iterate through each block in the file_data
		# for block_name, block_info in block_data.get('blocks', {}).items():
		# for block_name in block_data:

		# 	block_instance = Block(arg=block_name)
		# 	block_instance.page_id = alto_file_name
		# 	block_instance.year = year
		# 	block_instance.orig_block_id = block_name.split('-block')[0]

		# 	coordinates = None
		# 	text_parts_1 = []

		# block_index = 1
		new_core_block_name = ''
		for region in alto_json_data.get('r', []):
			coordinates = None   
			coordinates = region.get('c', '')
			# x = int(round(300.0/254.0*float(coordinates[0])))
			# y = int(round(300.0/254.0*float(coordinates[1])))
			# w = int(round(300.0/254.0*float(coordinates[2])))
			# h = int(round(300.0/254.0*float(coordinates[3])))
			# coordinates = (x, y, w, h)	

			core_block_name = region.get('pOf')
			if new_core_block_name != core_block_name:
				block_index = 1
				new_core_block_name = core_block_name
            
			actual_block_name = f"{core_block_name}-block_{block_index}"
			block_instance = Block(arg=actual_block_name)
			block_instance.page_id = alto_file_name
			block_instance.orig_block_id = actual_block_name.split('-block')[0]

			# if block_instance.orig_block_id == region.get('pOf'):
			text_parts_1 = []			
			for para_info in region.get('p', []):

				for line_info in para_info.get('l', []):
					line_text_parts = [text_info.get('tx', '') for text_info in line_info.get('t', [])]
					text_parts_1.extend(line_text_parts)
					text_parts_1.append('\n')

				# paragraph_text = " ".join(text_parts_1)
				block_text = " ".join(text_parts_1)
				# unique_block_name = f"{block_instance.orig_block_id}-block_{block_index}"

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
			block.lang_ori = lang_ori
			if block.lang_ori in ct.SUPPORTED_LANGS and block.lang_ori in models.epr['trigrams']:
				block = features.compute_features_ori(block)
				n_gram_score = features.get_ngram_score(trigrams_ori, models.epr['trigrams'][block.lang_ori])
				x = np.array([block.dict_ori, n_gram_score, block.garbage_ori, features.scale_year(block.year)])
				block.enhance = predict(models.epr, x, models.epr['k'])

	return block_data