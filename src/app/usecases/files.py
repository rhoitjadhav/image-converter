# Packages
import os
from typing import List, Type, Dict
from sqlalchemy.orm import Session
from fastapi import UploadFile, status
from fastapi.encoders import jsonable_encoder
from wand.image import Image

# Modules
from app.workers.tasks import upload_file, convert_to_png
from app.models import FilesTable
from app.utils.helper import ReturnValue, Helper
from app.utils.wand_helper import WandHelper
from app.config import STATIC_FILES_DIR


class FilesUsecase:
    """
    This class implements files related use cases
    """

    @staticmethod
    def _upload_images(
            db: Session,
            file: UploadFile,
            file_model: Type[FilesTable]
    ) -> Dict:
        """
        Upload images (png, jpeg, etc.) and convert them into png with
        configured resolution.

        Args:
            db: sqlalchemy instance
            file: UploadFile instance
            file_model: FilesTable instance

        Returns:
            dict: a dictionary of filename, new_filename and file_id
        """
        filename = f"{Helper.generate_random_text()}_{file.filename}"
        file_path = os.path.join(STATIC_FILES_DIR, filename)
        file_data = file.file.read()

        file_type = Helper.get_file_extension(file)
        resolution = WandHelper.get_resolution(file_data)
        file_ = file_model(name=filename, type=file_type,
                           resolution=resolution)
        db.add(file_)
        db.commit()
        db.refresh(file_)
        file_id = file_.id

        # Celery task
        upload_file.apply_async(
            (file_id, Helper.encode_bytes_to_base64_string(file_data), file_path),
            link=convert_to_png.si(file_id)
        )
        return {"filename": file.filename, "new_filename": filename, "file_id": file_id}

    @staticmethod
    def _upload_pdf_file(
            db: Session,
            file: UploadFile,
            file_model: Type[FilesTable]
    ) -> List:
        """
        Upload pdf file and convert extracted images into png with
        configured resolution.

        Args:
            db: sqlalchemy instance
            file: UploadFile instance
            file_model: FilesTable instance

        Returns:
            list: list of dictionaries containing filename, new_filename and file_id
        """
        files_id = []
        pdf_filename = f"{Helper.generate_random_text()}_{file.filename}"
        file_path = os.path.join(STATIC_FILES_DIR, pdf_filename)
        file_data = file.file.read()

        file_type = Helper.get_file_extension(file)
        file_ = file_model(name=pdf_filename, type=file_type)
        db.add(file_)
        db.commit()
        db.refresh(file_)
        pdf_file_id = file_.id
        files_id.append({"filename": file.filename,
                         "new_filename": pdf_filename,
                         "file_id": pdf_file_id})

        # Celery task
        upload_file.apply_async(
            (pdf_file_id, Helper.encode_bytes_to_base64_string(file_data), file_path)
        )

        with Image(blob=file_data) as pdf:
            images = pdf.sequence
            for i, image in enumerate(images):
                filename = f"{pdf_filename.split('.pdf')[0]}_image_{i + 1}.png"
                file_path = os.path.join(STATIC_FILES_DIR, filename)
                file_data = WandHelper.get_blob(image)
                resolution = f"{int(image.resolution[0])}x{int(image.resolution[1])}"
                file_ = file_model(name=filename, type="png",
                                   resolution=resolution, page_num=i + 1,
                                   pdf_id=pdf_file_id)
                db.add(file_)
                db.commit()
                db.refresh(file_)
                file_id = file_.id
                files_id.append({"filename": None, "new_filename": filename, "file_id": file_id})

                # call celery task here for images
                upload_file.apply_async(
                    (file_id, Helper.encode_bytes_to_base64_string(file_data), file_path),
                    link=convert_to_png.si(file_id)
                )

        return files_id

    @staticmethod
    def get_file_by_id(
            db: Session,
            file_id: str,
            file_model: Type[FilesTable]
    ) -> ReturnValue:
        """
        Get file details by id
        Args:
            db: sqlalchemy instance
            file_id: file id
            file_model: FilesTable instance

        Returns:
            ReturnValue: file details
        """

        file = db.query(file_model).filter(file_model.id == file_id).first()
        if not file:
            return ReturnValue(False, status.HTTP_404_NOT_FOUND, "File not found")

        data = jsonable_encoder(file)
        if file.type == "pdf":
            images = db.query(file_model).filter(file_model.pdf_id == file.id).all()
            data["images"] = jsonable_encoder(images)

        return ReturnValue(data=data)

    @staticmethod
    def get_file_status(
            db: Session,
            file_id: str,
            file_model: Type[FilesTable]
    ) -> ReturnValue:
        """
        Get file status
        Args:
            db: sqlalchemy instance
            file_id: file id
            file_model: FilesTable instance

        Returns:
            ReturnValue: file status
        """

        file = db.query(file_model).filter(file_model.id == file_id).first()
        if not file:
            return ReturnValue(False, status.HTTP_404_NOT_FOUND, "File not found")

        return ReturnValue(data=jsonable_encoder(file.status))

    def upload(
            self,
            db: Session,
            files: List[UploadFile],
            file_model: Type[FilesTable]
    ) -> ReturnValue:
        """
        Upload list of files
        Args:
            db: sqlalchemy instance
            files: list of UploadFile instance
            file_model: FilesTable instance

        Returns:
            ReturnValue: list of files id after added into db
        """
        files_id = []
        for file in files:
            if "pdf" in file.content_type:
                file_ids = self._upload_pdf_file(db, file, file_model)
                files_id.extend(file_ids)
            else:
                file_id = self._upload_images(db, file, file_model)
                files_id.append(file_id)

        if not files_id:
            return ReturnValue(False, status.HTTP_422_UNPROCESSABLE_ENTITY, "Please select files to upload")

        return ReturnValue(True, status.HTTP_200_OK, "File is uploaded", data=files_id)
