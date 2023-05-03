# Packages
import base64
import string
import random
from typing import Any, Dict, Optional, AnyStr
from dataclasses import dataclass, field, asdict
from fastapi import UploadFile


@dataclass
class ReturnValue:
    """ReturnValue class is responsible for holding returned value from operations
    Args:
        status: True if operation is successful otherwise False
        status_code: http status code
        message: message after successful operation
        error: error message after failed operation
        data: resulted data after operation completion
    """
    status: bool = True
    status_code: Optional[int] = 200
    message: str = ""
    error: str = ""
    data: Any = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


class Helper:
    @staticmethod
    def generate_random_text(l: int = 6) -> AnyStr:
        """Generate random alphanumeric string
        Args:
            l: length of string. Defaults to 6.
        Returns:
            random string
        """
        return ''.join(random.choices(string.ascii_letters +
                                      string.digits, k=l))

    @staticmethod
    def get_file_extension(file: UploadFile) -> AnyStr:
        return file.content_type.split("/")[-1]

    @staticmethod
    def save_file(file_data: bytes, file_path: str):
        print("save_file:", file_path)
        with open(file_path, "wb+") as fb:
            fb.write(file_data)

    @staticmethod
    def encode_bytes_to_base64_string(data: bytes) -> AnyStr:
        return base64.b64encode(data).decode("utf-8")

    @staticmethod
    def decode_base64_string_to_bytes(data: str) -> bytes:
        return base64.b64decode(data.encode("utf-8"))

    @staticmethod
    def read_file(file_path: str):
        with open(file_path) as file:
            return file.read()

    @staticmethod
    def change_extension(path: str, extension: str):
        name, _ = path.split(".")
        return f"{name}.{extension}"
