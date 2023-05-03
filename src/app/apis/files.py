# Packages
from typing import List
from sqlalchemy.orm import Session
from fastapi.routing import APIRouter
from fastapi import Depends, Response, UploadFile

# Modules
from app.database import db_instance
from app.models import FilesTable
from app.usecases.files import FilesUsecase

router = APIRouter(prefix="/files")


@router.get("/{file_id}")
async def get_file_by_id(
        response: Response,
        file_id: str,
        db: Session = Depends(db_instance.initialize_session),
        files_usecase: FilesUsecase = Depends(FilesUsecase)
):
    result = files_usecase.get_file_by_id(db, file_id, FilesTable)
    response.status_code = result.status_code
    return result


@router.post("/upload")
async def upload(
        response: Response,
        files: List[UploadFile],
        db: Session = Depends(db_instance.initialize_session),
        files_usecase: FilesUsecase = Depends(FilesUsecase)
):
    result = files_usecase.upload(db, files, FilesTable)
    response.status_code = result.status_code
    return result


@router.get("/{file_id}/status")
async def get_file_status(
        response: Response,
        file_id: str,
        db: Session = Depends(db_instance.initialize_session),
        files_usecase: FilesUsecase = Depends(FilesUsecase)
):
    result = files_usecase.get_file_status(db, file_id, FilesTable)
    response.status_code = result.status_code
    return result
