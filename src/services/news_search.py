import aiohttp

async def search_news(): #busca as noticias na API
    url = "https://www.tabnews.com.br/api/v1/contents"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resposta:
                if resposta.status == 200:
                    news_list = await resposta.json()
    
                    urls_list = [
                        f"Id:  {x['id']}  Url:  https://www.tabnews.com.br/{x['owner_username']}/{x['slug']}"
                        for x in news_list
                    ]
    
                    db_list = []
                    
                    for x in news_list:
                        news_info = {'id_noticia' : x['id'], 'titulo' : x['title'], 'url' : f"https://www.tabnews.com.br/{x['owner_username']}/{x['slug']}", 'autor' : x['owner_username'], 'tag' : 'tecnologia', 'postado_em' :  x['published_at']}
                    
                        db_list.append(news_info)
    

                    return "\n".join(urls_list)
                else:
                    return "Não foi possível carregar as notícias no momento."
    except Exception as e:
        print(f"Erro ao buscar notícias: {e}")
        return "Ocorreu um erro ao conectar com o serviço externo de notícias."