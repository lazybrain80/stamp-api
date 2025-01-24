from .mongodb import MongoAccessor
from .cloudinary import upload_byte_image, upload_image_by_path, create_download_url, remove_stamp_image

mongoDB = MongoAccessor()
