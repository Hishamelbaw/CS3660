from typing import Any

from app.builders.job_pack_builder import JobPackBuilder


def sample_context() -> dict[str, Any]:
    """Stubbed pipeline output — no LLM backend involved."""
    return {
        "resume_text": "Jane Doe - Software Engineer\n5 years Python, FastAPI, REST APIs.",
        "cover_letter_text": "Dear Hiring Manager,\n\nI am excited to apply.\n\nSincerely,\nJane",
        "fit_analysis_text": (
            "Skills Match: 9/10 - strong Python/FastAPI overlap\n"
            "Experience Level: 7/10 - meets years required\n"
            "Domain Knowledge: 6/10 - some gaps\n"
            "Culture Fit: 8/10 - values align\n"
            "Growth Potential: 8/10 - room to grow"
        ),
    }


def test_builder_produces_valid_resume_pdf():
    job_pack = JobPackBuilder(sample_context()).build()
    assert job_pack.resume_pdf.startswith(b"%PDF")


def test_builder_produces_valid_cover_letter_pdf():
    job_pack = JobPackBuilder(sample_context()).build()
    assert job_pack.cover_letter_pdf.startswith(b"%PDF")


def test_builder_produces_well_formed_infographic_svg():
    job_pack = JobPackBuilder(sample_context()).build()
    svg = job_pack.infographic_svg.strip()

    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    assert "Skills Match" in svg
    assert "9/10" in svg
