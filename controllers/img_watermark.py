import os
import cv2
import pickle
import numpy as np
import uuid

from fastapi import File, HTTPException
from fastapi.responses import StreamingResponse
from motor.core import AgnosticDatabase
from postoffice import image_stamp_func, image_stamp_valid_func
from io import BytesIO
from datetime import datetime, timedelta, timezone
from bson.binary import Binary
from db import upload_image_by_path, create_download_url
from .common import remove_extension, serialize_document
from pymongo import DESCENDING
from bson import ObjectId

async def create_blind_image_watermark(
        user: any,
        version: str,
        original_image: File,
        watermark_image: File,
        mongdb: AgnosticDatabase
    ):

    stamp_image_creater = image_stamp_func(version)
    if stamp_image_creater == None:
        raise HTTPException(status_code=400, detail=str("version is not valid."))
    
    # 파일 확장자 추출
    _, ext = os.path.splitext(original_image.filename)
    original_ext = ext.lower()

    # 파일 확장자 추출
    _, ext = os.path.splitext(watermark_image.filename)
    watermark_ext = ext.lower()

    ## read and tranform to cv2Image type.
    img_file = await original_image.read()
    cv2_original_image = cv2.imdecode(
                        np.frombuffer(img_file, np.uint8),
                        cv2.IMREAD_UNCHANGED
                    ).astype(np.float32)
    img_file = await watermark_image.read()
    cv2_watermark_image = cv2.imdecode(
                        np.frombuffer(img_file, np.uint8),
                        cv2.IMREAD_UNCHANGED
                    ).astype(np.float32)

    validater, stamped_image = await stamp_image_creater(cv2_original_image, cv2_watermark_image)

    image_name = remove_extension(original_image.filename)
    wm_name = remove_extension(watermark_image.filename)

    image_id = uuid.uuid4()
    output_filename = f'{image_id}-watermarked-{image_name}.png'
    wm_filename = f'{image_id}-wm-{wm_name}.png'

    output_path = os.path.join(os.getcwd(), 'wm_image_ground', output_filename)
    wm_path = os.path.join(os.getcwd(), 'wm_image_ground', wm_filename)

    cloudinary_output_path = f"{user['email']}/stamped_by_image"
    cloudinary_wm_path = f"{user['email']}/image_stamp"

    try:
        cv2.imwrite(output_path, stamped_image)
        stamped_image_cloudinary = upload_image_by_path(output_path,
                                                    public_id=remove_extension(output_filename),
                                                    dir_path=cloudinary_output_path,
                                                    preview=True,
                                                    tags=["stamped", "by_image"]
                                                )
            
        cv2.imwrite(wm_path, cv2_watermark_image)
        wm_image_cloudinary = upload_image_by_path(wm_path,
                                    public_id=remove_extension(wm_filename),
                                    dir_path=cloudinary_wm_path,
                                    preview=True
                                )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.remove(output_path)
        os.remove(wm_path)
        pass

    stamp_history = mongdb.get_collection("stamp_history")
    await stamp_history.insert_one({
        "email": user["email"],
        "type": "image",
        "version": version,
        "public_id": stamped_image_cloudinary["public_id"],
        "format": stamped_image_cloudinary["format"],
        "url": stamped_image_cloudinary["image_url"],
        "preview_url": stamped_image_cloudinary["preview_url"],
        "watermark_url": wm_image_cloudinary["image_url"],
        "watermark_preview_url": wm_image_cloudinary["preview_url"],
        "validater": Binary(
            pickle.dumps(validater)
        ),
        "createdAt": datetime.now(timezone.utc)
    })

    return {
            "watermark_text":"",
            "image_url": create_download_url(
                stamped_image_cloudinary["public_id"],
                stamped_image_cloudinary["format"]
            )
        }


async def valid_image_watermark(
        user: any,
        version: str,
        target_image: File,
        stamp_id: str,
        mongdb: AgnosticDatabase
    ):

    stamp_image_validater = image_stamp_valid_func(version)
    if stamp_image_validater == None:
        raise HTTPException(status_code=400, detail=str("version is not valid."))

    # 파일 확장자 추출
    _, ext = os.path.splitext(target_image.filename)
    ext = ext.lower()

    # 이미지 형식에 따른 MIME 타입 설정
    if ext == ".png":
        media_type = "image/png"
    elif ext in [".jpg", ".jpeg"]:
        media_type = "image/jpeg"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    # 검증 대상 이미지를 로컬 디스크에 저장
    image_id = uuid.uuid4()
    target_image_name = f'{image_id}-target-{target_image.filename}'
    target_image_path = os.path.join(os.getcwd(), 'wm_image_ground', target_image_name)
    with open(target_image_path, "wb") as f:
        f.write(await target_image.read())

    # stamp_history에서 스탬프 정보를 가져옴
    stamp_history = mongdb.get_collection("stamp_history")
    stamp = await stamp_history.find_one({
        "_id": ObjectId(stamp_id),
        "type": "image"
    })

    if stamp is None:
        raise HTTPException(status_code=400, detail="Stamp was not found.")
    
    # 스탬프 정보를 이용하여 이미지 스탬프를 추출
    extracted_watermark = await stamp_image_validater(
        target_image,
        pickle.loads(stamp["validater"])
    )

    # 이미지를 메모리 버퍼에 저장
    _, watermark_buffer = cv2.imencode(ext, extracted_watermark)

    ######################
    ## save history
    daily_validation = mongdb.get_collection("daily_validation")
    now_datetime = datetime.now(timezone.utc)
    await daily_validation.insert_one({
        "email": user["email"],
        "type": "image",
        "createdAt": now_datetime,
        "expireAt": (now_datetime + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0)
    })

    validate_history = mongdb.get_collection("validate_history")
    await validate_history.insert_one({
        "email": user["email"],
        "type": "image",
        "version": version,
        "createdAt": now_datetime,
        "expireAt": (now_datetime + timedelta(days=30)).replace(hour=15, minute=0, second=0, microsecond=0)
    })
    
    # 이미지 데이터를 HTTP 응답으로 반환
    return StreamingResponse(
        BytesIO(watermark_buffer),
        media_type=media_type
    )


async def search_user_watermarks(user: any,
        page: int,
        type: str,
        mongdb: AgnosticDatabase):
    stamp_history = mongdb.get_collection("stamp_history")
    page_size = 5
    skip = (page - 1) * page_size

    # 필터 조건 설정
    query = {
        "email": user["email"],
        "type": type,
        "validater": {"$ne": None}
    }
    
    cursor = stamp_history.find(query, {
            "type": 0,
            "url": 0,
            "email": 0,
            "validater": 0,
            "expireAt": 0,
        }).sort("createdAt", DESCENDING).skip(skip).limit(page_size)
    history = await cursor.to_list(length=page_size)

    return [serialize_document(doc) for doc in history]