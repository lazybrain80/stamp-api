import cv2
import numpy as np

from fastapi import File
from .txt_division.basic_000 import TextWatermarkDecoder
from .text_stamp_common import remove_null_characters, make_fixed_watermark, MAX_BIT_LENGTH

async def text_stamp_valid_basic_000(
        target_image: File,
    ):
    contents = await target_image.read()
    np_array = np.frombuffer(contents, np.uint8)

    decoder = TextWatermarkDecoder(MAX_BIT_LENGTH)
    watermark = decoder.decode(cv2.imdecode(np_array, cv2.IMREAD_COLOR))

    watermark = watermark.decode('utf-8', errors='ignore')

    watermark = remove_null_characters(watermark)

    if watermark == '':
        raise ValueError("No watermark found")
    
    return watermark

from .txt_division.basic_001 import StampValidator

async def text_stamp_valid_basic_001(
        target_image: File,
        validater: any,
    ):

    contents = await target_image.read()
    np_array = np.frombuffer(contents, np.uint8)

    stampValider = StampValidator()
    extracted_txt = stampValider.validate(cv2.imdecode(np_array, cv2.IMREAD_COLOR), MAX_BIT_LENGTH, validater)
    extracted_txt = remove_null_characters(extracted_txt)

    if extracted_txt == '':
        raise ValueError("No watermark found")
    
    return extracted_txt
