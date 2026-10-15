import discord
from discord import app_commands
from discord.ext import commands
from database.database import inserir_canal_servidor
from datetime import datetime

class SetupChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setupnews", description="Configura o canal onde as noticias serao encaminhadas")
    @app_commands.checks.has_permissions(administrator=True)
    async def channel(self, interaction: discord.Interaction):
        
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        inserir_canal_servidor(id_guild=str(interaction.guild.id), id_channel=str(interaction.channel.id), tipo="noticias", criado_em=data_atual)
        
        await interaction.response.send_message(f'Canal para noticias configurado com sucesso!')
        # print(interaction.channel.id, interaction.guild.id) Mostra o id do canal e do servidor no console
        
        task_cog = self.bot.get_cog("TasksBot")
        
        if task_cog:
            #Inicia a task de busca se ela não estiver rodando
            if not task_cog.busca_task.is_running():
                task_cog.busca_task.start()
                
            #Inicia a task de envio se ela não estiver rodando
            if not task_cog.envio_task.is_running():
                task_cog.envio_task.start()

    #Da erro caso alguem nao administrador tente rodar o comando
    @channel.error
    async def channel_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(f'Apenas administradores podem utilizar esse comando!', ephemeral=True)
          

async def setup(bot):
    await bot.add_cog(SetupChannel(bot))