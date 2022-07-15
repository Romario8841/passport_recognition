import pandas as pd
import pytesseract
import openpyxl

try:
    from PIL import Image
except ImportError:
    import Image


def ocr_core(filename):
    text = pytesseract.image_to_string(Image.open(filename), lang='rus')
    # print(text)
    return text
