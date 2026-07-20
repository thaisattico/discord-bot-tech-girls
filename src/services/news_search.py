import requests

def search_news(): #busca as noticias na API
    url = "https://www.tabnews.com.br/api/v1/contents"
    resposta = requests.get(url)
    news_list = resposta.json()
    
    urls_list = [] 

    for x in news_list:
        news = "Id:  " + x['id'] + "  Url:  https://www.tabnews.com.br/" + x['owner_username'] + "/" + x['slug'] #cria as urls de cada notícia

        urls_list.append(news)


    return "\n".join(urls_list) #Devolve a lista de links (ao Agente de IA)