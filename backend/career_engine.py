
def calculate_career_match(student_skills, required_skills):
    """
    student_skills: {"python": 4, "sql": 2}
    required_skills: {"Python": 5, "SQL": 3}
    """

    if not required_skills:
        return {
            "match_score": 0,
            "strong_skills": [],
            "partial_skills": [],
            "missing_skills": [],
        }

    total_weight = 0
    earned_weight = 0

    strong_skills = []
    partial_skills = []
    missing_skills = []

    # Normalize skill names and proficiency values
    normalized_skills = {
        str(name).strip().lower(): int(level)
        for name, level in student_skills.items()
    }

    for skill_name, importance in required_skills.items():
        weight = max(1, int(importance))
        total_weight += weight

        level = normalized_skills.get(skill_name.strip().lower(), 0)
        level = max(0, min(level, 5))

        earned_weight += weight * level / 5

        if level >= 4:
            strong_skills.append(skill_name)
        elif level >= 1:
            partial_skills.append(skill_name)
        else:
            missing_skills.append(skill_name)

    score = round((earned_weight / total_weight) * 100)

    return {
        "match_score": score,
        "strong_skills": strong_skills,
        "partial_skills": partial_skills,
        "missing_skills": missing_skills,
    }


def rank_careers(student_skills, careers):
    results = []

    for career in careers:
        result = calculate_career_match(
            student_skills,
            career.get("required_skills", {}),
        )

        results.append({
            "id": career.get("id"),
            "career_id": career.get(
                "career_id",
                career.get("id"),
            ),
            "career": career["title"],
            "title": career["title"],
            "description": career.get("description", ""),
            **result,
        })

    return sorted(
        results,
        key=lambda item: item["match_score"],
        reverse=True,
    )
