# Packages
from typing import Union, Dict, List
from sqlalchemy.orm import Session
from fastapi.routing import APIRouter
from fastapi import Request, Depends, Response, Header, UploadFile, status

# Modules
from utils.helper import Helper
from models.books import BooksModel
from db.postgresql_db import get_db
from usecases.books import BooksUsecase
from schemas.books import BooksAddSchema, BooksUpdateSchema

router = APIRouter(prefix="/files")


@router.get("/{file_id}")
async def get_file_by_id():
    pass


@router.post("/upload")
async def upload(files: List[UploadFile]):
    pass
