from fastapi import Request, HTTPException
from db import mongoDB
from config import basic_license


async def check_validation_history(request: Request):
    mongodb = await mongoDB.get_database()
    user = request.state.user

    lic_collection = mongodb.get_collection("license_book")
    user_lic = await lic_collection.find_one({"email": user["email"]})
    if user_lic is None:
        user_lic = basic_license

    history_collection = mongodb.get_collection("daily_validation")
    total_creation = await history_collection.count_documents({"email": user["email"]})

    if total_creation >= user_lic["max_validation"]:
        raise HTTPException(status_code=400, detail="Exceed maximum creation limit")
    pass