from motor.core import AgnosticDatabase
from fastapi import HTTPException
from db import create_download_url, remove_stamp_image
from bson import ObjectId

async def stamped_image_download_url(
        user: any,
        image_id: str,
        mongdb: AgnosticDatabase
    ):
    stamp_history = mongdb.get_collection("stamp_history")
    stamp = await stamp_history.find_one({
        "email": user["email"],
        "_id": ObjectId(image_id)
    })

    if stamp is None:
        raise HTTPException(status_code=400, detail="Stamp was not found.")

    return { "url": create_download_url(stamp["public_id"], stamp["format"]) }


async def delete_watermark(
        user: any,
        image_type: str,
        image_id: str,
        mongdb: AgnosticDatabase
    ):

    stamp_history = mongdb.get_collection("stamp_history")
    stamp = await stamp_history.find_one({
        "_id": ObjectId(image_id),
        "email": user["email"],
        "type": image_type,
    })

    if stamp is None:
        raise HTTPException(status_code=400, detail="Stamp was not found.")

    # remove image from cloudinary
    removed = remove_stamp_image(stamp['public_id'])
    if removed['result'] != "ok":
        raise HTTPException(status_code=400, detail=f"Failed to delete image from cloud({stamp['public_id']}).")
    
    removed = await stamp_history.delete_one({"_id": stamp["_id"]})
    if removed.deleted_count > 0:
        return { "message": "Stamped image was deleted." }
    else:
        raise HTTPException(status_code=400, detail=f"Failed to delete document({stamp['_id']}).")

    