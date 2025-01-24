from pymongo import DESCENDING
from motor.core import AgnosticDatabase
from datetime import datetime, timedelta, timezone
from .common import serialize_document
from config import basic_license

# 요일 이름 배열
DAYS_OF_WEEK = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def get_week_range():
    # 현재 UTC 시간
    now = datetime.now(timezone.utc)
    # 이번 주 월요일 (주 시작일)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    # 이번 주 일요일 (주 종료일)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    return start_of_week, end_of_week


async def watermark_dashboard(
        user: any,
        mongodb: AgnosticDatabase):
    daily_validation = mongodb.get_collection("daily_validation")
    total_stamp = mongodb.get_collection("stamp_history")
    total_validation = mongodb.get_collection("validate_history")
    
    user_query = {"email": user["email"],}

    validation_count = await daily_validation.count_documents(user_query)
    total_stamp_count = await total_stamp.count_documents(user_query)
    total_validation_count = await total_validation.count_documents(user_query)

    start_of_week, end_of_week = get_week_range()
    
    # 날짜 범위 필터 추가
    week_filter = {
        "createdAt": {
            "$gte": start_of_week,
            "$lte": end_of_week
        }
    }
    
    # 이메일과 날짜 범위 필터를 결합
    stamp_query = {**user_query, **week_filter}
    validation_query = {**user_query, **week_filter}

    pipeline = [
        {"$match": stamp_query},
        {
            "$group": {
                "_id": {"$dayOfWeek": "$createdAt"},
                "count": {"$sum": 1}
            }
        },
        {
            "$addFields": {
                "day": {"$arrayElemAt": [DAYS_OF_WEEK, {"$subtract": ["$_id", 1]}]}
            }
        },
        {"$sort": {"_id": DESCENDING}}
    ]

    weekly_stamp = await total_stamp.aggregate(pipeline).to_list(length=None)
    weekly_validation = await total_validation.aggregate(pipeline).to_list(length=None)
    
    # 기본 요일별 카운트 딕셔너리 초기화
    weekly_stamp_count = {day: 0 for day in DAYS_OF_WEEK}
    weekly_validation_count = {day: 0 for day in DAYS_OF_WEEK}

    # 조회된 결과를 기본 딕셔너리에 병합
    for day in weekly_stamp:
        weekly_stamp_count[day["day"]] = day["count"]
    for day in weekly_validation:
        weekly_validation_count[day["day"]] = day["count"]

    lic_collection = mongodb.get_collection("license_book")
    user_lic = await lic_collection.find_one({"email": user["email"]})
    if user_lic is None:
        user_lic = basic_license

    return {
        "max_creation": user_lic["max_creation"],
        "daily_validation_count": validation_count,
        "total_stamp_count": total_stamp_count,
        "total_validation_count": total_validation_count,
        "weekly_stamp_count": weekly_stamp_count,
        "weekly_validation_count": weekly_validation_count
    }


async def text_watermark_creation_history(
        user: any,
        page: int,
        page_size: int,
        filter: str,
        mongdb: AgnosticDatabase):
    stamp_history = mongdb.get_collection("stamp_history")

    skip = (page - 1) * page_size

    # 필터 조건 설정
    query = {"email": user["email"], "type": "text",}
    if filter:
        filter_query = {
            "$or": [
                {"filename": {"$regex": filter, "$options": "i"}},
                {"watermark": {"$regex": filter, "$options": "i"}}
            ]
        }
        query = {**query, **filter_query}

    cursor = stamp_history.find(query,{
            "type": 0,
            "version": 0,
            "validater": 0,
            "expireAt": 0,
        }).sort("createdAt", DESCENDING).skip(skip).limit(page_size)
    history = await cursor.to_list(length=page_size)

    return [serialize_document(doc) for doc in history]


async def image_watermark_creation_history(
        user: any,
        page: int,
        page_size: int,
        filter: str,
        mongdb: AgnosticDatabase):
    stamp_history = mongdb.get_collection("stamp_history")

    skip = (page - 1) * page_size

    # 필터 조건 설정
    query = {"email": user["email"], "type": "image",}
    if filter:
        filter_query = {
            "$or": [
                {"filename": {"$regex": filter, "$options": "i"}},
            ]
        }
        query = {**query, **filter_query}

    cursor = stamp_history.find(query,{
            "validater": 0,
            "expireAt": 0,
            "url": 0,
        })\
        .sort("createdAt", DESCENDING)\
        .skip(skip)\
        .limit(page_size)
    history = await cursor.to_list(length=page_size)

    return [serialize_document(doc) for doc in history]


async def valid_text_watermark_history(
        user: any,
        page: int,
        page_size: int,
        filter: str,
        mongdb: AgnosticDatabase):
    validate_history = mongdb.get_collection("validate_history")

    skip = (page - 1) * page_size

    # 필터 조건 설정
    query = {"email": user["email"], "type": "text",}
    if filter:
        filter_query = {
            "$or": [
                {"filename": {"$regex": filter, "$options": "i"}},
                {"watermark": {"$regex": filter, "$options": "i"}}
            ]
        }
        query = {**query, **filter_query}

    cursor = validate_history.find(query, {
        "email": 0,
        "type": 0,
        "expireAt": 0,
    }).sort("createdAt", DESCENDING).skip(skip).limit(page_size)
    history = await cursor.to_list(length=page_size)

    return [serialize_document(doc) for doc in history]


async def valid_image_watermark_history(
        user: any,
        page: int,
        page_size: int,
        filter: str,
        mongdb: AgnosticDatabase):
    validate_history = mongdb.get_collection("validate_history")

    skip = (page - 1) * page_size

    # 필터 조건 설정
    query = {"email": user["email"], "type": "image",}
    if filter:
        filter_query = {
            "$or": [
                {"filename": {"$regex": filter, "$options": "i"}},
                {"watermark": {"$regex": filter, "$options": "i"}}
            ]
        }
        query = {**query, **filter_query}

    cursor = validate_history.find(query, {
        "email": 0,
        "type": 0,
        "expireAt": 0,
    }).sort("createdAt", DESCENDING).skip(skip).limit(page_size)
    history = await cursor.to_list(length=page_size)

    return [serialize_document(doc) for doc in history]

