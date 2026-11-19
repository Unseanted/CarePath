"""
Simulated provider directory and matching.
In a real pilot these would be verified credentials and live availability.
"""

from app.models.schemas import Provider, ClinicalDecision, TriageCategory

# Prototype simulated directory – clearly marked as simulated
SIMULATED_PROVIDERS: list[Provider] = [
    Provider(
        provider_id="sim-pc-01",
        name="Community Primary Care Clinic (Simulated)",
        credentials="GP / Family Medicine – simulated entry",
        services=["primary_care", "gp", "general_information"],
        location="Demo City – Central",
        teleconsultation_available=True,
        verified=False,
    ),
    Provider(
        provider_id="sim-uro-01",
        name="City Urology & Andrology Centre (Simulated)",
        credentials="Consultant Urologist / Andrologist – simulated entry",
        services=["urology", "andrology", "specialist"],
        location="Demo City – Medical District",
        teleconsultation_available=True,
        verified=False,
    ),
    Provider(
        provider_id="sim-fert-01",
        name="Horizon Fertility Service (Simulated)",
        credentials="Reproductive medicine team – simulated entry",
        services=["fertility_clinic", "andrology", "specialist"],
        location="Demo City – North",
        teleconsultation_available=False,
        verified=False,
    ),
    Provider(
        provider_id="sim-urgent-01",
        name="Urgent Care / Emergency Pathway (Simulated)",
        credentials="Emergency department / urgent care – simulated entry",
        services=["urgent_care", "emergency"],
        location="Nearest emergency facility",
        teleconsultation_available=False,
        verified=False,
    ),
]


def match_providers(decision: ClinicalDecision, limit: int = 3) -> list[Provider]:
    """
    Return providers whose services intersect the recommended service types.
    Urgent decisions prioritise urgent_care / emergency entries.
    """
    wanted = set(decision.recommended_service_types)
    if decision.triage == TriageCategory.URGENT:
        wanted = {"urgent_care", "emergency"}

    matched = []
    for p in SIMULATED_PROVIDERS:
        if wanted.intersection(p.services):
            matched.append(p)
        if len(matched) >= limit:
            break
    return matched


def format_provider_list(providers: list[Provider]) -> str:
    if not providers:
        return "No matching providers in the current simulated directory."
    lines = []
    for i, p in enumerate(providers, 1):
        tele = "Teleconsultation available" if p.teleconsultation_available else "In-person"
        verified = "Verified" if p.verified else "Simulated entry – not a real clinic"
        lines.append(
            f"{i}. {p.name}\n"
            f"   {p.credentials}\n"
            f"   {p.location or 'Location not specified'} · {tele}\n"
            f"   ({verified})"
        )
    return "\n\n".join(lines)
