from typing import Any

from app.config import get_llm_backend
from app.llm_backends.base import LLMBackend
from app.pipeline.base import Filter


class ParseInputsFilter(Filter):
    """Validates and normalizes the raw job description + candidate profile text."""

    def process(self, context: dict[str, Any]) -> dict[str, Any]:
        job_description = context.get("job_description", "").strip()
        candidate_profile = context.get("candidate_profile", "").strip()

        if not job_description:
            raise ValueError("job_description is required")
        if not candidate_profile:
            raise ValueError("candidate_profile is required")

        context["job_description"] = job_description
        context["candidate_profile"] = candidate_profile
        return context


class BuildPromptsFilter(Filter):
    """Builds the LLM prompts for the résumé, cover letter, and company-fit analysis."""

    def process(self, context: dict[str, Any]) -> dict[str, Any]:
        job_description = context["job_description"]
        candidate_profile = context["candidate_profile"]

        context["resume_prompt"] = (
            "You are a professional resume writer. Using the candidate profile below, "
            "write a tailored resume targeting the given job description. Emphasize the "
            "candidate's experience and skills that match the job. Output plain text only, "
            "no markdown.\n\n"
            f"JOB DESCRIPTION:\n{job_description}\n\n"
            f"CANDIDATE PROFILE:\n{candidate_profile}\n"
        )
        context["cover_letter_prompt"] = (
            "You are a professional cover letter writer. Using the candidate profile below, "
            "write a tailored cover letter for the given job description. Keep it to three or "
            "four paragraphs. Output plain text only, no markdown.\n\n"
            f"JOB DESCRIPTION:\n{job_description}\n\n"
            f"CANDIDATE PROFILE:\n{candidate_profile}\n"
        )
        context["fit_analysis_prompt"] = (
            "Analyze how well the candidate profile fits the job description below. "
            "Respond with exactly five lines, each in the form "
            "'Category: Score/10 - short reason', covering these categories in order: "
            "Skills Match, Experience Level, Domain Knowledge, Culture Fit, Growth Potential. "
            "No other text.\n\n"
            f"JOB DESCRIPTION:\n{job_description}\n\n"
            f"CANDIDATE PROFILE:\n{candidate_profile}\n"
        )
        return context


class CallLLMFilter(Filter):
    """Runs each built prompt through the configured Strategy LLM backend."""

    def __init__(self, backend: LLMBackend | None = None) -> None:
        self.backend = backend or get_llm_backend()

    def process(self, context: dict[str, Any]) -> dict[str, Any]:
        context["resume_text"] = self.backend.generate(context["resume_prompt"])
        context["cover_letter_text"] = self.backend.generate(context["cover_letter_prompt"])
        context["fit_analysis_text"] = self.backend.generate(context["fit_analysis_prompt"])
        return context


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        _, _, text = text.partition("\n")
    if text.endswith("```"):
        text = text[: text.rfind("```")]
    return text.strip()


class PostProcessFilter(Filter):
    """Strips stray markdown code-fence artifacts the LLM sometimes wraps output in."""

    def process(self, context: dict[str, Any]) -> dict[str, Any]:
        for key in ("resume_text", "cover_letter_text", "fit_analysis_text"):
            context[key] = _strip_code_fence(context.get(key, ""))
        return context
