from .companies import update_search_companies
from .anime import update_search_anime


async def update_search():
    await update_search_companies()
    await update_search_anime()
