# Packages
from typing import List
from wand.image import Image
from wand.sequence import SingleImage


class WandHelper:
    @staticmethod
    def get_resolution(file: bytes):
        with Image(blob=file) as img:
            return f"{int(img.resolution[0])}x{int(img.resolution[1])}"

    @staticmethod
    def pdf_to_image(file: bytes):
        with Image(blob=file) as img:
            return img.sequence

    @staticmethod
    def get_blob(
            image: SingleImage,
            fmt: str = "png",
            resolution: str = None,
    ):
        with Image(image) as img:
            if resolution:
                img.resolution = list(map(int, resolution.split("x")))
            return img.make_blob(fmt)

    @staticmethod
    def convert_to_png(
            file_path: str,
            new_file_path: str,
            resolution: str = None
    ):
        print(file_path)
        print(new_file_path)
        with Image(filename=file_path) as img:
            if resolution:
                img.resolution = list(map(int, resolution.split("x")))

            img.save(filename=new_file_path)
