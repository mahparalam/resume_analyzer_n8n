from app.config import settings
from app.schemas.job_requirement import JobRequirement
from app.services.openai_client import LLMOutputError, client


def analyze_job(job_description: str) -> JobRequirement:

    response = client.responses.parse(
        model=settings.openai_model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are a job description analysis assistant. "
                    "Extract only information explicitly supported by "
                    "the job description. Do not invent requirements. "
                    "Separate required skills from preferred skills. "
                    "If information is missing, return an empty list "
                    "or null where appropriate."
                ),
            },
            {
                "role": "user",
                "content": f"Analyze this job description:\n\n{job_description}",
            },
        ],
        text_format=JobRequirement,
    )

    if response.output_parsed is None:
        raise LLMOutputError("No structured output for the job description")

    return response.output_parsed