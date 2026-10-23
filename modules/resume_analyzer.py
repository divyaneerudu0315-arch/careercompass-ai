
import re
import pymupdf


# Skills that CareerCompass AI can recognize
SKILL_KEYWORDS = [
    "python",
    "java",
    "c++",
    "sql",
    "excel",
    "statistics",
    "machine learning",
    "deep learning",
    "data science",
    "data analysis",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "power bi",
    "tableau",
    "html",
    "css",
    "javascript",
    "react",
    "git",
    "linux",
    "networking",
    "cybersecurity",
    "ethical hacking",
    "cloud",
    "docker",
    "api development",
    "communication",
    "problem solving",
    "figma",
    "ui design",
    "selenium",
    "testing",
]


def extract_text_from_pdf(uploaded_file):
    """Extract readable text from an uploaded PDF."""
    try:
        pdf_bytes = uploaded_file.getvalue()

        with pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        ) as document:
            pages = [
                page.get_text()
                for page in document
            ]

        return "\n".join(pages).strip()

    except Exception as error:
        raise ValueError(
            f"Could not read this PDF: {error}"
        ) from error


def extract_skills(resume_text):
    """Find recognized skills in resume text."""
    text = resume_text.lower()
    found_skills = []

    for skill in SKILL_KEYWORDS:
        pattern = (
            r"(?<![a-z0-9+#])"
            + re.escape(skill.lower())
            + r"(?![a-z0-9+#])"
        )

        if re.search(pattern, text):
            found_skills.append(skill)

    return sorted(set(found_skills))


def analyze_skill_gap(resume_skills, required_skills):
    """Compare resume skills against career requirements."""
    resume_set = {
        skill.strip().lower()
        for skill in resume_skills
    }

    required_set = {
        skill.strip().lower()
        for skill in required_skills
    }

    matched = sorted(resume_set & required_set)
    missing = sorted(required_set - resume_set)

    match_percentage = (
        round(len(matched) / len(required_set) * 100, 1)
        if required_set
        else 0
    )

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": match_percentage,
    }
