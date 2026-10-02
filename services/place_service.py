from integrations.places_provider import search_places


async def search_india_places(
    query: str,
    limit: int = 10
):
    results = await search_places(
        query=query,
        limit=limit
    )

    places = []

    for result in results:

        address = result.get("address", {})

        places.append({
            "external_place_id": result.get("place_id"),
            "name": result.get("display_name"),
            "latitude": float(result["lat"]),
            "longitude": float(result["lon"]),
            "type": result.get("type"),
            "category": result.get("class"),
            "city": (
                address.get("city")
                or address.get("town")
                or address.get("village")
            ),
            "state": address.get("state"),
            "country": address.get("country")
        })

    return places
