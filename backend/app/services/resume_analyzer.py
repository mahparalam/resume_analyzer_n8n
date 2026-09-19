import os

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.resume_analysis import ResumeAnalysis

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_resume(resume_text: str) -> ResumeAnalysis:

    response = client.responses.parse(
        model="gpt-5.6-luna",
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