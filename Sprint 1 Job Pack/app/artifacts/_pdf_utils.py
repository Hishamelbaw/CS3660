import io
import textwrap

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

_MARGIN = 0.75 * inch
_FONT_NAME = "Helvetica"
_FONT_SIZE = 10
_LEADING = 14
_WRAP_WIDTH = 95


def render_text_pdf(heading: str, body: str) -> bytes:
    """Renders a heading + plain-text body as a simple paginated PDF."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    page_width, page_height = LETTER
    y = page_height - _MARGIN

    c.setFont("Helvetica-Bold", 16)
    c.drawString(_MARGIN, y, heading)
    y -= _LEADING * 2

    c.setFont(_FONT_NAME, _FONT_SIZE)
    for paragraph in body.splitlines():
        lines = textwrap.wrap(paragraph, _WRAP_WIDTH) or [""]
        for line in lines:
            if y < _MARGIN:
                c.showPage()
                c.setFont(_FONT_NAME, _FONT_SIZE)
                y = page_height - _MARGIN
            c.drawString(_MARGIN, y, line)
            y -= _LEADING

    c.save()
    return buffer.getvalue()
