import shortuuid
import cv2
import numpy as np

from fastapi import File
from .txt_division.basic_000 import TextWatermarkEncoder, TextWatermarkDecoder
from .text_stamp_common import remove_null_characters, make_fixed_watermark, MAX_BIT_LENGTH

async def stamp_text_basic_000(
    original_image: File,
    input_watermark: str,
):
    ######################
    real_wm = ""
    if not input_watermark:
        real_wm = make_fixed_watermark(f"lazy-{shortuuid.uuid()}")
    else:
        real_wm = make_fixed_watermark(f"lazy-{remove_null_characters(input_watermark)}")

    ######################
    ## read and tranform to cv2Image type.
    contents = await original_image.read()
    np_array = np.frombuffer(contents, np.uint8)
    cv2ImageData = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    ######################
    ## check watermark exist
    decoder = TextWatermarkDecoder(MAX_BIT_LENGTH)
    watermark = decoder.decode(cv2ImageData)

    try:
        wm_extract = watermark.decode('utf-8')
        if wm_extract.startswith('lazy-'):
            raise Exception("이미지에 워터마크가 존재합니다.")
    except UnicodeDecodeError:
        pass
    
    ######################
    ## encode watermark
    encoder = TextWatermarkEncoder(real_wm.encode('utf-8'))
    bgr_encoded = encoder.encode(cv2ImageData)
    
    return bgr_encoded, remove_null_characters(real_wm), None


from .txt_division.basic_001 import StampOperator

async def stamp_text_basic_001(
    original_image: File,
    input_watermark: str,
):
    ######################
    real_wm = ""
    if not input_watermark:
        real_wm = make_fixed_watermark(f"lazy-{shortuuid.uuid()}")
    else:
        real_wm = make_fixed_watermark(f"lazy-{remove_null_characters(input_watermark)}")

    ######################
    ## read and tranform to cv2Image type.
    contents = await original_image.read()
    np_array = np.frombuffer(contents, np.uint8)
    cv2ImageData = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    ######################
    stamper = StampOperator()
    stamped_image, validater = stamper.stamp(cv2ImageData, real_wm)
    return stamped_image, remove_null_characters(real_wm), validater