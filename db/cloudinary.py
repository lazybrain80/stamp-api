import cloudinary
import cloudinary.uploader

from config import cloudinary_config

cloudinary.config(
    cloud_name = cloudinary_config["cloud_name"],
    api_key = cloudinary_config["api_key"],
    api_secret = cloudinary_config["api_secret"],
    secure = cloudinary_config["secure"]
)

EXPIRE_DAYS = cloudinary_config["expire_days"]

def upload_byte_image(io_buf, public_id=None):
    response = cloudinary.uploader.upload(io_buf, resource_type="image", public_id=public_id)
    return response['secure_url']

def upload_image_by_path(file_path, public_id=None, dir_path=None, transform=None, preview=False, tags=None):
    response = cloudinary.uploader.upload(file_path,
                                        resource_type="image",
                                        public_id=public_id,
                                        folder=dir_path,
                                        transformation=transform,
                                        eager=[{
                                            'width': 32, 'height': 32, 'crop': 'scale'
                                        }] if preview == True else None,
                                        tags=tags if tags != None else None,
                                        type = "private"
                                    )

    return {
        "public_id": response['public_id'],
        "image_url": response['secure_url'],
        "preview_url": response['eager'][0]['secure_url'] if preview == True else None,
        "format": response['format'],
    }

# https://cloudinary.com/documentation/control_access_to_media#providing_time_limited_access_to_private_media_assets
def create_download_url(public_id, format):
    return cloudinary.utils.private_download_url(
        public_id=public_id,
        format=format,
        attachment=True)


def remove_stamp_image(public_id):
    return cloudinary.uploader.destroy(public_id, type = "private")
