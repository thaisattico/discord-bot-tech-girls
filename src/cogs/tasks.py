import datetime
from discord.ext import commands, tasks
from services.news_search import search_news #Busca a funcao search news no services

fuso_br = datetime.timezone(datetime.timedelta(hours=-3)) #Definindo o fuso-horario para Brasil

#Task de buscar noticia "Acorda" a cada 6 horas 
times = [
    datetime.time(hour=8, tzinfo=fuso_br),
    datetime.time(hour=14, tzinfo=fuso_br),
    datetime.time(hour=20, tzinfo=fuso_br),
    datetime.time(hour=2, tzinfo=fuso_br)
]

class SearchNews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.search_task.start()

    def cog_unload(self):
        self.search_task.cancel()

    @tasks.loop(time=times)
    async def search_task(self):
        print("Tarefa Rodando!")
        search_result = search_news()
        
async def setup(bot):
    await bot.add_cog(SearchNews(bot))