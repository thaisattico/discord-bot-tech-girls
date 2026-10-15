import datetime
from discord.ext import commands, tasks
from services.news_search import search_news
from services.app_validador import enviar_para_ia_validar
from database.database import buscar_noticias, buscar_servidores, inserir_noticia
import asyncio
from utils.embeds import criar_embed_noticia

class TasksBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fila_noticias = []
        # self.search_task.start() sera inicializada pelo /setupnews

    def cog_unload(self):
        self.busca_task.cancel()
        self.envio_task.cancel()

    @tasks.loop(minutes=1)
    async def busca_task(self):
        print("\n\nTarefa de automatização Rodando!")
        
        canais = buscar_servidores("noticias")
        if canais == []: #Por seguranca caso rode sem o setupnews
            print("\nNenhum canal registrado no banco, cancelando execução das tasks")
            return
        
        noticias = await search_news()
        for noticia in reversed(noticias):
            if buscar_noticias(noticia['id_noticia']): #Busca as noticias no banco para ver se existem, se sim, pula
                continue
            
            # Envia para a IA
            resultado_ia = await enviar_para_ia_validar(noticia['url'])
            #resultado_ia = await enviar_para_ia_validar(noticia) para retornar o dicionario inteiro com o conteudo + titulo,etc
            
            await asyncio.sleep(5) #Pausa para nao estourar o limite de requisicoes
            
            #Manda o resultado enviado pela IA para uma fila de noticias
            if resultado_ia and resultado_ia.get("relevante") is True:
                self.fila_noticias.append({
                    "resultado_ia": resultado_ia,
                    "dados_banco": noticia
                })

    @tasks.loop(minutes=1)
    async def envio_task(self):
        if not self.fila_noticias:
            return
            
        canais = buscar_servidores("noticias")
        
        noticia_para_enviar = self.fila_noticias.pop(0)
        resultado_ia = noticia_para_enviar["resultado_ia"]
        noticia = noticia_para_enviar["dados_banco"]
        
        embed, view = criar_embed_noticia(resultado_ia)
        
        for id_canal in canais:
            canal = self.bot.get_channel(id_canal)
            if canal:
                await canal.send(embed=embed, view=view)
        
        #Insere a noticia encaminhada no banco para evitar duplicacao posterior
        inserir_noticia(
            noticia['id_noticia'], 
            noticia['titulo'], 
            noticia['autor'], 
            noticia['url'], 
            noticia['postado_em'], 
            noticia['tag']
        )
        print(f"\nNotícia enviada e salva: {noticia['titulo']}")

    @busca_task.error
    async def busca_task_error(self, error):
        print(f"\nERRO NA TASK: {error}")
        
async def setup(bot):
    await bot.add_cog(TasksBot(bot))