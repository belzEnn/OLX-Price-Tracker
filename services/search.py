from parsers.olx import fetch_listings
from models.listing import Listing


async def search_listings(query: str, limit: int = 40, offset: int = 0) -> list[Listing]:
    return await fetch_listings(query, limit=limit, offset=offset)
