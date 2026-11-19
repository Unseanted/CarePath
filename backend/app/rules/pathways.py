"""
Question banks per pathway.
These are provisional and MUST be reviewed by qualified clinicians
before any real-patient use.
"""

from app.models.schemas import Pathway

PATHWAY_LABELS = {
    Pathway.GENERAL: "General reproductive health",
    Pathway.FERTILITY: "Fertility concerns",
    Pathway.SYMPTOMS: "Symptoms or a health concern",
    Pathway.FIND_PROFESSIONAL: "Find a healthcare professional",
}

# Each question: id, prompt, type (yes_no | choice | text), options?, required, clinical_note
# Keep questions minimal and justified by protocol.

COMMON_QUESTIONS = [
    {
        "id": "age_band",
        "prompt": "Which age range best describes you?\n1. Under 25\n2. 25–34\n3. 35–44\n4. 45 or over\n\nReply with the number.",
        "type": "choice",
        "options": {"1": "under_25", "2": "25_34", "3": "35_44", "4": "45_plus"},
        "required": True,
    },
    {
        "id": "trying_to_conceive",
        "prompt": "Are you currently trying to conceive or planning to in the next year?\n1. Yes\n2. No\n3. Prefer not to say\n\nReply with the number.",
        "type": "choice",
        "options": {"1": "yes", "2": "no", "3": "prefer_not"},
        "required": True,
    },
]

FERTILITY_EXTRA = [
    {
        "id": "duration_trying",
        "prompt": "If you have been trying to conceive, for how long?\n1. Less than 6 months\n2. 6–12 months\n3. More than 12 months\n4. Not trying / not applicable\n\nReply with the number.",
        "type": "choice",
        "options": {"1": "lt_6m", "2": "6_12m", "3": "gt_12m", "4": "na"},
        "required": True,
    },
    {
        "id": "prior_semen_test",
        "prompt": "Have you ever had a semen analysis or fertility test?\n1. Yes – results were normal\n2. Yes – results were abnormal or unclear\n3. No\n4. Prefer not to say\n\nReply with the number.",
        "type": "choice",
        "options": {"1": "normal", "2": "abnormal", "3": "no", "4": "prefer_not"},
        "required": True,
    },
]

SYMPTOMS_EXTRA = [
    {
        "id": "severe_pain",
        "prompt": "Do you currently have severe testicular or scrotal pain?\n1. Yes\n2. No\n\nReply with the number.",
        "type": "choice",
        "options": {"1": True, "2": False},
        "required": True,
        "red_flag_if": True,
    },
    {
        "id": "sudden_swelling",
        "prompt": "Have you noticed sudden swelling or a lump in the testicle area?\n1. Yes\n2. No\n\nReply with the number.",
        "type": "choice",
        "options": {"1": True, "2": False},
        "required": True,
        "red_flag_if": True,
    },
    {
        "id": "fever_with_pain",
        "prompt": "Do you have fever together with scrotal or lower abdominal pain?\n1. Yes\n2. No\n\nReply with the number.",
        "type": "choice",
        "options": {"1": True, "2": False},
        "required": True,
        "red_flag_if": True,
    },
    {
        "id": "other_symptoms",
        "prompt": "Any other symptoms you would like us to note? (or reply 'none')",
        "type": "text",
        "required": False,
    },
]

GENERAL_EXTRA = [
    {
        "id": "known_condition",
        "prompt": "Have you been told you have any of the following?\n1. Varicocele\n2. Previous testicular infection or injury\n3. Hormone-related condition\n4. None of these / not sure\n\nReply with the number (or several separated by commas).",
        "type": "choice_multi",
        "options": {
            "1": "varicocele",
            "2": "prior_infection_or_injury",
            "3": "hormone_condition",
            "4": "none",
        },
        "required": True,
    },
    {
        "id": "lifestyle_smoking",
        "prompt": "Do you currently smoke or use tobacco?\n1. Yes\n2. No\n3. Prefer not to say\n\nReply with the number.",
        "type": "choice",
        "options": {"1": "yes", "2": "no", "3": "prefer_not"},
        "required": False,
    },
]


def get_questions_for_pathway(pathway: Pathway) -> list[dict]:
    """Return ordered question list for the selected pathway."""
    if pathway == Pathway.FIND_PROFESSIONAL:
        # Short path – mainly location / service preference later
        return COMMON_QUESTIONS[:1]  # age band only for basic matching
    if pathway == Pathway.FERTILITY:
        return COMMON_QUESTIONS + FERTILITY_EXTRA
    if pathway == Pathway.SYMPTOMS:
        return COMMON_QUESTIONS + SYMPTOMS_EXTRA
    # GENERAL
    return COMMON_QUESTIONS + GENERAL_EXTRA
