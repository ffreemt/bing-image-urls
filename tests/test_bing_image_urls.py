""" sanity test. """
from bing_image_urls import __version__


def test_version():
    """ test version. """
    assert __version__[:4] == "0.1."
