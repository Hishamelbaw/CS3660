import pytest

from app.llm_backends.base import LLMBackend
from app.pipeline.base import Pipeline
from app.pipeline.filters import (
    BuildPromptsFilter,
    CallLLMFilter,
    ParseInputsFilter,
    PostProcessFilter,
)


class StubBackend(LLMBackend):
    """Never touches the network — routes each prompt to canned text by looking
    for a marker phrase unique to BuildPromptsFilter's résumé/cover-letter/fit prompts."""

    def generate(self, prompt: str) -> str:
        if "resume writer" in prompt:
            return "```\nJane Doe - Software Engineer\n```"
        if "cover letter writer" in prompt:
            return "Dear Hiring Manager, ...  "
        return "Skills Match: 8/10 - strong overlap\n..."


def make_pipeline(backend: LLMBackend | None = None) -> Pipeline:
    return Pipeline(
        [
            ParseInputsFilter(),
            BuildPromptsFilter(),
            CallLLMFilter(backend=backend or StubBackend()),
            PostProcessFilter(),
        ]
    )


def test_pipeline_runs_full_chain_and_cleans_output():
    pipeline = make_pipeline()

    result = pipeline.run(
        {
            "job_description": "  Backend engineer, Python, FastAPI.  ",
            "candidate_profile": "  5 years Python, built REST APIs.  ",
        }
    )

    # PostProcessFilter should have stripped the code fence around the resume
    assert result["resume_text"] == "Jane Doe - Software Engineer"
    assert result["cover_letter_text"] == "Dear Hiring Manager, ..."
    assert result["fit_analysis_text"].startswith("Skills Match")

    # BuildPromptsFilter should have produced prompts embedding the (trimmed) inputs
    assert "resume_prompt" in result
    assert "JOB DESCRIPTION" in result["resume_prompt"]
    assert "CANDIDATE PROFILE" in result["resume_prompt"]
    assert "Backend engineer, Python, FastAPI." in result["resume_prompt"]


def test_pipeline_rejects_empty_job_description():
    pipeline = make_pipeline()
    with pytest.raises(ValueError, match="job_description"):
        pipeline.run({"job_description": "  ", "candidate_profile": "x"})


def test_pipeline_rejects_empty_candidate_profile():
    pipeline = make_pipeline()
    with pytest.raises(ValueError, match="candidate_profile"):
        pipeline.run({"job_description": "x", "candidate_profile": "  "})


def test_pipeline_rejects_missing_inputs():
    pipeline = make_pipeline()
    with pytest.raises(ValueError):
        pipeline.run({})
