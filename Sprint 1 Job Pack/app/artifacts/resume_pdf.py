from app.artifacts._pdf_utils import render_text_pdf


def render_resume_pdf(resume_text: str) -> bytes:
    return render_text_pdf("Resume", resume_text)
