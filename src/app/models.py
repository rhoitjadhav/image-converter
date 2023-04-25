"""Models for the database"""
from uuid import uuid4
from sqlalchemy.orm import relationship, backref
from sqlalchemy import text as sqlalchemy_text
from sqlalchemy import Column, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.database import db_instance

Base = db_instance.base


def string_uuid():
    return str(uuid4())


class UsersTable(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
    )
    username = Column(Text, nullable=False, unique=True)
    email = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)


class FilesTable(Base):
    __tablename__ = "files"

    id = Column(
        UUID,
        primary_key=True,
        default=string_uuid,
        server_default=sqlalchemy_text("uuid_generate_v4()"),
    )
    name = Column(Text, nullable=False)
    path = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    resolution = Column(Text, nullable=False)
    output_path = Column(Text, nullable=False)
    pdf_id = Column(UUID, ForeignKey("files.id"))
    files = relationship("FilesTable", backref=backref("parent", remote_side="FilesTable.id"))
