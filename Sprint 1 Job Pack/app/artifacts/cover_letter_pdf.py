from app.artifacts._pdf_utils import render_text_pdf


def render_cover_letter_pdf(cover_letter_text: str) -> bytes:
    return render_text_pdf("Cover Letter", cover_letter_text)
