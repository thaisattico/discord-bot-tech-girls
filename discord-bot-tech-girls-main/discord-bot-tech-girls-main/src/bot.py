import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from database.database import inicializar_banco

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
DEV_GUILD_ID= os.getenv("DEV_GUILD_ID")

GUILD_ID = discord.Object(id=int(DEV_GUILD_ID)) if DEV_GUILD_ID else None #Remover para tornar comando do bot globais *remover todos os GUILD_ID

intents = discord.Intents.default()
intents.message_content = True

class TechNews(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        inicializar_banco() #Inicia as tabelas do SQLite se elas nao existirem
        
        await self.load_extension("cogs.tasks")
        print("Tasks de automatizacao conectada com sucesso!")
        
        await self.load_extension("cogs.setup_news")
        await self.load_extension("cogs.setup_jobs")
        # await self.load_extension("cogs.teste_embed")
        
        if GUILD_ID:
            self.tree.clear_commands(guild=GUILD_ID)
            await self.tree.sync(guild=GUILD_ID)

        synced = await self.tree.sync()
        
        print(f"Comandos ativos: {[cmd.name for cmd in synced]}")
        
bot = TechNews()

@bot.event
async def on_ready():
    print(f'Logado como: {bot.user}')

bot.run(TOKEN)