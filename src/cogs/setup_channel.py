import discord
from discord import app_commands
from discord.ext import commands, tasks

class SetupChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setupnews", description="Configura o canal onde as noticias serao encaminhadas")
    async def channel(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Canal para noticias configurado com sucesso!')
        print(interaction.channel.id)
        
async def setup(bot):
    await bot.add_cog(SetupChannel(bot))

