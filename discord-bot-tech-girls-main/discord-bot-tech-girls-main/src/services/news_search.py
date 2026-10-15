import aiohttp

async def search_news(): #busca as noticias na API

    url = "https://www.tabnews.com.br/api/v1/contents"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resposta:
                if resposta.status == 200:
                    news_list = await resposta.json()

                    lista_noticias = []
                   
                    for x in news_list:
                        
                        url_individual = f"https://www.tabnews.com.br/api/v1/contents/{x['owner_username']}/{x['slug']}"
                        
                        async with session.get(url_individual) as resp_post:
                            if resp_post.status == 200:
                                post_completo = await resp_post.json()
                                texto_body = post_completo.get('body', '')
                            else:
                                texto_body = ''
                        
                        news_info = {'id_noticia' : x['id'], 'titulo' : x['title'], 'url' : f"https://www.tabnews.com.br/{x['owner_username']}/{x['slug']}", 'autor' : x['owner_username'], 'tag' : 'tecnologia', 'postado_em' :  x['published_at'], 'conteudo' : texto_body}

                        lista_noticias.append(news_info)  

                    return lista_noticias

                else:
                    print("Não foi possível carregar as notícias no momento.")
                    return []

    except Exception as e:
        print(f"Erro ao buscar notícias: {e}")
        return []