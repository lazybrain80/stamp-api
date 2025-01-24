import os
import cv2

def remove_extension(filename):
    return os.path.splitext(filename.replace(" ","_"))[0]


def resize_image(image, max_width=128, max_height=128):
    height, width = image.shape[:2]
    if width > max_width or height > max_height:
        # 비율을 유지하면서 리사이즈
        scaling_factor = min(max_width / width, max_height / height)
        new_size = (int(width * scaling_factor), int(height * scaling_factor))
        resized_image = cv2.resize(image, new_size)
        return resized_image
    return image


def serialize_document(doc):
    doc["_id"] = str(doc["_id"])
    return doc