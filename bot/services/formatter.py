from typing import List
from models.listing import Listing


def format_listing(listing: Listing) -> str:
    if listing.arranged:
        price_str = "Договірна"
    elif listing.price is not None:
        price_str = listing.price_label or f"{listing.price} грн"
        if listing.negotiable:
            price_str += " (торг)"
    else:
        price_str = listing.price_label or "Не вказана"

    location_parts = [p for p in [listing.city, listing.region] if p]
    location_str = ", ".join(location_parts) if location_parts else "Не вказано"

    lines = []
    # First 3 lines — visible when collapsed
    lines.append(f"<b>{_e(listing.title)}</b>")
    lines.append(f"💰 {_e(price_str)}")
    lines.append(f"📍 {_e(location_str)}")
    # Rest — visible only when expanded
    seller = "🏪 Магазин / бізнес" if listing.is_business else "👤 Приватна особа"
    lines.append(seller)
    if listing.created_time:
        lines.append(f"🕐 {_e(listing.created_time)}")
    if listing.description:
        desc = listing.description.strip()
        if len(desc) > 300:
            desc = desc[:297] + "..."
        lines.append(f"\n{_e(desc)}")
    lines.append(f"\n🔗 <a href=\"{listing.url}\">Відкрити оголошення</a>")

    inner = "\n".join(lines)
    return f"<blockquote expandable>{inner}</blockquote>"


def format_listings_message(listings: List[Listing]) -> str:
    return "\n\n".join(format_listing(l) for l in listings)


def _e(text: str) -> str:
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )