from fastapi import APIRouter, Query, HTTPException
from services.search import search_listings
from models.listing import Listing

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=list[Listing])
async def search(
    query: str = Query(...),
    limit: int = Query(40, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    try:
        return await search_listings(query, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))