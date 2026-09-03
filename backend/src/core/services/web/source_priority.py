import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

DEFAULT_TIER = 4 # fallback for domain not in map

DOMAIN_DISPLAY_NAMES = {
    "kemkes.go.id": "Kemenkes RI",
    "idai.or.id": "IDAI",
    "who.int": "WHO",
    "cdc.gov": "CDC",
    "nih.gov": "NIH",
    "medlineplus.gov": "MedlinePlus (NIH)",
    "unicef.org": "UNICEF",
    "msyoclinic.org": "Mayo Clinic",
    "healthychildren.ord": "HealthyChildren.org (AAP)",
    "alodokter.com": "Alodokter",
    "halodoc.com": "Halodoc",
}


def get_domain_tier(url: str, tier_map: dict[str, int]) -> int:
    """A lower number = more trustworthy (Tier 1 = official institutions)."""
    netloc = urlparse(url).netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]

    for domain, tier in tier_map.items():
        if netloc == domain or netloc.endswith(f".{domain}"):
            return tier
        
    return DEFAULT_TIER


def sort_by_source_tier(chunks: list[dict], tier_map: dict[str, int]) -> list[dict]:
    """
    Sort web chunks by confidence tier (ascending, Tier 1 first),
    while preserving the re-ranked relevance order within the same tier.
    Stamp the resolution tier onto each chunk’s metadata for downstream use.
    """
    for chunk in chunks:
        chunk["metadata"]["source_tier"] = get_domain_tier(chunk["metadata"]["source"], tier_map)

    return sorted(chunks, key=lambda c: c["metadata"]["source_tier"])

def get_source_label(url: str, title: str) -> str:
    """Create a label in the format “Organization — Title” (e.g., “WHO — Iron Requirements in Infants”)."""
    netloc = urlparse(url).netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]

    display_name = next(
        (name for domain, name in DOMAIN_DISPLAY_NAMES.items() if netloc == domain or netloc.endswith(f".{domain}")),
        netloc
    )
    return f"{display_name} - {title}"