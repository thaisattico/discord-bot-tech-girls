import asyncio
from pprint import pprint
from services.news_search import search_news

async def testar():
    noticias = await search_news()
    
    noticias_teste = noticias[:3]
    print("\n============TESTANDO DICIONARIOS=============")
    pprint(noticias_teste if noticias_teste else "Lista vazia")

asyncio.run(testar()) 