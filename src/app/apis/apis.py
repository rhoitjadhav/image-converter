# Packages
from fastapi import APIRouter

# Modules
from .files import router as files

router = APIRouter(prefix="/api")

router.include_router(files)
