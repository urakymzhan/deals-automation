import requests
from typing import Optional
from config import RAPIDAPI_KEY, RAPIDAPI_HOST

HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST,
    "Content-Type": "application/json",
}


def get_region_id(zip_code: str) -> Optional[str]:
    """Convert a zip code to a Redfin regionId using autocomplete."""
    try:
        response = requests.get(
            f"https://{RAPIDAPI_HOST}/properties/auto-complete",
            headers=HEADERS,
            params={"query": zip_code},
            timeout=10,
        )
        response.raise_for_status()
        results = response.json()
        sections = results.get("data", [])

        # Look for the "Places" section which contains zip code matches
        for section in sections:
            if section.get("name") == "Places":
                for row in section.get("rows", []):
                    if zip_code in row.get("name", ""):
                        return row.get("id")

        # Fallback: first row with an id
        for section in sections:
            for row in section.get("rows", []):
                if row.get("id"):
                    return row.get("id")

    except Exception as e:
        print(f"[Redfin] Error getting region ID for {zip_code}: {e}")
    return None


def search_properties(
    zip_code: str,
    max_price: Optional[float] = None,
    min_beds: Optional[int] = None,
    min_baths: Optional[float] = None,
    region_id: Optional[str] = None,
) -> list[dict]:
    """Search Redfin for for-sale listings in a zip code."""
    if not RAPIDAPI_KEY:
        print("[Redfin] RAPIDAPI_KEY not set. Skipping.")
        return []

    if not region_id:
        region_id = get_region_id(zip_code)
    if not region_id:
        print(f"[Redfin] Could not find regionId for zip {zip_code}")
        return []

    params = {"regionId": region_id}
    if max_price:
        params["maxPrice"] = int(max_price)
    if min_beds:
        params["bedsMin"] = min_beds
    if min_baths:
        params["bathsMin"] = min_baths

    try:
        response = requests.get(
            f"https://{RAPIDAPI_HOST}/properties/search-sale",
            headers=HEADERS,
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print(f"[Redfin] Error searching {zip_code}: {e}")
        return []


def search_sold(zip_code: str) -> list[dict]:
    """Fetch recently sold properties for a zip code (used for ARV comps)."""
    if not RAPIDAPI_KEY:
        return []

    region_id = get_region_id(zip_code)
    if not region_id:
        print(f"[Redfin] Could not find regionId for sold search in zip {zip_code}")
        return []

    try:
        response = requests.get(
            f"https://{RAPIDAPI_HOST}/properties/search-sold",
            headers=HEADERS,
            params={"regionId": region_id},
            timeout=15,
        )
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"[Redfin] Error fetching sold data for {zip_code}: {e}")
        return []


def calc_arv_comps(sold_props: list[dict]) -> Optional[float]:
    """Calculate average price per sqft from sold comps. Returns None if insufficient data."""
    price_per_sqft = []
    for prop in sold_props:
        home = prop.get("homeData", {})
        price_raw = home.get("priceInfo", {}).get("amount")
        sqft_raw = home.get("sqftInfo", {}).get("amount")
        if price_raw and sqft_raw:
            try:
                ppsf = float(price_raw) / float(sqft_raw)
                price_per_sqft.append(ppsf)
            except (ValueError, ZeroDivisionError):
                pass
    if len(price_per_sqft) < 3:
        return None
    return sum(price_per_sqft) / len(price_per_sqft)


def parse_property(prop: dict, search_id: int) -> dict:
    """Normalize a Redfin API property result."""
    home = prop.get("homeData", {})

    listing_id = str(home.get("propertyId", ""))
    price_raw = home.get("priceInfo", {}).get("amount")
    price = float(price_raw) if price_raw else None
    beds = home.get("beds")
    baths = home.get("baths")
    sqft_raw = home.get("sqftInfo", {}).get("amount")
    sqft = float(sqft_raw) if sqft_raw else None
    dom_raw = home.get("daysOnMarket", {}).get("daysOnMarket")
    dom = int(dom_raw) if dom_raw else None

    addr = home.get("addressInfo", {})
    address = f"{addr.get('formattedStreetLine', '')}, {addr.get('city', '')}, {addr.get('state', '')} {addr.get('zip', '')}".strip(", ")

    url = home.get("url", "")
    if url and not url.startswith("http"):
        url = f"https://www.redfin.com{url}"

    return {
        "search_id": search_id,
        "zpid": listing_id,
        "address": address,
        "price": price,
        "beds": beds,
        "baths": baths,
        "sqft": sqft,
        "days_on_market": dom,
        "url": url,
    }
