from openai import OpenAI

from app.config import settings
from app.schemas.resume_analysis import ResumeAnalysis

client = OpenAI(api_key=settings.openai_api_key)


def analyze_resume(resume_text: str) -> ResumeAnalysis:

    response = client.responses.parse(
        model=settings.openai_model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are a resume analysis assistant. "
                    "Extract only information supported by the resume. "
                    "Do not invent or assume information. "
                    "If information is missing, return an empty list "
                    "or null where appropriate."
                ),
            },
            {
                "role": "user",
                "content": f"Analyze this resume:\n\n{resume_text}",
            },
        ],
        text_format=ResumeAnalysis,
    )

    return response.output_parsed