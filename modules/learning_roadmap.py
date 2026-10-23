
"""Generate a personalized learning roadmap from missing skills."""

LEARNING_RESOURCES = {
    "python": {
        "duration": "2 weeks",
        "topics": "Python basics, functions, data structures",
        "resource": "https://docs.python.org/3/tutorial/",
    },
    "sql": {
        "duration": "2 weeks",
        "topics": "SELECT, JOIN, GROUP BY, subqueries",
        "resource": "https://sqlbolt.com/",
    },
    "statistics": {
        "duration": "2 weeks",
        "topics": "Mean, median, probability, distributions",
        "resource": "https://www.khanacademy.org/math/statistics-probability",
    },
    "machine learning": {
        "duration": "4 weeks",
        "topics": "Regression, classification, model evaluation",
        "resource": "https://scikit-learn.org/stable/tutorial/index.html",
    },
    "pandas": {
        "duration": "1 week",
        "topics": "DataFrames, filtering, cleaning, grouping",
        "resource": "https://pandas.pydata.org/docs/getting_started/",
    },
    "excel": {
        "duration": "1 week",
        "topics": "Formulas, sorting, pivot tables, charts",
        "resource": "https://support.microsoft.com/excel",
    },
    "power bi": {
        "duration": "2 weeks",
        "topics": "Data modeling, dashboards, visualizations",
        "resource": "https://learn.microsoft.com/power-bi/",
    },
    "tableau": {
        "duration": "2 weeks",
        "topics": "Charts, dashboards, calculated fields",
        "resource": "https://www.tableau.com/learn/training",
    },
    "data visualization": {
        "duration": "1 week",
        "topics": "Charts, storytelling, visual design",
        "resource": "https://matplotlib.org/stable/tutorials/",
    },
    "java": {
        "duration": "3 weeks",
        "topics": "OOP, collections, exception handling",
        "resource": "https://dev.java/learn/",
    },
    "react": {
        "duration": "3 weeks",
        "topics": "Components, props, state, hooks",
        "resource": "https://react.dev/learn",
    },
    "statistics and probability": {
        "duration": "2 weeks",
        "topics": "Probability, distributions, statistical inference",
        "resource": "https://www.khanacademy.org/math/statistics-probability",
    },
}


def generate_learning_roadmap(missing_skills):
    """Create learning steps for skills missing from a career profile."""

    roadmap = []

    for skill in missing_skills:
        normalized_skill = skill.strip().lower()

        resource = LEARNING_RESOURCES.get(
            normalized_skill,
            {
                "duration": "1–2 weeks",
                "topics": f"Learn the fundamentals and practice {skill}",
                "resource": "",
            },
        )

        roadmap.append({
            "skill": skill.title(),
            "duration": resource["duration"],
            "topics": resource["topics"],
            "resource": resource["resource"],
        })

    return roadmap
