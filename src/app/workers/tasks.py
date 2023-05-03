# Packages
import os
from typing import Type
import logging
import asyncio
from fastapi import status
from sqlalchemy.orm import Session

# Modules
from app.config import CONVERTED_IMAGE_RESOLUTION
from app.utils.helper import ReturnValue, Helper
from app.utils.wand_helper import WandHelper
from app.models import FilesTable
from app.workers.celery import celery_app, BaseDbTask, loop


class Tasks:
    @staticmethod
    async def run_async_test_task(session: Session):
        # session is the db session from sqlalchemy
        logging.info("Entering test task (next message will appear in 5 seconds)")
        await asyncio.sleep(5)
        logging.info("Exiting test task")

    @staticmethod
    async def run_upload_file(
            db: Session,
            file_model: Type[FilesTable],
            file_id: str,
            file_data: bytes,
            file_path: str,
    ):
        file_ = db.query(file_model).filter(file_model.id == file_id).one()
        if not file_:
            logging.error(f"File {file_id} not found in database")
            return ReturnValue(False, status.HTTP_404_NOT_FOUND,
                               f"File {file_id} not found in database")

        # Uploading
        Helper.save_file(file_data, file_path)
        file_.status = "uploaded"
        file_.path = file_path
        db.commit()
        return file_id

    @staticmethod
    async def run_convert_to_png(
            db: Session,
            file_model: Type[FilesTable],
            file_id: str
    ):
        file = db.query(file_model).filter(file_model.id == file_id).one()
        if not file:
            logging.error(f"File {file_id} not found in database")
            return ReturnValue(False, status.HTTP_404_NOT_FOUND,
                               f"File {file_id} not found in database")

        # Change status to processing
        file.status = "processing"
        db.commit()

        # Conversion
        file_path = file.path
        new_file_path = f"{file_path.split('.')[0]}_converted.png"
        resolution = CONVERTED_IMAGE_RESOLUTION
        WandHelper.convert_to_png(file_path, new_file_path, resolution)

        file.output_path = new_file_path
        file.output_resolution = resolution
        file.status = "completed"
        db.commit()
        return file_id


@celery_app.task(
    bind=True,
    max_retries=3,
    acks_late=True,
    base=BaseDbTask,
    retry_jitter=True,
    retry_backoff=True,
    default_retry_delay=5,
    reject_on_worker_lost=True,
)
def run_test_task(self):
    try:
        # Example of async task running within celery
        loop.run_until_complete(Tasks.run_async_test_task(self.session))
    except Exception as exc:
        logging.exception("exception while running task. retrying")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    max_retries=3,
    acks_late=True,
    base=BaseDbTask,
    retry_jitter=True,
    retry_backoff=True,
    default_retry_delay=5,
    reject_on_worker_lost=True,
)
def upload_file(
        self,
        file_id: str,
        file_data_str: str,
        file_path: str
):
    try:
        # Example of async task running within celery
        file_data = Helper.decode_base64_string_to_bytes(file_data_str)
        loop.run_until_complete(Tasks.run_upload_file(
            self.session, FilesTable,
            file_id, file_data, file_path
        ))
    except Exception as exc:
        logging.exception("exception while running upload_file task. retrying")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    max_retries=3,
    acks_late=True,
    base=BaseDbTask,
    retry_jitter=True,
    retry_backoff=True,
    default_retry_delay=5,
    reject_on_worker_lost=True,
)
def convert_to_png(self, file_id: str):
    try:
        # Example of async task running within celery
        loop.run_until_complete(Tasks.run_convert_to_png(
            self.session, FilesTable, file_id
        ))
    except Exception as exc:
        logging.exception("exception while running upload_file task. retrying")
        raise self.retry(exc=exc)
