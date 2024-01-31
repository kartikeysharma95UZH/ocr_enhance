from ocr.pipe.bin import bin_otsu
from seg.apply_seg import combiseg
from fcr.apply_fcr import predict_font
from ocr.pipe.models import Models
from ocr.pipe.block import Block
from ocr.pipe.pred import Predictor
# from ocr.pipe.alto import generate_alto

# ocr applied on image using models object
def ocr(block: Block, models: Models) -> Block:
	"""
	Apply OCR on an image using models.

	Args:
		block (Block): The Block object containing information about the image and OCR results.
		models (Models): The Models object containing the necessary models for OCR.

	Returns:
		Block: The Block object updated with OCR results.

	Example:
		>>> block = ocr(<Block object>, <Models object>)
		>>> print(block)
		<Updated Block object>
	"""
	# binarization
	bin_image, inv_image = bin_otsu(block.image)
	block.bin_image = bin_image
	block.inv_image = inv_image

	# segmentation
	block.lines = combiseg(block.inv_image)

	# font recognition
	block.font = predict_font(block, models)

	# character recognition
	predictor = Predictor(block, models)
	block = predictor.kraken()
	
	# # alto generation
	# if alto:
	# 	block.ocr_alto = generate_alto(block, addOffset)

	return block