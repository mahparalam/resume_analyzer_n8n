def build_resume_embedding_text(
    summary: str | None,
    skills: list | None,
    experience: list | None,
    projects: list | None,
) -> str:
    parts = []

    if summary:
        parts.append(f"Summary:\n{summary}")

    if skills:
        parts.append(
            "Skills:\n" + "\n".join(str(skill) for skill in skills)
        )

    if experience:
        parts.append(
            "Experience:\n" + "\n".join(str(item) for item in experience)
        )

    if projects:
        parts.append(
            "Projects:\n" + "\n".join(str(item) for item in projects)
        )

    return "\n\n".join(parts)


def build_job_embedding_text(
    job_title: str | None,
    required_skills: list | None,
    preferred_skills: list | None,
    experience_years: int | None,
    responsibilities: list | None,
) -> str:
    parts = []

    if job_title:
        parts.append(f"Job Title:\n{job_title}")

    if required_skills:
        parts.append(
            "Required Skills:\n"
            + "\n".join(str(skill) for skill in required_skills)
        )

    if preferred_skills:
        parts.append(
            "Preferred Skills:\n"
            + "\n".join(str(skill) for skill in preferred_skills)
        )

    if experience_years is not None:
        parts.append(
            f"Required Experience:\n{experience_years} years"
        )

    if responsibilities:
        parts.append(
            "Responsibilities:\n"
            + "\n".join(str(item) for item in responsibilities)
        )

    return "\n\n".join(parts)