"""
get image size.

Based on image_size_py at github
"""
from typing import Union, Tuple

from pathlib import Path
import io
import re
import struct
from xml.etree import ElementTree


_UNIT_KM = -3
_UNIT_100M = -2
_UNIT_10M = -1
_UNIT_1M = 0
_UNIT_10CM = 1
_UNIT_CM = 2
_UNIT_MM = 3
_UNIT_0_1MM = 4
_UNIT_0_01MM = 5
_UNIT_UM = 6
_UNIT_INCH = 6

_TIFF_TYPE_SIZES = {
    1: 1,
    2: 1,
    3: 2,
    4: 4,
    5: 8,
    6: 1,
    7: 1,
    8: 2,
    9: 4,
    10: 8,
    11: 4,
    12: 8,
}


# pylint: disable=invalid-name, no-else-return, too-many-branches, unused-variable, too-many-statements, too-many-return-statements, no-else-raise, too-many-locals
def _convertToDPI(density, unit):
    if unit == _UNIT_KM:
        return int(density * 0.0000254 + 0.5)
    elif unit == _UNIT_100M:
        return int(density * 0.000254 + 0.5)
    elif unit == _UNIT_10M:
        return int(density * 0.00254 + 0.5)
    elif unit == _UNIT_1M:
        return int(density * 0.0254 + 0.5)
    elif unit == _UNIT_10CM:
        return int(density * 0.254 + 0.5)
    elif unit == _UNIT_CM:
        return int(density * 2.54 + 0.5)
    elif unit == _UNIT_MM:
        return int(density * 25.4 + 0.5)
    elif unit == _UNIT_0_1MM:
        return density * 254
    elif unit == _UNIT_0_01MM:
        return density * 2540
    elif unit == _UNIT_UM:
        return density * 25400
    return density


def _convertToPx(value):
    matched = re.match(r"(\d+)(?:\.\d)?([a-z]*)$", value)
    if not matched:
        raise ValueError("unknown length value: %s" % value)
    else:
        length, unit = matched.groups()
        if unit == "":
            return int(length)
        elif unit == "cm":
            return int(length) * 96 / 2.54
        elif unit == "mm":
            return int(length) * 96 / 2.54 / 10
        elif unit == "in":
            return int(length) * 96
        elif unit == "pc":
            return int(length) * 96 / 6
        elif unit == "pt":
            return int(length) * 96 / 6
        elif unit == "px":
            return int(length)
        else:
            raise ValueError("unknown unit type: %s" % unit)


def get_image_size(filepath: Union[str, Path, io.BytesIO]) -> Tuple[int, int]:
    """
    Return (width, height) for a given img file content

    no requirements

    :type filepath: Union[str, pathlib.Path]
    :rtype Tuple[int, int]
    """
    height = -1
    width = -1

    if isinstance(filepath, io.BytesIO):  # file-like object
        fhandle = filepath
    else:
        fhandle = open(str(filepath), "rb")

    try:
        head = fhandle.read(24)
        size = len(head)
        # handle GIFs
        if size >= 10 and head[:6] in (b"GIF87a", b"GIF89a"):
            # Check to see if content_type is correct
            try:
                width, height = struct.unpack("<hh", head[6:10])
            except struct.error:
                raise ValueError("Invalid GIF file")
        # see png edition spec bytes are below chunk length then and finally the
        elif  size >= 24 and head.startswith(b"\211PNG\r\n\032\n") and head[12:16] == b"IHDR":
            try:
                width, height = struct.unpack(">LL", head[16:24])
            except struct.error:
                raise ValueError("Invalid PNG file")
        # Maybe this is for an older PNG version.
        elif size >= 16 and head.startswith(b"\211PNG\r\n\032\n"):
            # Check to see if we have the right content type
            try:
                width, height = struct.unpack(">LL", head[8:16])
            except struct.error:
                raise ValueError("Invalid PNG file")
        # handle JPEGs
        elif size >= 2 and head.startswith(b"\377\330"):
            try:
                fhandle.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xC0 <= ftype <= 0xCF or ftype in [0xC4, 0xC8, 0xCC]:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xFF:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack(">H", fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack(">HH", fhandle.read(4))
            except struct.error:
                raise ValueError("Invalid JPEG file")
        # handle JPEG2000s
        elif size >= 12 and head.startswith(b"\x00\x00\x00\x0cjP  \r\n\x87\n"):
            fhandle.seek(48)
            try:
                height, width = struct.unpack(">LL", fhandle.read(8))
            except struct.error:
                raise ValueError("Invalid JPEG2000 file")
        # handle big endian TIFF
        elif size >= 8 and head.startswith(b"\x4d\x4d\x00\x2a"):
            offset = struct.unpack(">L", head[4:8])[0]
            fhandle.seek(offset)
            ifdsize = struct.unpack(">H", fhandle.read(2))[0]
            for i in range(ifdsize):
                tag, datatype, count, data = struct.unpack(">HHLL", fhandle.read(12))
                if tag == 256:
                    if datatype == 3:
                        width = int(data / 65536)
                    elif datatype == 4:
                        width = data
                    else:
                        raise ValueError(
                            "Invalid TIFF file: width column data type should be SHORT/LONG."
                        )
                elif tag == 257:
                    if datatype == 3:
                        height = int(data / 65536)
                    elif datatype == 4:
                        height = data
                    else:
                        raise ValueError(
                            "Invalid TIFF file: height column data type should be SHORT/LONG."
                        )
                if width != -1 and height != -1:
                    break
            if width == -1 or height == -1:
                raise ValueError(
                    "Invalid TIFF file: width and/or height IDS entries are missing."
                )
        elif size >= 8 and head.startswith(b"\x49\x49\x2a\x00"):
            offset = struct.unpack("<L", head[4:8])[0]
            fhandle.seek(offset)
            ifdsize = struct.unpack("<H", fhandle.read(2))[0]
            for i in range(ifdsize):
                tag, datatype, count, data = struct.unpack("<HHLL", fhandle.read(12))
                if tag == 256:
                    width = data
                elif tag == 257:
                    height = data
                if width != -1 and height != -1:
                    break
            if width == -1 or height == -1:
                raise ValueError(
                    "Invalid TIFF file: width and/or height IDS entries are missing."
                )
        # handle SVGs
        elif size >= 5 and head.startswith(b"<?xml"):
            try:
                fhandle.seek(0)
                root = ElementTree.parse(fhandle).getroot()
                width = _convertToPx(root.attrib["width"])
                height = _convertToPx(root.attrib["height"])
            except Exception:
                raise ValueError("Invalid SVG file")
    finally:
        fhandle.close()
    return int(width), int(height)
