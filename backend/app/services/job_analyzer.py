from openai import OpenAI

from app.config import settings
from app.schemas.job_requirement import JobRequirement

client = OpenAI(api_key=settings.openai_api_key)


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

    return response.output_parsed