from dataclasses import dataclass
from typing import Any

from app.artifacts.cover_letter_pdf import render_cover_letter_pdf
from app.artifacts.infographic_svg import render_infographic_svg
from app.artifacts.resume_pdf import render_resume_pdf


@dataclass
class JobPack:
    resume_pdf: bytes
    cover_letter_pdf: bytes
    infographic_svg: str


class JobPackBuilder:
    """Builder: assembles a JobPack (resume PDF, cover letter PDF, infographic SVG)
    step by step from the pipeline's output context."""

    def __init__(self, context: dict[str, Any]) -> None:
        self._context = context
        self._resume_pdf: bytes | None = None
        self._cover_letter_pdf: bytes | None = None
        self._infographic_svg: str | None = None

    def build_resume(self) -> "JobPackBuilder":
        self._resume_pdf = render_resume_pdf(self._context["resume_text"])
        return self

    def build_cover_letter(self) -> "JobPackBuilder":
        self._cover_letter_pdf = render_cover_letter_pdf(self._context["cover_letter_text"])
        return self

    def build_infographic(self) -> "JobPackBuilder":
        self._infographic_svg = render_infographic_svg(self._context["fit_analysis_text"])
        return self

    def build(self) -> JobPack:
        if self._resume_pdf is None:
            self.build_resume()
        if self._cover_letter_pdf is None:
            self.build_cover_letter()
        if self._infographic_svg is None:
            self.build_infographic()
        return JobPack(
            resume_pdf=self._resume_pdf,
            cover_letter_pdf=self._cover_letter_pdf,
            infographic_svg=self._infographic_svg,
        )
