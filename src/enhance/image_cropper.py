import constants.constants as ct
import cv2
from typing import Dict, Optional
from enhance.page_parser import Block


# crops all images from image file for a set of blocks related to the same page file
def get_images(
    image_path: str, blocks_stuff: Dict[str, Block]
) -> Optional[Dict[str, Block]]:
    """
    Crop images for a set of blocks related to the same page file.

    Args:
        image_path (str): Path to the image file.
        blocks_stuff (Dict[str, Block]): Dictionary containing information about text blocks.

    Returns:
        Optional[Dict[str, Block]]: Updated dictionary containing information about text blocks with cropped images.

    Example:
        >>> updated_blocks = get_images('/path/to/image.jpg', {'block_1': <Block object 1>, 'block_2': <Block object 2>})
        >>> print(updated_blocks)
        {'block_1': <Block object 1>, 'block_2': <Block object 2>, ...}
    """
    image = cv2.imread(image_path)
    if not image is None:
        for block_id in blocks_stuff:
            coords = blocks_stuff[block_id].coordinates
            x = coords[0]
            y = coords[1]
            w = coords[2]
            h = coords[3]
            if x + w > (len(image[0]) + ct.IMG_CROP_TOLERANCE) or y + h > (
                len(image) + ct.IMG_CROP_TOLERANCE
            ):
                print(
                    "image coordinates for block "
                    + block_id
                    + " are out of bounds in image "
                    + image_path
                )
                return
            cropped_image = image[y : y + h, x : x + w]
            blocks_stuff[block_id].image = cropped_image
    else:
        print("couldn't read image at " + image_path)
        return
    return blocks_stuff
