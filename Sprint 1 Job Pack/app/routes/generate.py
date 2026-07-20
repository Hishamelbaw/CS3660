import base64
import os

from fastapi import APIRouter, HTTPException

from app.builders.job_pack_builder import JobPackBuilder
from app.config import get_llm_backend
from app.pipeline.base import Pipeline
from app.pipeline.filters import (
    BuildPromptsFilter,
    CallLLMFilter,
    ParseInputsFilter,
    PostProcessFilter,
)
from app.schemas import GenerateRequest, GenerateResponse

router = APIRouter(prefix="/api", tags=["generate"])


@router.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    backend = get_llm_backend()
    pipeline = Pipeline(
        [
            ParseInputsFilter(),
            BuildPromptsFilter(),
            CallLLMFilter(backend=backend),
            PostProcessFilter(),
        ]
    )

    try:
        context = pipeline.run(
            {
                "job_description": req.job_description,
                "candidate_profile": req.candidate_profile,
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    job_pack = JobPackBuilder(context).build()

    return GenerateResponse(
        backend_used=os.environ.get("LLM_BACKEND", "hosted_ollama"),
        resume_text=context["resume_text"],
        cover_letter_text=context["cover_letter_text"],
        fit_analysis_text=context["fit_analysis_text"],
        infographic_svg=job_pack.infographic_svg,
        resume_pdf_base64=base64.b64encode(job_pack.resume_pdf).decode("ascii"),
        cover_letter_pdf_base64=base64.b64encode(job_pack.cover_letter_pdf).decode("ascii"),
    )
