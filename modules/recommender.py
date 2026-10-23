from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CAREERS_FILE = PROJECT_ROOT / "data" / "careers.csv"


def load_careers():
    """Load and validate the career dataset."""
    if not CAREERS_FILE.exists():
        raise FileNotFoundError(
            f"Career dataset not found: {CAREERS_FILE}"
        )

    df = pd.read_csv(CAREERS_FILE).fillna("")

    required_columns = {
        "career", "domain", "skills", "interests", "education"
    }

    if not required_columns.issubset(df.columns):
        raise ValueError(
            "The career dataset has missing columns."
        )

    return df


def split_items(value):
    """Convert pipe-separated text into lowercase items."""
    if not isinstance(value, str):
        return []

    return [
        item.strip().lower()
        for item in value.split("|")
        if item.strip()
    ]


def calculate_recommendations(
    skills, interests, education, top_n=3
):
    """Rank careers using skill, interest, and education matches."""
    careers = load_careers()

    student_skills = set(split_items("|".join(skills)))
    student_interests = set(split_items("|".join(interests)))
    education = education.strip().lower()

    if not student_skills and not student_interests:
        return []

    results = []

    for _, row in careers.iterrows():
        required_skills = set(split_items(row["skills"]))
        career_interests = set(split_items(row["interests"]))
        education_options = set(split_items(row["education"]))

        matched_skills = student_skills & required_skills
        missing_skills = required_skills - student_skills
        matched_interests = student_interests & career_interests

        skill_score = (
            len(matched_skills) / len(required_skills) * 100
            if required_skills else 0
        )

        interest_score = (
            len(matched_interests) / len(career_interests) * 100
            if career_interests else 0
        )

        education_score = (
            100
            if "any degree" in education_options
            or education in education_options
            else 60
        )

        final_score = (
            0.60 * skill_score
            + 0.25 * interest_score
            + 0.15 * education_score
        )

        results.append({
            "career": row["career"],
            "domain": row["domain"],
            "match_score": round(final_score, 1),
            "skill_score": round(skill_score, 1),
            "interest_score": round(interest_score, 1),
            "education_score": round(education_score, 1),
            "matched_skills": sorted(matched_skills),
            "missing_skills": sorted(missing_skills),
            "matched_interests": sorted(matched_interests),
            "required_skills": sorted(required_skills),
        })

    results.sort(
        key=lambda item: item["match_score"],
        reverse=True
    )

    return results[:max(1, top_n)]


def calculate_career_readiness(student_skills, career_name):
    """
    Calculate career readiness based on required skill coverage.

    The score measures skill coverage, not the probability
    of getting a job or placement.
    """
    careers = load_careers()

    # Normalize student skills
    if isinstance(student_skills, str):
        student_skills = split_items(student_skills)
    else:
        student_skills = [
            skill.strip().lower()
            for skill in student_skills
            if isinstance(skill, str) and skill.strip()
        ]

    student_skills = set(student_skills)

    # Find the selected career
    career_rows = careers[
        careers["career"].str.strip().str.lower()
        == career_name.strip().lower()
    ]

    if career_rows.empty:
        return None

    career = career_rows.iloc[0]

    # Get the required skills
    required_skills = set(split_items(career["skills"]))

    # Compare skills
    matched_skills = student_skills & required_skills
    missing_skills = required_skills - student_skills

    # Calculate readiness score
    if not required_skills:
        readiness_score = 0.0
    else:
        readiness_score = round(
            len(matched_skills) / len(required_skills) * 100,
            1
        )

    return {
        "career": career["career"],
        "domain": career["domain"],
        "readiness_score": readiness_score,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "required_skills": sorted(required_skills),
        "total_required_skills": len(required_skills),
        "total_matched_skills": len(matched_skills),
        "total_missing_skills": len(missing_skills),
    }