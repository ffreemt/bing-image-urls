# Bing-Image-Urls ![build](https://github.com/ffreemt/bing-image-urls/workflows/build/badge.svg)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/bing-image-urls.svg)](https://badge.fury.io/py/bing-image-urls)

Fetch Bing image urls based on keywords

### Installation
```pip install bing-image-urls```

### Usage

```python

from bing_image_urls import bing_image_urls

print(bing_iamge_urls("bear", limit=2))
# ['https://www.stgeorgeutah.com/wp-content/uploads/2017/01/blackbear.jpg',
# 'http://www.cariboutrailoutfitters.com/wp-content/uploads/2017/03/saskatchewan-black-bear-hunting.jpg']
```

The helper function `get_image_size` may sometimes come handy if you need to know the size of the image. `get_image_size` takes a filename or a filelike object as input and outputs the widht and height of the image. Hence the raw bytes of an image from the net can be wrapped in io.BytesIO and fed to `get_image_size`.

```python
import io
import httpx
from bing_image_urls import get_image_size

url = "https://www.stgeorgeutah.com/wp-content/uploads/2017/01/blackbear.jpg"
try:
    resp = httpx.get(url)
    resp.raise_for_status()
except Exception as exc:
    raise SystemExit(exc)

print(get_image_size(io.BytesIO(resp.content)))
# (1797, 2696)
```

Most the code in `get_image_size` is from [imagesize_py](https://github.com/shibukawa/imagesize_py). As soon as the [PR](https://github.com/shibukawa/imagesize_py/pull/46) about filelike object is merged to the main, the `imagesize_py` package will be included as a depdendant package.
