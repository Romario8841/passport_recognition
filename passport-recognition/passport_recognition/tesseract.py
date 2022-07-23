import pandas as pd
import pytesseract
import openpyxl

try:
    from PIL import Image
except ImportError:
    import Image


def ocr_core(filename):
    text = pytesseract.image_to_string(Image.open(filename), lang='rus')
    return text

def dig_ocr_core(filename):
    digits = pytesseract.image_to_string(Image.open(filename), lang='rus',config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
    return digits
