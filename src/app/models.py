"""Models for the database"""
from uuid import uuid4
from sqlalchemy.orm import relationship, backref
from sqlalchemy import text as sqlalchemy_text
from sqlalchemy import Column, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import ChoiceType

from app.database import db_instance

Base = db_instance.base


def string_uuid():
    return str(uuid4())


STATUS_TYPES = [
    ("uploading", "Uploading"),
    ("uploaded", "Uploaded"),
    ("processing", "Processing"),
    ("completed", "Completed"),
    ("failure", "Failure")
]

FILE_TYPE = [
    ("png", "Png"),
    ("jpg", "Jpg"),
    ("jpeg", "Jpeg"),
    ("pdf", "Pdf"),
]


class FilesTable(Base):
    __tablename__ = "files"

    id = Column(
        UUID,
        primary_key=True,
        default=string_uuid,
        server_default=sqlalchemy_text("uuid_generate_v4()"),
    )
    name = Column(Text, nullable=False)
    path = Column(Text)
    type = Column(ChoiceType(FILE_TYPE), nullable=False)
    resolution = Column(Text)
    status = Column(ChoiceType(STATUS_TYPES), nullable=False, default="uploading")
    output_path = Column(Text)
    output_resolution = Column(Text)
    page_num = Column(Text)
    pdf_id = Column(UUID, ForeignKey("files.id"))
    files = relationship("FilesTable", backref=backref("parent", remote_side="FilesTable.id"))
