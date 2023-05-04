# Packages
from typing import AnyStr
from wand.image import Image
from wand.sequence import SingleImage, Sequence


class WandHelper:
    """
    Helper class for Wand library
    """

    @staticmethod
    def get_resolution(file: bytes) -> AnyStr:
        """
        Get resolution of file
        Args:
            file: contents of file

        Returns:
            AnyStr: resolution of file (e.g. 100x100)
        """
        with Image(blob=file) as img:
            return f"{int(img.resolution[0])}x{int(img.resolution[1])}"

    @staticmethod
    def pdf_to_image(file: bytes) -> Sequence:
        """
        Extract images from pdf

        Args:
            file: contents of pdf file

        Returns:
            Sequence: list of images
        """
        with Image(blob=file) as img:
            return img.sequence

    @staticmethod
    def get_blob(
            image: SingleImage,
            fmt: str = "png",
            resolution: str = None,
    ) -> bytes:
        """
        Get blob contents of file

        Args:
            image: SingleImage instance
            fmt: format of blob
            resolution: resolution

        Returns:
             bytes: blob contents of file
        """
        with Image(image) as img:
            if resolution:
                img.resolution = list(map(int, resolution.split("x")))
            return img.make_blob(fmt)

    @staticmethod
    def convert_to_png(
            file_path: str,
            new_file_path: str,
            resolution: str = None
    ) -> None:
        """
        Convert file into png format and its resolution
        Args:
            file_path: path of file
            new_file_path: new path of file
            resolution: resolution
        """

        with Image(filename=file_path) as img:
            if resolution:
                img.resolution = list(map(int, resolution.split("x")))

            img.save(filename=new_file_path)
