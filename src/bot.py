import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

class TechNews(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        await self.load_extension("cogs.tasks")
        await self.load_extension("cogs.setup_channel")
        await self.tree.sync()
        print("Comandos sincronizados com sucesso")
        
bot = TechNews()

@bot.event
async def on_ready():
    print(f'Logado como: {bot.user}')

bot.run(TOKEN)
