from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DraftCreate(BaseModel):
    title: str
    job_description: str
    candidate_profile: str
    backend_used: str
    resume_text: str
    cover_letter_text: str
    infographic_svg: str


class DraftSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    backend_used: str
    created_at: datetime


class DraftDetail(DraftSummary):
    job_description: str
    candidate_profile: str
    resume_text: str
    cover_letter_text: str
    infographic_svg: str


class GenerateRequest(BaseModel):
    job_description: str
    candidate_profile: str


class GenerateResponse(BaseModel):
    backend_used: str
    resume_text: str
    cover_letter_text: str
    fit_analysis_text: str
    infographic_svg: str
    resume_pdf_base64: str
    cover_letter_pdf_base64: str
