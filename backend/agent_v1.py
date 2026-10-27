def generate_career_advice(student_skills, career_recommendations):
    """
    Rule-based AI Agent V1.
    Analyzes student skills and career matches,
    then provides simple next-step advice.
    """

    if not career_recommendations:
        return {
            "message": "No career recommendations available yet.",
            "suggestions": [
                "Add your skills to your profile.",
                "Make sure career and required-skill data is available."
            ]
        }

    best_career = career_recommendations[0]

    missing_skills = best_career.get("missing_skills", [])
    partial_skills = best_career.get("partial_skills", [])

    suggestions = []

    if missing_skills:
        suggestions.append(
            "Start learning these missing skills: "
            + ", ".join(missing_skills[:3])
        )

    if partial_skills:
        suggestions.append(
            "Improve your existing skills: "
            + ", ".join(partial_skills[:3])
        )

    if not suggestions:
        suggestions.append(
            "Continue practicing your skills and build a project "
            "related to your target career."
        )

    return {
        "message": "Career advice generated successfully.",
        "recommended_career": best_career.get("career"),
        "match_score": best_career.get("match_score", 0),
        "suggestions": suggestions
    }