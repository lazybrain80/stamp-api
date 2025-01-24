import cv2
import numpy as np
import os

from fastapi import File
from .img_division.basic_000 import StampValidater

async def image_stamp_valid_basic_000(
        watermarked_image: File,
        validater: any
    ):
    await watermarked_image.seek(0)
    contents = await watermarked_image.read()
    np_array = np.frombuffer(contents, np.uint8)
    cv2_image_data = cv2.imdecode(np_array, cv2.IMREAD_UNCHANGED).astype(np.float32)

    stamp_machine = StampValidater()
    stamp_machine.prepare(cv2_image_data, validater)
    return stamp_machine.extract_watermark()
    