from enum import Enum
import argparse
import os
import sys

class ParseMode(Enum):
    SINGLE      = 'single'
    PARALLEL    = 'parallel'

    def __str__(self):
        return self.value

def readable_file(x):
	if not os.path.isfile(x):
		raise argparse.ArgumentTypeError('{} does not exist'.format(x))
	return x

def readable_folder(x):
	if not os.path.isdir(x):
		raise argparse.ArgumentTypeError('{} does not exist'.format(x))
	return x

def print_kvp(dictionary):
	print('Parameters:')
	for k, v in dictionary.items():
		print(' > {:15} : {}'.format(k,v))

# defines the actions and options stated in the readme file
SUBPARSERS = {

	# args order: short name, long name, required, default, type, action, help

	'enhance': {
		'args': [
			['-d', '--directory', True, None, readable_folder, 'store', 'Path to directory containing all orignal METS/ALTO packages'],
			['-r', '--required', False, 0.0, float, 'store', 'Value for minimum required enhancement prediction']
		],
		'func': 'enhance',
	}
}