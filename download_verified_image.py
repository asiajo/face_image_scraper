import hashlib
import io
import os

import requests
from PIL import Image, UnidentifiedImageError

from get_verified_face import return_verified_face


def download_image_verified(folder_path: str, url: str, search_term: str):
    """
    Downloads image from received url, if it passes basic verification. Does nothing otherwise.

    :param folder_path:  path where the image should be saved
    :param url:          url with the image
    """
    try:
        image_content = requests.get(url).content

    except Exception as e:
        return

    try:
        image = Image.open(io.BytesIO(image_content)).convert('RGB')
        cropped_img = return_verified_face(image)
        if cropped_img is None:
            return
        cropped = cropped_img.convert('RGB')
        file_path = os.path.join(folder_path, search_term + '.jpg')
        with open(file_path, 'wb') as f:
            cropped.save(f, "JPEG", quality=100)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except UnidentifiedImageError:
        return

