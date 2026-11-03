from app.config import settings
from app.schemas.resume_analysis import ResumeAnalysis
from app.services.openai_client import LLMOutputError, client


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

    if response.output_parsed is None:
        raise LLMOutputError("No structured output for the resume")

    return response.output_parsed