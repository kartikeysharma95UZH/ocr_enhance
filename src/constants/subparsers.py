from enum import Enum
import os

class ParseMode(Enum):
    SINGLE      = 'single'
    PARALLEL    = 'parallel'

    def __str__(self):
        return self.value

def readable_folder(x):
	if not os.path.isdir(x):
		print("Directory does not exist... Checking for s3 config")
	return x

# defines the actions and options stated in the readme file
SUBPARSERS = {

	# args order: short name, long name, required, default, type, action, help

	'enhance': {
		'args': [
			['-d', '--directory', True, None, readable_folder, 'store', 'Path to directory containing all orignal issues along with pages and images'],
			['-r', '--required', False, 0.0, float, 'store', 'Value for minimum required enhancement prediction']
		],
		'func': 'enhance',
	}
}