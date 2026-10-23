import inspect
import re
from typing import Any
import streamlit as st
import pymupdf
from modules.chatbot import get_career_response

from modules.learning_roadmap import generate_learning_roadmap

from modules.recommender import (

    load_careers,

    split_items,

    calculate_recommendations,

    calculate_career_readiness,

)

from modules.database import initialize_database, save_profile

from modules.resume_analyzer import extract_skills, analyze_skill_gap





# --------------------------------------------------

# 1. Page configuration and initialization

# --------------------------------------------------

st.set_page_config(

    page_title="CareerCompass AI",

    page_icon="🎯",

    layout="wide",

    initial_sidebar_state="expanded",

)



initialize_database()



for key, default in {

    "career_results": [],

    "chat_history": [],

    "resume_analysis": None,

    "resume_analysis_career": None,

    "resume_file_name": None,

    "student_name": "",

    "student_skills": [],

    "student_interests": [],

    "student_education": "",

    "profile_id": None,

}.items():

    if key not in st.session_state:

        st.session_state[key] = default





# --------------------------------------------------

# 2. Styling

# --------------------------------------------------

st.markdown(

    """

    <style>

    :root {

        --cc-bg: #080D1A;

        --cc-panel: #111A2E;

        --cc-panel-soft: #17223A;

        --cc-text: #F3F5FA;

        --cc-muted: #AAB4C8;

        --cc-border: rgba(166, 182, 214, .18);

        --cc-purple: #8B5CF6;

        --cc-cyan: #38BDF8;

        --cc-green: #34D399;

    }

    .stApp { background: var(--cc-bg); color: var(--cc-text); }

    [data-testid="stHeader"] { background: rgba(8,13,26,.94); }

    [data-testid="stSidebar"] { background: #0B1222; border-right: 1px solid var(--cc-border); }

    [data-testid="stSidebar"] > div { padding-top: 1.2rem; }

    .block-container { max-width: 1440px; padding-top: 1.8rem; padding-bottom: 2rem; }

    h1, h2, h3, h4, p, label { color: var(--cc-text); }

    .cc-brand { font-size: 1.2rem; font-weight: 850; letter-spacing: -.02em; }

    .cc-sidebar-sub { color: var(--cc-muted); font-size: .82rem; line-height: 1.5; margin: .35rem 0 1rem; }

    .cc-topbar { display:flex; justify-content:space-between; align-items:center; gap:1rem; padding:1.25rem 1.4rem; border:1px solid var(--cc-border); border-radius:20px; background:linear-gradient(120deg,rgba(139,92,246,.17),rgba(56,189,248,.07)); margin-bottom:1rem; }

    .cc-title { font-size:2rem; line-height:1.15; font-weight:900; letter-spacing:-.04em; margin:0; }

    .cc-subtitle { color:var(--cc-muted); margin-top:.45rem; font-size:.96rem; }

    .cc-eyebrow { color:#C4B5FD; font-size:.72rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }

    .cc-hero { padding:1.35rem 1.5rem; border-radius:18px; background:var(--cc-panel); border:1px solid var(--cc-border); margin:1rem 0 1.4rem; }

    .cc-hero-title { font-size:1.2rem; font-weight:800; margin-bottom:.35rem; }

    .cc-muted { color:var(--cc-muted); line-height:1.65; }

    .cc-card { background:var(--cc-panel); border:1px solid var(--cc-border); padding:1rem 1.1rem; border-radius:16px; margin:.35rem 0 .7rem; }

    .cc-card-title { font-size:1.08rem; font-weight:800; margin-bottom:.25rem; }

    .cc-pill { display:inline-block; padding:.25rem .6rem; margin:.15rem .2rem .15rem 0; border-radius:999px; background:rgba(139,92,246,.16); border:1px solid rgba(139,92,246,.30); color:#DDD6FE; font-size:.78rem; }

    .cc-footer { text-align:center; color:var(--cc-muted); padding:1.5rem 0 .5rem; font-size:.82rem; }

    .score-ring-wrap { display:flex; justify-content:center; align-items:center; padding:.4rem 0 .5rem; }

    .score-label { color:var(--cc-muted); text-align:center; font-size:.68rem; letter-spacing:.14em; font-weight:800; }

    [data-testid="stMetric"] { background:var(--cc-panel); border:1px solid var(--cc-border); padding:1rem; border-radius:14px; }

    [data-testid="stMetricLabel"] { color:var(--cc-muted) !important; }

    [data-testid="stMetricValue"] { color:var(--cc-text) !important; }

    [data-baseweb="input"] > div, [data-baseweb="textarea"] > div,

    [data-baseweb="select"] > div { background:#111A2E !important; border-color:#34415D !important; color:#F3F5FA !important; border-radius:10px !important; }

    input, textarea { color:#F3F5FA !important; -webkit-text-fill-color:#F3F5FA !important; }

    [data-baseweb="select"] * { color:#F3F5FA !important; }

    /* Premium dark resume uploader */
    [data-testid="stFileUploader"] {
        background: #111A2E !important;
        border: 1px dashed #536581 !important;
        border-radius: 14px !important;
        padding: 12px !important;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: #111A2E !important;
        border: 1px dashed #475569 !important;
        border-radius: 10px !important;
    }

    [data-testid="stFileUploaderDropzone"] > div {
        background: transparent !important;
    }

    [data-testid="stFileUploaderDropzone"] button {
        background: #1B2740 !important;
        color: #F3F5FA !important;
        border: 1px solid #536581 !important;
        border-radius: 8px !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover {
        background: #253454 !important;
        border-color: #8B5CF6 !important;
        color: #FFFFFF !important;
    }

    [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stFileUploaderDropzone"] span {
        color: #AAB4C8 !important;
    }

    [data-testid="stFileUploaderDropzone"] svg {
        color: #A78BFA !important;
    }

    .stButton > button, .stFormSubmitButton > button { color:white !important; background:linear-gradient(100deg,#7C3AED,#2563EB) !important; border:0 !important; border-radius:10px !important; min-height:2.65rem; font-weight:750 !important; }

    .stButton > button:hover, .stFormSubmitButton > button:hover { filter:brightness(1.1); }



/* Premium dark AI chat input and fixed bottom area */



/* CareerCompass AI - consistent dark chat footer */



[data-testid="stBottom"],

[data-testid="stBottom"] *,

[data-testid="stBottomBlockContainer"],

[data-testid="stChatInput"],

[data-testid="stChatInput"] form {

    background-color: #080D1A !important;

    box-shadow: none !important;

}



/* Dark chat input container */

[data-testid="stChatInput"] > div,

[data-testid="stChatInput"] form > div {

    background: #111A2E !important;

    border: 1px solid #34415D !important;

    border-radius: 14px !important;

}



/* Chat text */

[data-testid="stChatInput"] textarea {

    background: transparent !important;

    color: #F3F5FA !important;

    -webkit-text-fill-color: #F3F5FA !important;

    caret-color: #A78BFA !important;

    border: none !important;

    box-shadow: none !important;

    opacity: 1 !important;

}



/* Placeholder */

[data-testid="stChatInput"] textarea::placeholder {

    color: #AAB4C8 !important;

    -webkit-text-fill-color: #AAB4C8 !important;

    opacity: 1 !important;

}



/* Send button */

[data-testid="stChatInput"] button {

    background: linear-gradient(100deg, #7C3AED, #2563EB) !important;

    color: #FFFFFF !important;

    border: none !important;

    border-radius: 10px !important;

}



    [data-testid="stChatMessage"] { background:var(--cc-panel); border:1px solid var(--cc-border); border-radius:14px; padding:.8rem 1rem; margin-bottom:.6rem; }

    [data-testid="stExpander"] { background:var(--cc-panel); border:1px solid var(--cc-border); border-radius:13px; }

    [data-testid="stAlert"] { border-radius:12px; }

    [data-testid="stProgressBar"] > div { background:#25314A; border-radius:999px; }

    [data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,#8B5CF6,#38BDF8); border-radius:999px; }

    hr { border-color:var(--cc-border) !important; }

    a { color:#A5B4FC; }

    @media(max-width:768px) { .block-container { padding:1rem .8rem 2rem; } .cc-topbar { align-items:flex-start; flex-direction:column; } .cc-title { font-size:1.65rem; } }


    /* FINAL FIX: keep profile text input and education dropdown dark and readable */
    [data-testid="stTextInput"] [data-baseweb="input"],
    [data-testid="stTextInput"] [data-baseweb="input"] > div,
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] [data-baseweb="select"],
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stSelectbox"] [role="combobox"] {
        background-color: #111A2E !important;
        color: #F3F5FA !important;
        border-color: #536581 !important;
        opacity: 1 !important;
        box-shadow: none !important;
    }

    [data-testid="stTextInput"] input {
        -webkit-text-fill-color: #F3F5FA !important;
        caret-color: #A78BFA !important;
    }

    [data-testid="stTextInput"] input::placeholder {
        color: #AAB4C8 !important;
        -webkit-text-fill-color: #AAB4C8 !important;
        opacity: 1 !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] span,
    [data-testid="stSelectbox"] [data-baseweb="select"] div,
    [data-testid="stSelectbox"] [data-baseweb="select"] input {
        color: #F3F5FA !important;
        -webkit-text-fill-color: #F3F5FA !important;
    }

    [data-testid="stSelectbox"] label,
    [data-testid="stTextInput"] label {
        color: #F3F5FA !important;
    }

    [data-baseweb="popover"], [data-baseweb="menu"],
    [role="listbox"], [role="option"] {
        background-color: #111A2E !important;
        color: #F3F5FA !important;
    }
    
/* Make AI mentor responses readable in dark mode */
[data-testid="stChatMessage"] {
    background-color: #111A2E !important;
    color: #F3F5FA !important;
    border: 1px solid #34415D !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] h4,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] em,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] * {
    color: #F3F5FA !important;
    -webkit-text-fill-color: #F3F5FA !important;
    opacity: 1 !important;
}

[data-testid="stChatMessage"] a {
    color: #93C5FD !important;
    -webkit-text-fill-color: #93C5FD !important;
}


    </style>

    """,

    unsafe_allow_html=True,

)



def render_score_ring(score, label="CAREER READINESS"):
    """Display a circular percentage indicator."""
    import math
    import html

    try:
        score = float(score)
        if not math.isfinite(score):
            score = 0
        score = max(0, min(100, score))
    except (TypeError, ValueError, OverflowError):
        score = 0

    percent = int(round(score))
    circumference = 2 * math.pi * 43
    offset = circumference * (1 - score / 100)
    safe_label = html.escape(str(label))

    st.markdown(
        f"""
        <div style="
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;
            padding:12px 6px 18px;
            text-align:center;
        ">
          <svg width="132" height="132" viewBox="0 0 120 120"
               role="img" aria-label="{safe_label}: {percent}%">
            <circle cx="60" cy="60" r="43"
                    fill="none"
                    stroke="#29344A"
                    stroke-width="10"/>
            <circle cx="60" cy="60" r="43"
                    fill="none"
                    stroke="#38BDF8"
                    stroke-width="10"
                    stroke-linecap="round"
                    stroke-dasharray="{circumference:.2f}"
                    stroke-dashoffset="{offset:.2f}"
                    transform="rotate(-90 60 60)"/>
            <text x="60" y="67"
                  text-anchor="middle"
                  fill="#F3F5FA"
                  font-size="25"
                  font-weight="700">{percent}%</text>
          </svg>
          <div style="
              color:#AAB4C8;
              font-size:12px;
              font-weight:700;
              letter-spacing:0.8px;
              margin-top:4px;
          ">{safe_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_split(value: Any) -> list[str]:

    """Use the project's split_items helper with a safe fallback."""

    if value is None:

        return []

    try:

        items = split_items(value)

    except Exception:

        items = re.split(r"[,;|\n]", str(value))

    if isinstance(items, str):

        items = [items]

    return [str(item).strip() for item in items if str(item).strip()]





def normalized_set(items: Any) -> set[str]:

    """Return normalized skill strings from common helper output shapes."""

    if items is None:

        return set()

    if isinstance(items, dict):

        for key in ("skills", "extracted_skills", "resume_skills", "items", "results"):

            if key in items:

                return normalized_set(items[key])

        items = list(items.keys())

    if isinstance(items, str):

        items = safe_split(items)

    try:

        return {str(item).strip().lower() for item in items if str(item).strip()}

    except TypeError:

        return {str(items).strip().lower()} if str(items).strip() else set()





def get_required_skills(careers_df, career_name: str) -> list[str]:

    """Find the required skills for a career row in the supplied dataset."""

    if "career" not in careers_df.columns or "skills" not in careers_df.columns:

        return []

    rows = careers_df[careers_df["career"].astype(str).str.casefold() == str(career_name).casefold()]

    if rows.empty:

        return []

    return safe_split(rows.iloc[0]["skills"])





def get_readiness(skills: list[str], career_name: str) -> dict | None:

    try:

        result = calculate_career_readiness(skills, career_name)

        return result if isinstance(result, dict) else None

    except Exception:

        return None





def call_roadmap(missing_skills: list[str], career_name: str):

    """Call the existing roadmap helper while accommodating common signatures."""

    try:

        sig = inspect.signature(generate_learning_roadmap)

        params = list(sig.parameters.values())

        values = {}

        for p in params:

            if p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):

                continue

            name = p.name.lower()

            if any(word in name for word in ("career", "role", "job", "path")):

                values[p.name] = career_name

            elif any(word in name for word in ("missing", "gap", "skill", "topic")):

                values[p.name] = missing_skills

        required = [p for p in params if p.default is inspect.Parameter.empty and p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)]

        if all(p.name in values for p in required):

            return generate_learning_roadmap(**values)

    except (TypeError, ValueError):

        pass

    for args in ((missing_skills,), (career_name, missing_skills), (missing_skills, career_name)):

        try:

            return generate_learning_roadmap(*args)

        except TypeError:

            continue

    return []





def normalize_roadmap(roadmap: Any, fallback_skills: list[str]) -> list[dict]:

    if isinstance(roadmap, dict):

        for key in ("roadmap", "steps", "learning_roadmap", "plan"):

            if key in roadmap:

                roadmap = roadmap[key]

                break

    if isinstance(roadmap, str):

        return [{"skill": s, "duration": "Practice regularly", "topics": roadmap, "resource": ""} for s in fallback_skills[:8]]

    items = []

    try:

        for index, step in enumerate(roadmap):

            if isinstance(step, dict):

                items.append({

                    "skill": str(step.get("skill", step.get("title", step.get("topic", fallback_skills[index] if index < len(fallback_skills) else f"Learning step {index + 1}")))),

                    "duration": str(step.get("duration", step.get("time", "Not specified"))),

                    "topics": str(step.get("topics", step.get("description", step.get("details", "Practice this skill with small exercises.")))),

                    "resource": str(step.get("resource", step.get("url", step.get("link", ""))) or ""),

                })

            else:

                items.append({"skill": str(step), "duration": "Practice regularly", "topics": "Learn the fundamentals and complete a small practical exercise.", "resource": ""})

    except TypeError:

        pass

    if not items:

        items = [{"skill": s, "duration": "Practice regularly", "topics": "Learn the fundamentals and complete a small practical exercise.", "resource": ""} for s in fallback_skills[:8]]

    return items





def normalize_gap_result(raw_gap: Any, detected_skills: set[str], required_skills: list[str]) -> dict:

    """Normalize the project's analyzer output into a consistent structure."""

    required_map = {s.lower(): s for s in required_skills}

    matched = [required_map[s] for s in required_map if s in detected_skills]

    missing = [s for s in required_skills if s.lower() not in detected_skills]

    if isinstance(raw_gap, dict):

        raw_matched = raw_gap.get("matched_skills", raw_gap.get("matching_skills", raw_gap.get("matched", None)))

        raw_missing = raw_gap.get("missing_skills", raw_gap.get("skills_to_learn", raw_gap.get("missing", None)))

        if raw_matched is not None:

            candidates = normalized_set(raw_matched)

            matched = [s for s in required_skills if s.lower() in candidates]

        if raw_missing is not None:

            candidates = normalized_set(raw_missing)

            missing = [s for s in required_skills if s.lower() in candidates]

    percentage = round((len(matched) / len(required_skills)) * 100) if required_skills else 0

    return {"matched_skills": matched, "missing_skills": missing, "match_percentage": percentage}





# --------------------------------------------------

# 3. Sidebar and page header

# --------------------------------------------------

with st.sidebar:

    st.markdown('<div class="cc-brand">✦ CareerCompass AI</div>', unsafe_allow_html=True)

    st.markdown('<div class="cc-sidebar-sub">Your personal AI-powered career guide</div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("**QUICK NAVIGATION**")

    st.markdown(

        """

        <div style="line-height:2.2">

          <a href="#student-profile" style="text-decoration:none">👤 Student Profile</a><br>

          <a href="#career-recommendations" style="text-decoration:none">🎯 Career Matches</a><br>

          <a href="#resume-analyzer" style="text-decoration:none">📄 Resume Analyzer</a><br>

          <a href="#learning-roadmap" style="text-decoration:none">🗺️ Learning Roadmap</a><br>

          <a href="#career-chatbot" style="text-decoration:none">🤖 AI Career Mentor</a>

        </div>

        """,

        unsafe_allow_html=True,

    )

    st.markdown("---")

    st.caption("Build skills. Explore possibilities. Move forward.")



st.markdown(
    """<div class="cc-topbar"><div><div class="cc-eyebrow">Personalized career discovery</div><div class="cc-title">CareerCompass AI 🎯</div><div class="cc-subtitle">Discover your direction. Develop your potential.</div></div><div style="text-align:right;color:#AAB4C8;font-size:.78rem;letter-spacing:.1em;font-weight:700">AI SKILL ANALYZER<br>CAREER READINESS</div></div><div class="cc-hero"><div class="cc-hero-title">Your future, with direction</div><div class="cc-muted">Get career recommendations based on your skills, interests, and education. Explore your readiness, identify missing skills, analyze your resume, build a learning roadmap, and ask your personal AI career mentor for guidance.</div></div>""",
    unsafe_allow_html=True,
)





# --------------------------------------------------

# 4. Load career dataset

# --------------------------------------------------

try:

    careers_df = load_careers()

    if careers_df is None or getattr(careers_df, "empty", True):

        st.error("The career dataset is empty. Please check the careers CSV file.")

        st.stop()

    required_columns = {"career", "skills", "interests", "education"}

    missing_columns = required_columns - set(careers_df.columns)

    if missing_columns:

        st.error("The career dataset is missing columns: " + ", ".join(sorted(missing_columns)))

        st.stop()

except Exception as error:

    st.error(f"Could not load the career dataset: {error}")

    st.stop()



all_skills = sorted({item for value in careers_df["skills"] for item in safe_split(value)}, key=str.casefold)

all_interests = sorted({item for value in careers_df["interests"] for item in safe_split(value)}, key=str.casefold)

education_options = ["btech", "bsc", "bca", "mtech", "msc", "bba", "bcom"]

if "education" in careers_df.columns:

    for value in careers_df["education"].dropna().astype(str).tolist():

        for item in safe_split(value):

            normalized = item.strip().lower()

            if normalized and normalized not in education_options:

                education_options.append(normalized)





# --------------------------------------------------

# 5. Student profile form

# --------------------------------------------------

st.markdown('<div id="student-profile"></div>', unsafe_allow_html=True)

st.header("👤 Build Your Student Profile")

st.caption("Tell us about your current skills and interests so we can suggest career paths to explore.")

with st.form("career_profile_form", clear_on_submit=False):

    name = st.text_input("Your name", value=st.session_state.get("student_name", ""), placeholder="Enter your name")

    current_education = st.session_state.get("student_education", "btech")

    if current_education not in education_options:

        current_education = "btech" if "btech" in education_options else education_options[0]

    education = st.selectbox(

        "Education",

        options=education_options,

        index=education_options.index(current_education),

        format_func=lambda value: value.upper(),

    )

    default_skills = [s for s in st.session_state.get("student_skills", []) if s in all_skills]

    default_interests = [i for i in st.session_state.get("student_interests", []) if i in all_interests]

    skills = st.multiselect("Skills you currently have", options=all_skills, default=default_skills, placeholder="Choose your skills")

    interests = st.multiselect("Areas that interest you", options=all_interests, default=default_interests, placeholder="Choose your interests")

    submitted = st.form_submit_button("✨ Find My Career Matches", use_container_width=True)



if submitted:

    if not name.strip():

        st.warning("Please enter your name.")

    elif not skills and not interests:

        st.warning("Select at least one skill or interest.")

    else:

        try:

            results = calculate_recommendations(skills=skills, interests=interests, education=education, top_n=5)

            if results is None:

                results = []

            if not isinstance(results, list):

                results = results.to_dict(orient="records") if hasattr(results, "to_dict") else list(results)

            if not results:

                st.warning("No recommendations could be generated. Try selecting more skills or interests.")

            else:

                try:

                    profile_id = save_profile(name=name.strip(), education=education, skills=skills, interests=interests, results=results)

                except Exception as db_error:

                    profile_id = None

                    st.warning(f"Recommendations were generated, but the profile could not be saved to the database: {db_error}")

                st.session_state["career_results"] = results

                st.session_state["profile_id"] = profile_id

                st.session_state["student_name"] = name.strip()

                st.session_state["student_skills"] = list(skills)

                st.session_state["student_interests"] = list(interests)

                st.session_state["student_education"] = education

                for key in ("resume_analysis", "resume_analysis_career", "resume_file_name", "resume_detected_count"):

                    st.session_state.pop(key, None)

                st.success("Your career recommendations are ready!")

        except Exception as error:

            st.error(f"Could not generate career recommendations: {error}")




# --------------------------------------------------
# 6. Career recommendations and readiness
# --------------------------------------------------

results = st.session_state.get("career_results", [])
student_skills = st.session_state.get("student_skills", [])
student_interests = st.session_state.get("student_interests", [])
student_education = st.session_state.get("student_education", "")
student_name = st.session_state.get("student_name", "")

if results:
    st.markdown(
        '<div id="career-recommendations"></div>',
        unsafe_allow_html=True,
    )

    st.header(f"🎯 {student_name or 'Your'} Career Recommendations")
    st.caption(
        "Explore the strongest matches first. Scores are guidance indicators, "
        "not guarantees of placement or employment."
    )

    for index, result in enumerate(results, start=1):
        if not isinstance(result, dict):
            try:
                result = dict(result)
            except Exception:
                result = {"career": str(result)}

        career_name = str(
            result.get(
                "career",
                result.get(
                    "career_name",
                    result.get("role", "Career option"),
                ),
            )
        )
        domain = str(result.get("domain", "Career pathway"))

        match_score = result.get(
            "match_score",
            result.get(
                "score",
                result.get(
                    "career_score",
                    result.get("match_percentage"),
                ),
            ),
        )
        interest_score = result.get("interest_score")

        # One separate card for each career.
        with st.container(border=True):
            st.subheader(f"{index}. {career_name}")
            st.caption(domain)

            # Calculate career readiness only once.
            readiness = get_readiness(student_skills, career_name)

            if isinstance(readiness, dict) and readiness:
                readiness_value = readiness.get(
                    "readiness_score",
                    readiness.get("score", 0),
                )

                matched_skills = readiness.get("matched_skills", []) or []
                missing_skills = readiness.get("missing_skills", []) or []

                matched_count = readiness.get(
                    "total_matched_skills",
                    len(matched_skills),
                )
                total_count = readiness.get(
                    "total_required_skills",
                    len(matched_skills) + len(missing_skills),
                )
            else:
                required = get_required_skills(careers_df, career_name)
                student_set = normalized_set(student_skills)

                matched_skills = [
                    skill for skill in required
                    if skill.strip().lower() in student_set
                ]
                missing_skills = [
                    skill for skill in required
                    if skill.strip().lower() not in student_set
                ]

                matched_count = len(matched_skills)
                total_count = len(required)

                readiness_value = (
                    round(matched_count * 100 / total_count)
                    if total_count else 0
                )

            # Keep all three circular graphs in one row.
            score_col1, score_col2, score_col3 = st.columns(3)

            with score_col1:
                if match_score is not None:
                    render_score_ring(match_score, "MATCH SCORE")
                else:
                    st.caption("Match score unavailable")

            with score_col2:
                if interest_score is not None:
                    render_score_ring(
                        interest_score,
                        "INTEREST COVERAGE",
                    )
                else:
                    st.caption("Interest score unavailable")

            with score_col3:
                try:
                    readiness_value = float(readiness_value)
                    if not (
                        readiness_value == readiness_value
                        and abs(readiness_value) != float("inf")
                    ):
                        readiness_value = 0
                    readiness_value = max(
                        0, min(100, readiness_value)
                    )
                except (TypeError, ValueError, OverflowError):
                    readiness_value = 0

                render_score_ring(
                    readiness_value,
                    "CAREER READINESS",
                )

            st.markdown("---")

            st.write(
                f"You currently match **{matched_count} of {total_count}** "
                "required skills for this role."
            )

            with st.expander("View skills and readiness details"):
                matched_col, missing_col = st.columns(2)

                with matched_col:
                    st.markdown("**✅ Skills you already have**")

                    if matched_skills:
                        for skill in matched_skills:
                            st.markdown(f"- {str(skill).title()}")
                    else:
                        st.write("No direct skill matches yet.")

                with missing_col:
                    st.markdown("**📌 Skills to learn next**")

                    if missing_skills:
                        for skill in missing_skills:
                            st.markdown(f"- {str(skill).title()}")
                    else:
                        st.success(
                            "All listed skills for this career are covered."
                        )

# --------------------------------------------------

# 7. Learning roadmap

# --------------------------------------------------

st.markdown('<div id="learning-roadmap"></div>', unsafe_allow_html=True)

st.header("🗺️ Personalized Learning Roadmap")

if not results:

    st.info("Create your student profile first. Your career recommendations will unlock a tailored learning roadmap.")

else:

    available_careers = [str(r.get("career", r.get("career_name", r.get("role", "Career option")))) for r in results if isinstance(r, dict)]

    if not available_careers:

        available_careers = careers_df["career"].dropna().astype(str).tolist()

    selected_career_for_roadmap = st.selectbox("Choose a career for your roadmap", options=available_careers, key="roadmap_career")

    roadmap_readiness = get_readiness(student_skills, selected_career_for_roadmap)

    if roadmap_readiness:

        roadmap_missing = [str(s) for s in roadmap_readiness.get("missing_skills", []) or []]

    else:

        req = get_required_skills(careers_df, selected_career_for_roadmap)

        student_set = normalized_set(student_skills)

        roadmap_missing = [s for s in req if s.lower() not in student_set]

    if st.button("Generate My Learning Roadmap", key="generate_roadmap", use_container_width=True):

        with st.spinner("Building your learning roadmap..."):

            try:

                raw_roadmap = call_roadmap(roadmap_missing, selected_career_for_roadmap)

                st.session_state["generated_roadmap"] = normalize_roadmap(raw_roadmap, roadmap_missing)

                st.session_state["generated_roadmap_career"] = selected_career_for_roadmap

            except Exception as error:

                st.error(f"Could not generate the learning roadmap: {error}")

    roadmap = st.session_state.get("generated_roadmap", [])

    if roadmap and st.session_state.get("generated_roadmap_career") == selected_career_for_roadmap:

        if roadmap_missing:

            st.write("Start with the skill gaps below. Work through the topics and practice each skill with a small project.")

        else:

            st.success("Your listed skills already match the dataset requirements. Use the roadmap to deepen your skills and build projects.")

        for index, step in enumerate(roadmap, start=1):

            with st.expander(f"Step {index}: {step['skill']}"):

                st.write(f"**Estimated duration:** {step['duration']}")

                st.write(f"**Topics / action:** {step['topics']}")

                if step.get("resource"):

                    resource = step["resource"]

                    if resource.startswith(("https://", "http://")):

                        st.markdown(f"[Open learning resource]({resource})")

                    else:

                        st.write(resource)

    elif not st.session_state.get("generated_roadmap"):

        st.caption("Choose a career and select Generate My Learning Roadmap to create your plan.")





# --------------------------------------------------

# 8. AI resume analyzer

# --------------------------------------------------

st.markdown('<div id="resume-analyzer"></div>', unsafe_allow_html=True)

st.header("📄 AI Resume Analyzer")

st.write("Upload a PDF resume and compare its detected skills with a career you want to pursue.")

resume_careers = [str(r.get("career", r.get("career_name", r.get("role", "Career option")))) for r in results if isinstance(r, dict)]

if not resume_careers:

    resume_careers = careers_df["career"].dropna().astype(str).tolist()

resume_careers = list(dict.fromkeys(resume_careers))

resume_col, career_col = st.columns([2, 1])

with resume_col:

    uploaded_resume = st.file_uploader("Upload resume (PDF)", type=["pdf"], key="resume_pdf_upload")

with career_col:

    default_resume_career = st.session_state.get("resume_analysis_career") or (resume_careers[0] if resume_careers else "")

    if default_resume_career not in resume_careers and resume_careers:

        default_resume_career = resume_careers[0]

    resume_career = st.selectbox("Target career", options=resume_careers, index=resume_careers.index(default_resume_career) if default_resume_career in resume_careers else 0, key="resume_target_career") if resume_careers else ""



if st.button("Analyze My Resume", key="analyze_resume", use_container_width=True):

    if uploaded_resume is None:

        st.warning("Please upload a PDF resume first.")

    elif not resume_career:

        st.warning("Please select a target career.")

    else:

        try:

            with st.spinner("Reading your resume and checking its skills..."):

                pdf_bytes = uploaded_resume.getvalue()

                with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf_document:

                    resume_text = "\n".join(page.get_text("text") for page in pdf_document)

                if not resume_text.strip():

                    raise ValueError("No readable text was found in this PDF. Try a text-based PDF rather than a scanned image.")

                extracted = extract_skills(resume_text)

                detected = normalized_set(extracted)

                required_skills = get_required_skills(careers_df, resume_career)

                raw_gap = None

                try:

                    raw_gap = analyze_skill_gap(list(detected), required_skills)

                except TypeError:

                    # Support modules whose helper names its two arguments explicitly.

                    try:

                        signature = inspect.signature(analyze_skill_gap)

                        kwargs = {}

                        for parameter in signature.parameters:

                            pname = parameter.lower()

                            if "resume" in pname or "detected" in pname or "candidate" in pname:

                                kwargs[parameter] = list(detected)

                            elif "required" in pname or "career" in pname or "target" in pname or "job" in pname:

                                kwargs[parameter] = required_skills

                        raw_gap = analyze_skill_gap(**kwargs)

                    except Exception:

                        raw_gap = None

                analysis = normalize_gap_result(raw_gap, detected, required_skills)

                # Keep the extracted skill list as well as the standard gap fields.

                analysis["detected_skills"] = sorted(detected)

                analysis["career"] = resume_career

                st.session_state["resume_analysis"] = analysis

                st.session_state["resume_analysis_career"] = resume_career

                st.session_state["resume_file_name"] = uploaded_resume.name

                st.session_state["resume_detected_count"] = len(detected)

        except Exception as error:

            st.error(f"Could not analyze this resume: {error}")



resume_analysis = st.session_state.get("resume_analysis")

if resume_analysis:

    st.markdown(f"### Resume results: {st.session_state.get('resume_analysis_career', 'Selected career')}")

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    metric_col1.metric("Skill match", f"{resume_analysis.get('match_percentage', 0)}%")

    metric_col2.metric("Matching skills", len(resume_analysis.get("matched_skills", [])))

    metric_col3.metric("Skills to learn", len(resume_analysis.get("missing_skills", [])))

    try:

        st.progress(max(0.0, min(1.0, float(resume_analysis.get("match_percentage", 0)) / 100)))

    except (TypeError, ValueError):

        pass

    matched_col, missing_col = st.columns(2)

    with matched_col:

        st.markdown("**Skills found in the resume and required for this career**")

        if resume_analysis.get("matched_skills"):

            for skill in resume_analysis["matched_skills"]:

                st.markdown(f"- ✅ {skill.title()}")

        else:

            st.write("No matching required skills were detected.")

    with missing_col:

        st.markdown("**Skills not detected in the resume**")

        if resume_analysis.get("missing_skills"):

            for skill in resume_analysis["missing_skills"]:

                st.markdown(f"- 📌 {skill.title()}")

        else:

            st.success("All skills listed for this career were detected.")

    with st.expander("View detected resume skills"):

        detected_skills = resume_analysis.get("detected_skills", [])

        st.write(", ".join(s.title() for s in detected_skills) if detected_skills else "No skills were detected.")



# --------------------------------------------------
# 9. Dedicated Skill Gap Analysis
# --------------------------------------------------

st.markdown('<div id="skill-gap-analysis"></div>', unsafe_allow_html=True)

st.header("🧩 Skill Gap Analysis")

st.write(
    "Analyze your current skills against your target career, "
    "identify missing skills, and get personalized learning recommendations."
)

# Select target career independently of the other sections.
available_gap_careers = careers_df["career"].dropna().astype(str).unique().tolist()

if available_gap_careers:
    recommended_gap_careers = [
        str(item.get("career", item.get("career_name", item.get("role", ""))))
        for item in results
        if isinstance(item, dict)
    ]

    gap_default_options = [
        career for career in recommended_gap_careers
        if career in available_gap_careers
    ]

    gap_career_options = gap_default_options or available_gap_careers

    selected_gap_career = st.selectbox(
        "Choose your target career",
        options=gap_career_options,
        key="dedicated_gap_career",
    )

    # Choose the source of skills for this separate analysis.
    has_resume_analysis = bool(st.session_state.get("resume_analysis"))

    skill_sources = ["Student Profile"]
    if has_resume_analysis:
        skill_sources.append("Uploaded Resume")

    selected_skill_source = st.radio(
        "Analyze skills from",
        options=skill_sources,
        horizontal=True,
        key="dedicated_gap_source",
    )

    if selected_skill_source == "Uploaded Resume":
        resume_data = st.session_state.get("resume_analysis", {})

        if resume_data.get("career") == selected_gap_career:
            analysis_skills = resume_data.get("detected_skills", [])
        else:
            st.info(
                "Your saved resume analysis targets a different career. "
                "Upload and analyze your resume for this career in the "
                "Resume Analyzer section first."
            )
            analysis_skills = []
    else:
        analysis_skills = st.session_state.get("student_skills", [])

    required_gap_skills = get_required_skills(
        careers_df, selected_gap_career
    )

    current_skill_set = normalized_set(analysis_skills)

    matched_gap_skills = [
        skill for skill in required_gap_skills
        if skill.strip().lower() in current_skill_set
    ]

    missing_gap_skills = [
        skill for skill in required_gap_skills
        if skill.strip().lower() not in current_skill_set
    ]

    gap_percentage = (
        round(len(matched_gap_skills) * 100 / len(required_gap_skills))
        if required_gap_skills else 0
    )

    st.markdown("---")

    if not analysis_skills:
        st.warning(
            "No skills are available for this analysis. "
            "Complete your Student Profile or analyze a resume first."
        )

    if not required_gap_skills:
        st.warning(
            "No required skills were found for this career in the dataset."
        )
    else:
        metric1, metric2, metric3 = st.columns(3)

        metric1.metric(
            "Matched Skills",
            len(matched_gap_skills),
        )
        metric2.metric(
            "Missing Skills",
            len(missing_gap_skills),
        )
        metric3.metric(
            "Skill Match",
            f"{gap_percentage}%",
        )

        st.progress(gap_percentage / 100)

        st.caption(
            f"You match {len(matched_gap_skills)} of "
            f"{len(required_gap_skills)} required skills for "
            f"{selected_gap_career}."
        )

        matched_col, missing_col = st.columns(2)

        with matched_col:
            st.subheader("✅ Skills You Have")

            if matched_gap_skills:
                for skill in matched_gap_skills:
                    st.markdown(f"- {skill.title()}")
            else:
                st.info("No matching skills found yet.")

        with missing_col:
            st.subheader("📌 Skills to Develop")

            if missing_gap_skills:
                for skill in missing_gap_skills:
                    st.markdown(f"- {skill.title()}")
            else:
                st.success("You match all the listed required skills!")

        st.markdown("---")

else:
    st.warning("No careers are available in the career dataset.")


# --------------------------------------------------
# Keep the existing AI Career Mentor section below
# --------------------------------------------------

# --------------------------------------------------

# 10. Personalized AI career mentor

# --------------------------------------------------

st.markdown('<div id="career-chatbot"></div>', unsafe_allow_html=True)

st.header("🤖 AI Career Mentor")

st.write("Ask about career options, skill gaps, interviews, projects, or how to plan your learning.")



# Build profile context from the saved profile and latest resume analysis.

def build_profile_context() -> str:

    parts = []

    if st.session_state.get("student_name"):

        parts.append(f"Student name: {st.session_state['student_name']}")

    if st.session_state.get("student_education"):

        parts.append(f"Education: {st.session_state['student_education']}")

    current_skills = st.session_state.get("student_skills", [])

    current_interests = st.session_state.get("student_interests", [])

    parts.append("Student skills: " + (", ".join(current_skills) if current_skills else "Not provided"))

    parts.append("Student interests: " + (", ".join(current_interests) if current_interests else "Not provided"))

    current_results = st.session_state.get("career_results", [])

    if current_results:

        career_names = [str(r.get("career", r.get("career_name", ""))) for r in current_results if isinstance(r, dict)]

        if career_names:

            parts.append("Recommended careers: " + ", ".join(career_names))

        first_career = career_names[0] if career_names else ""

        if first_career:

            readiness = get_readiness(current_skills, first_career)

            if readiness:

                parts.append(f"Readiness score for {first_career}: {readiness.get('readiness_score', 0)}%")

                parts.append("Matched skills: " + (", ".join(readiness.get("matched_skills", []) or []) or "None"))

                parts.append("Missing skills: " + (", ".join(readiness.get("missing_skills", []) or []) or "None"))

    latest_resume = st.session_state.get("resume_analysis")

    if latest_resume:

        parts.append("Latest resume target career: " + str(st.session_state.get("resume_analysis_career", "Unknown")))

        parts.append(f"Latest resume skill match: {latest_resume.get('match_percentage', 0)}%")

        parts.append("Resume-matched skills: " + (", ".join(latest_resume.get("matched_skills", []) or []) or "None"))

        parts.append("Resume missing skills: " + (", ".join(latest_resume.get("missing_skills", []) or []) or "None"))

    return "\n".join(parts)



for message in st.session_state["chat_history"]:

    with st.chat_message(message.get("role", "assistant")):

        st.markdown(message.get("content", ""))



prompt = st.chat_input("Ask your AI career mentor...")

if prompt:

    st.session_state["chat_history"].append({"role": "user", "content": prompt})

    with st.chat_message("user"):

        st.markdown(prompt)

    context = build_profile_context()

    question_with_context = (

        f"STUDENT QUESTION:\n{prompt}\n\n"

        f"STUDENT PROFILE CONTEXT:\n{context}\n\n"

        "CAREER GUIDANCE INSTRUCTIONS:\n"

        "- Personalize the answer using the supplied profile when relevant.\n"

        "- Use supplied scores and skill lists accurately.\n"

        "- Prioritize missing skills and realistic next steps.\n"

        "- Organize learning plans into weeks when useful.\n"

        "- Use simple English, headings, and practical examples.\n"

        "- Do not invent student details, scores, or learning resources.\n"

        "- Never guarantee jobs, salaries, or placements.\n"

        "- If no profile exists, provide general advice."

    )

    with st.chat_message("assistant"):

        with st.spinner("CareerCompass AI is thinking..."):

            try:

                answer = get_career_response(

                    question_with_context,

                    conversation_history=st.session_state["chat_history"][:-1],

                )

                if not isinstance(answer, str) or not answer.strip():

                    answer = "I couldn't generate a response. Please try again."

            except Exception as error:

                print(f"Chatbot error: {error}")

                answer = "Sorry, the AI career mentor is temporarily unavailable. Please check your Groq API key and internet connection, then try again."

        st.markdown(answer)

    st.session_state["chat_history"].append({"role": "assistant", "content": answer})
if st.button("🗑️ Clear Chat", key="clear_career_chat"):

    st.session_state["chat_history"] = []

    st.rerun()
# --------------------------------------------------

# 11. Footer

# --------------------------------------------------

st.divider()

st.markdown(

    '<div class="cc-footer">✦ CareerCompass AI · Personalized Career Recommendation Agent<br>Discover your direction. Develop your potential.</div>',

    unsafe_allow_html=True,

)
