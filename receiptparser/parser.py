import os
import io
import codecs
import pytesseract
from PIL import Image
from wand.image import Image as WandImage
from .receipt import Receipt


def ocr_image(input_file, language, sharpen=False, timeout=20):
    """
    :param input_file: str
        Path to image to prettify
    :return: str
    """
    with io.BytesIO() as transfer:
        with WandImage(filename=input_file) as img:
            if sharpen:
                img.auto_level()
                img.sharpen(radius=0, sigma=4.0)
                img.contrast()
            img.save(transfer)

        with Image.open(transfer) as img:
            return pytesseract.image_to_string(img, lang=language, timeout=20)

def process_receipt(config, filename, sharpen=False, out_dir=None, verbosity=0):
    if filename.endswith('.txt'):
        if verbosity > 0:
            print("Parsing existing OCR result", filename)
        return Receipt.from_file(config, filename)

    if verbosity > 0:
        print("Performing OCR scan on", filename)
    result = ocr_image(filename, config.language, sharpen=sharpen)

    if out_dir:
        basename = os.path.basename(filename)
        out_filename = os.path.join(out_dir, basename+'.txt')
        with codecs.open(out_filename, 'w') as fp:
            fp.write(result)
    else:
        out_filename = None

    return Receipt(config, out_filename or filename, result)
