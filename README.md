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
