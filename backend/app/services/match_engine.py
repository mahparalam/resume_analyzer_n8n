def normalize_skill(skill: str) -> str:
    return skill.strip().lower()


def calculate_skill_match(
    resume_skills: list[str],
    required_skills: list[str],
    preferred_skills: list[str],
):
    resume_skill_set = {
        normalize_skill(skill)
        for skill in resume_skills
    }

    required_skill_set = {
        normalize_skill(skill)
        for skill in required_skills
    }

    preferred_skill_set = {
        normalize_skill(skill)
        for skill in preferred_skills
    }

    matched_required = (
        resume_skill_set & required_skill_set
    )

    matched_preferred = (
        resume_skill_set & preferred_skill_set
    )

    missing_required = (
        required_skill_set - resume_skill_set
    )

    if required_skill_set:
        required_score = (
            len(matched_required)
            / len(required_skill_set)
        ) * 60
    else:
        required_score = 60

    if preferred_skill_set:
        preferred_score = (
            len(matched_preferred)
            / len(preferred_skill_set)
        ) * 20
    else:
        preferred_score = 20

    return {
        "required_score": required_score,
        "preferred_score": preferred_score,
        "matched_required": sorted(matched_required),
        "matched_preferred": sorted(matched_preferred),
        "missing_required": sorted(missing_required),
    }

def calculate_experience_match(
    resume_experience: list,
    required_years: int | None,
):
    if required_years is None:
        return 20, "Not specified"

    total_years = 0

    for experience in resume_experience:
        duration = experience.get("duration")

        if not duration:
            continue

        # We will improve duration parsing later.
        # For now, use simple year detection.
        if "year" in duration.lower():
            try:
                years = float(
                    duration.lower()
                    .split("year")[0]
                    .strip()
                )
                total_years += years
            except ValueError:
                pass

    if total_years >= required_years:
        return 20, "Strong"

    if total_years >= required_years * 0.7:
        return 15, "Good"

    if total_years >= required_years * 0.5:
        return 10, "Partial"

    return 5, "Weak"

def calculate_match(
    resume_skills: list[str],
    resume_experience: list,
    required_skills: list[str],
    preferred_skills: list[str],
    required_years: int | None,
):
    skill_result = calculate_skill_match(
        resume_skills,
        required_skills,
        preferred_skills,
    )

    experience_score, experience_match = (
        calculate_experience_match(
            resume_experience,
            required_years,
        )
    )

    final_score = round(
        skill_result["required_score"]
        + skill_result["preferred_score"]
        + experience_score
    )

    matched_skills = (
        skill_result["matched_required"]
        + skill_result["matched_preferred"]
    )

    missing_skills = skill_result["missing_required"]

    if final_score >= 80:
        recommendation = "APPLY"
    elif final_score >= 60:
        recommendation = "CONSIDER"
    else:
        recommendation = "SKIP"

    return {
        "match_score": final_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "experience_match": experience_match,
        "recommendation": recommendation,
    }