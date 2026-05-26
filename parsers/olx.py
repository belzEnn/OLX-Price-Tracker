import httpx
from typing import Optional
from models.listing import Listing

GRAPHQL_QUERY = """
query ListingSearchQuery(
  $searchParameters: [SearchParameter!] = []
) {
  clientCompatibleListings(searchParameters: $searchParameters) {
    __typename
    ... on ListingSuccess {
      data {
        id
        title
        url
        description
        created_time
        business
        location {
          city { name }
          region { name }
        }
        params {
          key
          value {
            __typename
            ... on PriceParam {
              value
              negotiable
              label
              currency
              arranged
            }
            ... on GenericParam {
              key
              label
            }
          }
        }
        photos {
          link
        }
      }
      metadata {
        total_elements
        visible_total_count
      }
    }
    ... on ListingError {
      error { detail }
    }
  }
}
"""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0",
    "Accept": "application/json",
    "Accept-Language": "uk",
    "Content-Type": "application/json",
    "Referer": "https://www.olx.ua/uk/list/q-iphone-14/",
    "x-client": "DESKTOP",
    "Origin": "https://www.olx.ua",
}

OLX_GRAPHQL_URL = "https://www.olx.ua/apigateway/graphql"


def _parse_listing(raw: dict) -> Listing:
    price = None
    price_label = "Договірна"
    negotiable = False
    arranged = False

    for param in raw.get("params", []):
        if param["key"] == "price":
            val = param.get("value", {})
            price = val.get("value")
            price_label = val.get("label", "")
            negotiable = val.get("negotiable", False)
            arranged = val.get("arranged", False)

    location = raw.get("location", {})
    city = location.get("city", {}).get("name", "") if location.get("city") else ""
    region = location.get("region", {}).get("name", "") if location.get("region") else ""

    photos = raw.get("photos", [])
    photo_url = (
        photos[0]["link"].replace("{width}", "400").replace("{height}", "300")
        if photos else None
    )

    return Listing(
        id=raw["id"],
        title=raw["title"],
        url=raw["url"],
        price=price,
        price_label=price_label,
        negotiable=negotiable,
        arranged=arranged,
        city=city,
        region=region,
        description=raw.get("description", ""),
        is_business=raw.get("business", False),
        photo_url=photo_url,
        created_time=raw.get("created_time", ""),
    )


async def fetch_listings(query: str, limit: int = 40, offset: int = 0) -> list[Listing]:
    payload = {
        "query": GRAPHQL_QUERY,
        "variables": {
            "searchParameters": [
                {"key": "offset", "value": str(offset)},
                {"key": "limit", "value": str(limit)},
                {"key": "query", "value": query},
                {"key": "suggest_filters", "value": "true"},
            ],
        }
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(OLX_GRAPHQL_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()

    if "errors" in data:
        raise Exception(f"GraphQL error: {data['errors'][0]['message']}")

    listings_data = data["data"]["clientCompatibleListings"]

    if listings_data["__typename"] == "ListingError":
        raise Exception(f"OLX error: {listings_data['error']['detail']}")

    return [_parse_listing(item) for item in listings_data["data"]]
