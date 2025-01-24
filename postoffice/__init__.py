from .text_stamp import stamp_text_basic_000, stamp_text_basic_001
from .text_stamp_valid import text_stamp_valid_basic_000, text_stamp_valid_basic_001

from .image_stamp import stamp_image_basic_000
from .image_stamp_valid import image_stamp_valid_basic_000


text_stamp_funcs = {
    "text-basic-000": stamp_text_basic_000,
    "text-basic-001": stamp_text_basic_001,
}

text_stamp_valid_funcs = {
    "text-basic-000": text_stamp_valid_basic_000,
    "text-basic-001": text_stamp_valid_basic_001,
}

image_stamp_funcs = {
    "image-basic-000": stamp_image_basic_000
}

image_stamp_valid_funcs = {
    "image-basic-000": image_stamp_valid_basic_000
}


def text_stamp_func(version: str):
    if version in text_stamp_funcs:
        return text_stamp_funcs[version]
    return None


def text_stamp_valid_func(version: str):
    if version in text_stamp_valid_funcs:
        return text_stamp_valid_funcs[version]
    return None


def image_stamp_func(version: str):
    if version in image_stamp_funcs:
        return image_stamp_funcs[version]
    return None


def image_stamp_valid_func(version: str):
    if version in image_stamp_valid_funcs:
        return image_stamp_valid_funcs[version]
    return None