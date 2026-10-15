# Tasks mas em forma de teste, sem banco de dados e com tempo de execucao menor

import asyncio
from discord.ext import commands, tasks
from services.news_search import search_news
from services.app_validador import enviar_para_ia_validar
from utils.embeds import criar_embed_noticia

def buscar_noticias(id_noticia):
    return False # Simula que tudo é notícia nova (sem estar no banco)

def buscar_servidores():
    return [1528571533889634415] 

def inserir_noticias(*args):
    print("Notícia salva com sucesso!") #O banco e fake, no arquivo de testes

class TasksTeste(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #self.search_task_teste.start()

    def cog_unload(self):
        self.search_task_teste.cancel()

    @tasks.loop(minutes=2)
    async def search_task_teste(self):
        print("\n---------TESTE EXECUTANDO--------")
        urls_list, dados_banco = await search_news()
        
        for noticia in dados_banco[:10]: 
            print(f"\nTitulo da noticia {noticia['titulo']}")
            
            if buscar_noticias(noticia['id_noticia']):
                print("-> Notícia enviada anteriormente, pulando...")
                continue
            
            # Envia para a IA
            resultado_ia = await enviar_para_ia_validar(noticia['url'])
            
            if resultado_ia and resultado_ia.get("relevante") is True:
                embed,view = criar_embed_noticia(resultado_ia)
                                
                canais = buscar_servidores()
                            
                for id_canal in canais:
                    canal = self.bot.get_channel(id_canal)
                    if canal:
                        await canal.send(embed=embed, view=view)
                        print("-> Mensagem enviada no Discord!")
                
                inserir_noticias(
                    noticia['id_noticia'], 
                    noticia['titulo'], 
                    noticia['autor'], 
                    noticia['url'], 
                    noticia['postado_em'], 
                    noticia['tag']
                )

            print("-> Pausa de 10 segundos antes da proxima noticia")
            await asyncio.sleep(10)

    # Roda assim que o bot fica online
    @search_task_teste.before_loop
    async def before_search_task(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(TasksTeste(bot))