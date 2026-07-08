"""
_pptx_compat.py — open .pptx or .potx files with python-pptx.

python-pptx's Presentation() raises ValueError when given a .potx file because
the internal [Content_Types].xml declares the content type as:
  application/vnd.openxmlformats-officedocument.presentationml.template.main+xml

instead of:
  application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml

This module patches that content type in-memory before handing the bytes to
python-pptx, so .potx files are transparently usable everywhere.  It also handles
.potx files that have been renamed to .pptx (the internal bytes still declare
the template content type in that case).
"""

import io
import zipfile
from pathlib import Path

from pptx import Presentation

_POTX_CT = (
    b"application/vnd.openxmlformats-officedocument"
    b".presentationml.template.main+xml"
)
_PPTX_CT = (
    b"application/vnd.openxmlformats-officedocument"
    b".presentationml.presentation.main+xml"
)


def _is_template(raw_zip: bytes) -> bool:
    """Check if a ZIP file contains a .potx content type declaration.

    Must actually decompress [Content_Types].xml because ZIP entries
    are deflated — the raw bytes won't appear in the outer container.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(raw_zip), "r") as zf:
            ct_xml = zf.read("[Content_Types].xml")
            return _POTX_CT in ct_xml
    except (zipfile.BadZipFile, KeyError):
        return False


def open_presentation(path) -> Presentation:
    """Open a PowerPoint file (.pptx or .potx) as a python-pptx Presentation.

    If the file contains a template content type (as .potx files do), the
    content type is patched in-memory so python-pptx accepts it.
    The saved output will always be a valid .pptx file.
    """
    raw = Path(path).read_bytes()

    if not _is_template(raw):
        # Standard .pptx — open normally
        return Presentation(str(path))

    # Template content type detected — rewrite [Content_Types].xml in a new ZIP
    src = io.BytesIO(raw)
    dst = io.BytesIO()

    with zipfile.ZipFile(src, "r") as zin:
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "[Content_Types].xml":
                    data = data.replace(_POTX_CT, _PPTX_CT)
                zout.writestr(item, data)

    dst.seek(0)
    return Presentation(dst)
