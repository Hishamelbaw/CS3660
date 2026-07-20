"""Entry point for the Job Pack generation pipeline. Never imports a
concrete backend directly -- always goes through config.get_llm_backend().
"""
from config import get_llm_backend


def build_job_pack(job_description: str, candidate_profile: str) -> dict:
    backend = get_llm_backend()
    resume_prompt = f"Tailor this resume to the job.\nJOB:\n{job_description}\nPROFILE:\n{candidate_profile}"
    resume_text = backend.generate(resume_prompt)
    return {"resume": resume_text}
