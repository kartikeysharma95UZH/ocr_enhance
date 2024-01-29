from enhance.json_test import parse_pages_structure
from epr.features_epr import Features
from ocr.pipe.pipe import Models
from enhance.image_cropper import get_images
from enhance.alto_parser import process_alto_file
from ocr.pipe.pipe import ocr
import constants.constants as ct
import datetime
import os
import json
import time
import shutil

def incomplete_mets(mets_path):
	print('mets not processed entirely: ' + mets_path)

# writes out completely processed mets issues
def add_to_json(blocks, path):
	if not os.path.exists(path):
		os.makedirs(path)
	with open(path+'data.jsonl', "a") as output:
		output.write(json.dumps(blocks) + "\n")

# pipeline for processing a single mets/alto package
def process_package(old_mets_path, models, output_path, features, required_epr):

	# start clock
	before = int(round(time.time() * 1000))

	# copy package to new destination
	old_package_dir = os.path.dirname(old_mets_path)	
	original_pages_directory = old_package_dir + "/pages"
	copied_pages_directory = old_package_dir + "/enhanced/pages"

	# Delete the existing destination directory
	if os.path.exists(copied_pages_directory):
		shutil.rmtree(copied_pages_directory)	

	shutil.copytree(original_pages_directory, copied_pages_directory)

	blocks_info, ark, n_blocks = parse_pages_structure(old_package_dir)
	ark = os.path.basename(old_mets_path)
	processed_blocks = 0
	if ark == None:
		print("couldn't identify ark in " + old_mets_path)
		incomplete_mets(old_mets_path)
		return
	elif n_blocks == 0:
		print("found 0 blocks for requested types in " + old_mets_path)
		incomplete_mets(old_mets_path)
		return

	# create json dict for package
	json_dict = dict()
	json_dict[ark] = list()

    # Iterate through each JSON file in the directory
	for alto_id, file_data in blocks_info.items():
		blocks_stuff = blocks_info[alto_id]['blocks']
		blocks_stuff = process_alto_file(old_package_dir, alto_id, blocks_stuff, features, required_epr, models)
		alto_file_path = os.path.join(old_package_dir, alto_id)
		copied_alto_file_path = os.path.join(copied_pages_directory, alto_id) 

		image_path = blocks_info[alto_id]['image']
		blocks_stuff = get_images(image_path, blocks_stuff)
		if blocks_stuff == None:
			incomplete_mets(old_mets_path)
			return
		
		# for every block
		for block_id in blocks_stuff:
			composed = blocks_stuff[block_id].composed
			rotated = blocks_stuff[block_id].rotated
			text = blocks_stuff[block_id].ocr_ori
			enhance = blocks_stuff[block_id].enhance
			n_chars_ori = len(text)

			# check conditions for continuing with this block
			if rotated:
				print('ignoring rotated text block: ' + block_id + ' - alto: ' + alto_id + ' - ark: ' + ark + ' - mets: ' + old_mets_path)
				continue
			elif text == "":
				print('ignoring empty text block: ' + block_id + ' - alto: ' + alto_id + ' - ark: ' + ark + ' - mets: ' + old_mets_path)
				continue

			# create block dict for data.jsonl
			block_dict = {
				'blockId': block_id,
				'altoId': alto_id,
				'epr': enhance,
				'processed': False,
				'altoPathOri': "./" + alto_file_path,
				'composedBlock': composed,
				'charsOri': n_chars_ori
			}

			# block is not prcessed because there is no epr model or predicted enhancement is too low
			if enhance != None and enhance < required_epr:
				json_dict[ark].append(block_dict)
				continue

			# predicted enhancement is high enough: run ocr
			block = ocr(blocks_stuff[block_id], models, alto=True, addOffset=True)

			# Load the JSON file
			with open(copied_alto_file_path, 'r', encoding='utf-8') as json_file:
				json_data = json.load(json_file)

			# Iterate through 'r' entries in the JSON data
			block_index = 1
			for region_entry in json_data.get('r', []):
				pOf_value = region_entry.get('pOf', '')

				if pOf_value == block.orig_block_id:
					# Construct the block_id from the pOf_value and the assumed block index
					block_id = f"{pOf_value}-block_{block_index}"

					# Check if the block_id is present in your 'block' dictionary
					if block.block_id == block_id:
						enhanced_text = block.ocr
						original_text = block.ocr_ori
						predicted_font = block.font
						
						# Add the enhanced text to the JSON data
						region_entry['predicted_font'] = predicted_font
						region_entry['original_text'] = original_text
						region_entry['enhanced_text'] = enhanced_text
						break
					block_index += 1

			# Save the updated JSON data back to the file
			with open(copied_alto_file_path, 'w', encoding='utf-8') as json_file:
				json.dump(json_data, json_file, indent=2, ensure_ascii=False)			

			processed_blocks += 1

	time_needed = int(round(time.time() * 1000))-before
	print(ark + ' processed successfully in ' + str(time_needed) + ' ms (new ocr for ' + str(processed_blocks) + '/' + str(n_blocks) + ' target blocks)')

	return json_dict

# aims to enhance mets/alto by running ocr on a select subset of textblocks only
def improve_alto(mets_directory, required_epr):

	# save start date
	date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
	path = ct.OCR_OUTPUT_PATH + str(date)

	# create mets paths list
	mets_paths = list()
	for root, _, files in os.walk(mets_directory):
		for f in files:
			# if f.endswith('-mets.xml'):
			if f.endswith('-a.json'):
				mets_paths.append(root + '/' + f)
	print('identified all METS files within directory')

	# load models
	models = Models()
	models.load_final_models(True)
	if models.epr == None and required_epr > -1:
		required_epr = -1
		print('no enhancement prediction (epr) model found in models/final/ -> running ocr for all target blocks')

	features = None
	if required_epr > -1:
		features = Features()

	for mets_path in mets_paths:
		mets_path = mets_path.strip()
		result = process_package(mets_path, models, path, features, required_epr)
		if result != None:
			add_to_json(result, path+ "/new-blocks/")

	print("\nenhance completed - new METS/ALTO packages and blocks are located in " + path)