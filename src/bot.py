import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

GUILD_ID = discord.Object(id=1528106461362651338)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

class TechNews(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        await self.load_extension("cogs.tasks")
        await self.load_extension("cogs.setup_channel")
        await self.load_extension("cogs.teste_embed")
        
        self.tree.copy_global_to(guild=GUILD_ID) #Copia os comandos globais para o servidor de testes

        synced = await self.tree.sync(guild=GUILD_ID) #Sincroniza os comandos diretamente no servidor
        
        print(f"Comandos prontos e ativos: {[cmd.name for cmd in synced]}")
        
bot = TechNews()

@bot.event
async def on_ready():
    print(f'Logado como: {bot.user}')

bot.run(TOKEN)
