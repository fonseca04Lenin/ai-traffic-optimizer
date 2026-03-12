"""
Lightweight geocoder using OpenStreetMap Nominatim.
No API key required. Respects the 1 req/s rate limit guideline.
"""
import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "AITrafficOptimizer/1.0 (class-project; contact: student)"}


def geocode(address: str):
    """
    Convert a plain-text address to (lat, lng).
    Returns (None, None) on failure — callers must handle that gracefully.
    """
    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={"q": address, "format": "json", "limit": 1},
            headers=HEADERS,
            timeout=6,
        )
        resp.raise_for_status()
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None, None
