import os

from fastapi import APIRouter, Query, File, UploadFile, Form, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from controllers import (
    create_blind_text_watermark,
    create_blind_image_watermark,
    valid_text_watermark,
    valid_image_watermark,
    text_watermark_creation_history,
    image_watermark_creation_history,
    valid_text_watermark_history,
    valid_image_watermark_history,
    watermark_dashboard,
    search_user_watermarks,
    stamped_image_download_url,
    delete_watermark
)
from .depends import check_creation_history, check_validation_history
from motor.core import AgnosticDatabase
from db import mongoDB


router = APIRouter(prefix="/filigrana")


@router.delete("")
async def req_delete_watermark(
        request: Request,
        image_type: str = Query(..., description="text or image"),
        image_id: str = Query(..., description="image id"),
        mongdb: AgnosticDatabase = Depends(mongoDB.get_database)
    ):
    try:
        return await delete_watermark(request.state.user, image_type, image_id, mongdb)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/testo", dependencies=[Depends(check_creation_history)])
async def create_text_watermark(
        request: Request,
        file: UploadFile = File(..., description="image file"),
        version: str = Form("text-basic-000", description="text-watermark model version"),
        watermark: str = Form("", description="watermark text"),
        mongdb: AgnosticDatabase = Depends(mongoDB.get_database)
    ):
    
    try:
        return await create_blind_text_watermark(
            request.state.user,
            version,
            file,
            watermark,
            mongdb
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/immagine", dependencies=[Depends(check_creation_history)])
async def create_image_watermark(
        request: Request,
        file: UploadFile = File(..., description="image file"),
        version: str = Form("image-basic-000", description="image-watermark model version"),
        watermark: UploadFile = File(..., description="watermark image file"),
        mongdb: AgnosticDatabase = Depends(mongoDB.get_database)
    ):
    
    try:
        return await create_blind_image_watermark(
            request.state.user,
            version,
            file,
            watermark,
            mongdb
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/corda/testo", dependencies=[Depends(check_validation_history)])
async def validate_text_watermark(
        request: Request,
        file: UploadFile = File(..., description="image file"),
        version: str = Form("text-basic-000", description="text-watermark model version"),
        watermark: str = Form("stamp id", description="stored watermark id"),
        mongdb: AgnosticDatabase = Depends(mongoDB.get_database)
    ):
    try:
        return await valid_text_watermark(request.state.user, version, file, watermark, mongdb)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/corda/immagine", dependencies=[Depends(check_validation_history)])
async def validate_image_watermark(
        request: Request,
        file: UploadFile = File(..., description="image file"),
        version: str = Form("image-basic-000", description="image-watermark model version"),
        watermark: str = Form("stamp id", description="stored watermark id"),
        mongdb: AgnosticDatabase = Depends(mongoDB.get_database)
    ):
    try:
        return await valid_image_watermark(request.state.user, version, file, watermark, mongdb)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/storia/testo")
async def get_text_watermark_creation_history(
        request: Request,
        page: int = Query(1, description="page number"),
        page_size: int = Query(10, description="number of items per page"),
        filter: str = Query("", description="filter by filename or watermark"),
        mongdb: AgnosticDatabase = Depends(mongoDB.get_database)
    ):
    try:
        return await text_watermark_creation_history(request.state.user,
                                            page,
                                            page_size,
                                            filter,
                                            mongdb)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/storia/immagine")
async def get_image_watermark_creation_history(
        request: Request,
        page: int = Query(1, description="page number"),
        page_size: int = Query(10, description="number of items per page"),
        filter: str = Query("", description="filter by filename or watermark"),
        mongdb: AgnosticDatabase = Depends(mongoDB.get_database)
    ):
    try:
        return await image_watermark_creation_history(request.state.user,
                                                page,
                                                page_size,
                                                filter,
                                                mongdb)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/corda/testo/storia")
async def get_text_watermark_validation_history(
        request: Request,
        page: int = Query(1, description="page number"),
        page_size: int = Query(10, description="number of items per page"),
        filter: str = Query("", description="filter by filename or watermark"),
        mongdb: AgnosticDatabase = Depends(mongoDB.get_database)
    ):
    try:
        return await valid_text_watermark_history(request.state.user,
                                            page,
                                            page_size,
                                            filter,
                                            mongdb)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/corda/immagine/storia")
async def get_image_watermark_validation_history(
        request: Request,
        page: int = Query(1, description="page number"),
        page_size: int = Query(10, description="number of items per page"),
        filter: str = Query("", description="filter by filename or watermark"),
        mongdb: AgnosticDatabase = Depends(mongoDB.get_database)
    ):
    try:
        return await valid_image_watermark_history(request.state.user,
                                            page,
                                            page_size,
                                            filter,
                                            mongdb)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/corda/timbro")
async def get_user_watermarks(
        request: Request,
        page: int = Query(1, description="page number"),
        tipo: str = Query("text", description="text or image"),
        mongdb: AgnosticDatabase = Depends(mongoDB.get_database)
    ):
    try:
        return await search_user_watermarks(request.state.user,
                                            page,
                                            tipo,
                                            mongdb)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/corda/scaricare_url")
async def get_stamped_image_download_url(
        request: Request,
        image_id: str = Query("text", description="text or image"),
        mongdb: AgnosticDatabase = Depends(mongoDB.get_database)
    ):
    try:
        return await stamped_image_download_url(request.state.user,
                                            image_id,
                                            mongdb)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cruscotto")
async def get_dashboard_info(
        request: Request,
        mongdb: AgnosticDatabase = Depends(mongoDB.get_database)
    ):
    try:
        return await watermark_dashboard(request.state.user, mongdb)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
