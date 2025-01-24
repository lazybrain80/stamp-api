import os
import cv2
import uuid
import pickle

from fastapi import File, HTTPException
from motor.core import AgnosticDatabase
from datetime import datetime, timedelta, timezone
from postoffice import text_stamp_func, text_stamp_valid_func
from .common import remove_extension
from db import upload_image_by_path, create_download_url
from bson.binary import Binary
from bson import ObjectId

async def create_blind_text_watermark(
        user: any,
        version: str,
        original_image: File,
        input_watermark: str,
        mongdb: AgnosticDatabase
    ):

    stamp_text_creater = text_stamp_func(version)
    if stamp_text_creater == None:
        raise HTTPException(status_code=400, detail=str("version is not valid."))

    stamped_image, stamp_text,  validater = await stamp_text_creater(original_image, input_watermark)
    
    ######################
    ## save image
    image_id = uuid.uuid4()
    # 파일 확장자 추출
    _, ext = os.path.splitext(original_image.filename)
    ext = ext.lower()
    #image_name = remove_extension(original_image.filename)
    output_filename = f'{image_id}-watermarked{ext}'
    output_path = os.path.join(os.getcwd(), 'wm_image_ground', output_filename)
    cloudinary_path = f"{user['email']}/stamped_by_text"

    try:
        cv2.imwrite(output_path, stamped_image)
        stamped_image_cloudinary  = upload_image_by_path(output_path,
                                                    public_id=remove_extension(output_filename),
                                                    dir_path=cloudinary_path,
                                                    preview=True,
                                                    tags=["stamped", "by_text"]
                                                )
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.remove(output_path)
        pass

    stamp_history = mongdb.get_collection("stamp_history")
    await stamp_history.insert_one({
        "email": user["email"],
        "type": "text",
        "version": version,
        "public_id": stamped_image_cloudinary["public_id"],
        "format": stamped_image_cloudinary["format"],
        "url": stamped_image_cloudinary["image_url"],
        "preview_url": stamped_image_cloudinary["preview_url"],
        "watermark": stamp_text,
        "validater": Binary(
            pickle.dumps(validater)
        ) if validater != None else None,
        "createdAt": datetime.now(timezone.utc)
    })

    return {
        "watermark_text": stamp_text,
        "image_url": create_download_url(
            stamped_image_cloudinary["public_id"],
            stamped_image_cloudinary["format"]
        )
    }


async def valid_text_watermark(
        user: any,
        version: str,
        target_image: File,
        stamp_id: str,
        mongdb: AgnosticDatabase
    ):

    stamp_text_validater = text_stamp_valid_func(version)
    if stamp_text_validater == None:
        raise HTTPException(status_code=400, detail=str("version is not valid."))

    # stamp_history에서 스탬프 정보를 가져옴
    stamp_history = mongdb.get_collection("stamp_history")
    stamp = await stamp_history.find_one({
        "_id": ObjectId(stamp_id),
        "type": "text",
        "validater": {"$ne": None}
    })

    if stamp is None:
        raise HTTPException(status_code=400, detail="Stamp was not found.")

    extracted_stamp = await stamp_text_validater(target_image, pickle.loads(stamp["validater"]))
    ######################
    ## save history
    daily_validation = mongdb.get_collection("daily_validation")
    now_datetime = datetime.now(timezone.utc)
    await daily_validation.insert_one({
        "email": user["email"],
        "type": "text",
        "createdAt": now_datetime,
        "expireAt": (now_datetime + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0)
    })

    validate_history = mongdb.get_collection("validate_history")
    await validate_history.insert_one({
        "email": user["email"],
        "type": "text",
        "version": version,
        "createdAt": now_datetime,
        "expireAt": (now_datetime + timedelta(days=30)).replace(hour=15, minute=0, second=0, microsecond=0)
    })

    return {
        "extracted_watermark": extracted_stamp
    }


