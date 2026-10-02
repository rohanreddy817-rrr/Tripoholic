import httpx


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


async def search_places(
    query: str,
    limit: int = 10
):
    params = {
        "q": query,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": min(limit, 20),
        "countrycodes": "in"
    }

    headers = {
        "User-Agent": "Tripoholic/1.0 Travel Planning Application"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            NOMINATIM_URL,
            params=params,
            headers=headers
        )

    response.raise_for_status()

    return response.json()