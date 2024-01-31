import numpy as np

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
		self.page_id = None
		self.ark = None
		self.year = None
		self.lang_ori = None
		self.lang_gt = None
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