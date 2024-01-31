from enhance.issue_parser import parse_pages_structure
from epr.features_epr import Features
from ocr.pipe.pipe import Models
from enhance.image_cropper import get_images
from enhance.page_parser import process_pages_file
from ocr.pipe.pipe import ocr
import constants.constants as ct
import datetime
import os
import json
import time
import shutil

def incomplete_issue(issue_path: str) -> None:
	"""
	Print a message indicating that the issue was not processed entirely.

	Args:
		issue_path (str): The path of the incomplete issue.

	Returns:
		None

	Example:
		>>> incomplete_issue('/path/to/incomplete/issue')
		Issue not processed entirely: /path/to/incomplete/issue
	"""	
	print('Issue not processed entirely: ' + issue_path)

# # writes out completely processed mets issues
# def add_to_json(blocks, path):
# 	if not os.path.exists(path):
# 		os.makedirs(path)
# 	with open(path+'data.jsonl', "a") as output:
# 		output.write(json.dumps(blocks) + "\n")

# pipeline for processing all the pages of a single issue
def process_package(old_issues_path: str, models: Models, features: Features, required_epr: float) -> None:
	"""
	Pipeline for processing all the pages of a single issue.

	Args:
		old_issues_path (str): Path to the issue directory to be processed.
		models (Models): Object containing the loaded OCR and enhancement prediction models.
		features (Features): Object containing additional features.
		required_epr (float): Enhancement prediction threshold for deciding which textblocks to process.

	Returns:
		None: The function processes the issue pages and writes enhanced results to the directory.

	Raises:
		Any exceptions raised during the processing.

	Note:
		This function processes all the pages of a single issue. It extracts necessary information realated to the issue and 
		pages structure using the "parse_pages_structure" followed by extracting coordinate information and texts for each regions 
		on the pages level using "process_pages_file". For each block inside each page, the enhancement threshold is checked, and if successful, 
		OCR is carried out on the block for enhancement. The new pages with enhanced OCR results are written inside the directory of 
		the issue inside the "enhanced" folder.

	Example:
		>>> process_package('/path/to/issue', models_instance, features_instance, 0.02)
	"""	

	# start clock
	before = int(round(time.time() * 1000))

	# copy package to new destination
	old_package_dir = os.path.dirname(old_issues_path)	
	original_pages_directory = old_package_dir + "/pages"
	copied_pages_directory = old_package_dir + "/enhanced/pages"

	# Delete the existing destination directory
	if os.path.exists(copied_pages_directory):
		shutil.rmtree(copied_pages_directory)	

	shutil.copytree(original_pages_directory, copied_pages_directory)

	blocks_info, n_blocks = parse_pages_structure(old_package_dir)
	ark = os.path.basename(old_issues_path)
	processed_blocks = 0
	if ark == None:
		print("couldn't identify ark in " + old_issues_path)
		incomplete_issue(old_issues_path)
		return
	elif n_blocks == 0:
		print("found 0 blocks for requested types in " + old_issues_path)
		incomplete_issue(old_issues_path)
		return

	# # create json dict for package
	# json_dict = dict()
	# json_dict[ark] = list()

    # Iterate through each JSON file in the directory
	for page_id, file_data in blocks_info.items():
		blocks_stuff = blocks_info[page_id]['blocks']
		blocks_stuff = process_pages_file(old_package_dir, page_id, blocks_stuff, features, required_epr, models)
		# alto_file_path = os.path.join(old_package_dir, page_id)
		copied_alto_file_path = os.path.join(copied_pages_directory, page_id) 

		image_path = blocks_info[page_id]['image']
		blocks_stuff = get_images(image_path, blocks_stuff)
		if blocks_stuff == None:
			incomplete_issue(old_issues_path)
			return
		
		# for every block
		for block_id in blocks_stuff:
			# composed = blocks_stuff[block_id].composed
			rotated = blocks_stuff[block_id].rotated
			text = blocks_stuff[block_id].ocr_ori
			enhance = blocks_stuff[block_id].enhance
			# n_chars_ori = len(text)

			# check conditions for continuing with this block
			if rotated:
				print('ignoring rotated text block: ' + block_id + ' - alto: ' + page_id + ' - ark: ' + ark + ' - mets: ' + old_issues_path)
				continue
			elif text == "":
				print('ignoring empty text block: ' + block_id + ' - alto: ' + page_id + ' - ark: ' + ark + ' - mets: ' + old_issues_path)
				continue

			# # create block dict for data.jsonl
			# block_dict = {
			# 	'blockId': block_id,
			# 	'altoId': page_id,
			# 	'epr': enhance,
			# 	'processed': False,
			# 	'altoPathOri': "./" + alto_file_path,
			# 	'composedBlock': composed,
			# 	'charsOri': n_chars_ori
			# }

			# block is not prcessed because there is no epr model or predicted enhancement is too low
			if enhance != None and enhance < required_epr:
				# json_dict[ark].append(block_dict)
				continue

			# predicted enhancement is high enough: run ocr
			block = ocr(blocks_stuff[block_id], models)

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

	# return json_dict

# aims to enhance pages of the issues by running ocr on a select subset of textblocks only
def improve_pages(issues_directory: str, required_epr: float) -> None:
	"""
	Enhances OCR quality for pages of issues in the specified directory.

	Args:
		issues_directory (str): Path to the directory containing the issues to be enhanced.
		required_epr (float): Enhancement prediction threshold for deciding which textblocks to process.

	Returns:
		None: The function does not return a value but saves enhanced results in a new directory.

	Raises:
		Any exceptions raised during the process_package function.

	Note:
		This function aims to enhance pages of issues by running OCR on a select subset of textblocks only.
		It identifies issues files within the specified directory, loads necessary OCR and enhancement prediction models,
		and processes each issue individually, saving the enhanced results in a new directory.

	Example:
		>>> improve_pages('/path/to/issues', 0.02)
	"""	

	# # save start date
	# date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
	# path = ct.OCR_OUTPUT_PATH + str(date)

    # Check each folder in the issues_directory
	issues_paths = list()
	for folder_name in os.listdir(issues_directory):
		folder_path = os.path.join(issues_directory, folder_name)

		# Check if it is a directory
		if os.path.isdir(folder_path):
			for f in os.listdir(folder_path):
				if f.endswith('.json'):
					json_file_path = os.path.join(folder_path, f)
					issues_paths.append(json_file_path)	
	print('identified all issues files within directory')

	# load models
	models = Models()
	models.load_final_models(True)
	if models.epr == None and required_epr > -1:
		required_epr = -1
		print('no enhancement prediction (epr) model found in models/final/ -> running ocr for all target blocks')

	features = None
	if required_epr > -1:
		features = Features()

	for issue_path in issues_paths:
		issue_path = issue_path.strip()
		# result = process_package(issue_path, models, path, features, required_epr)
		process_package(issue_path, models, features, required_epr)
		# if result != None:
		# 	add_to_json(result, path+ "/new-blocks/")

		print(f"\nenhance completed - new json for pages and blocks are located in {issue_path}/enhanced")
	print("\n Enhancements for all the issues completed")