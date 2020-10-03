"""
test imagesize.get for filelike object io.BytesIO(raw bytes)

to test:
pytest -k test_get_filelike
"""

from pathlib import Path
from io import BytesIO

# import requests
import httpx

# import tempfile

from bing_image_urls import get_image_size


def test_get_filelike():
    """ test_get_filelike. """

    url = "https://www.tsln.com/wp-content/uploads/2018/10/bears-tsln-101318-3-1240x826.jpg"
    try:
        # response = requests.get(url)
        response = httpx.get(url)
        response.raise_for_status()
    except Exception as exc:
        raise SystemExit(exc)

    file_like = BytesIO(response.content)

    # assert imagesize.get(file_like) == (1240, 826)
    assert get_image_size(file_like) == (1240, 826)


def test_get_filepath():
    """ test_get_filelike. """

    url = "https://www.tsln.com/wp-content/uploads/2018/10/bears-tsln-101318-3-1240x826.jpg"
    try:
        # response = requests.get(url)
        response = httpx.get(url)
        response.raise_for_status()
    except Exception as exc:
        raise SystemExit(exc)

    # tf = tempfile.NamedTemporaryFile()

    Path("get_image_size_test.jpg").write_bytes(response.content)

    # assert imagesize.get(file_like) == (1240, 826)
    assert get_image_size("get_image_size_test.jpg") == (1240, 826)

    Path("get_image_size_test.jpg").unlink()
