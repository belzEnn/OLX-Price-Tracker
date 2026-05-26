from pydantic import BaseModel
from typing import Optional


class Listing(BaseModel):
    id: int
    title: str
    url: str
    price: Optional[int] = None
    price_label: str = "Договірна"
    negotiable: bool = False
    arranged: bool = False
    city: str = ""
    region: str = ""
    description: str = ""
    is_business: bool = False
    photo_url: Optional[str] = None
    created_time: str = ""
