# Packages
from typing import List
from sqlalchemy.orm import Session
from fastapi.routing import APIRouter
from fastapi import Depends, Response, UploadFile, status

# Modules
from app.utils.exceptions import ExtensionNotAllowed
from app.config import ALLOWED_EXTENSIONS
from app.database import db_instance
from app.models import FilesTable
from app.usecases.files import FilesUsecase

router = APIRouter(prefix="/files")


def validate_content_type(files: List[UploadFile]):
    for file in files:
        extension = file.content_type.split("/")[-1]

        if extension not in ALLOWED_EXTENSIONS:
            raise ExtensionNotAllowed(
                status.HTTP_403_FORBIDDEN,
                f"Extension not allowed. Allowed extensions are {', '.join(ALLOWED_EXTENSIONS)}")


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
        _: None = Depends(validate_content_type),
        db: Session = Depends(db_instance.initialize_session),
        files_usecase: FilesUsecase = Depends(FilesUsecase),
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


@router.get("/{file_id}/paths")
async def get_file_paths(
        response: Response,
        file_id: str,
        db: Session = Depends(db_instance.initialize_session),
        files_usecase: FilesUsecase = Depends(FilesUsecase)
):
    result = files_usecase.get_file_paths(db, file_id, FilesTable)
    response.status_code = result.status_code
    return result
