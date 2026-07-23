import json
import os
import discord
from discord import app_commands
from discord.ext import commands
from utils.embeds import criar_embed_noticia

# Caminho para buscar o json
CAMINHO_JSON = os.path.join(
    "Validador_IA", "dados_teste", "noticias_postadas.json"
)


class TestEmbedCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="testarembed",
        description="Exibe a última notícia salva no noticias_postadas.json.",
    )
    async def testar_embed(self, interaction: discord.Interaction):
        if not os.path.exists(CAMINHO_JSON):
            await interaction.response.send_message(
                "Arquivo noticias_postadas.json não foi encontrado.",
                ephemeral=True,
            )
            return

        try:
            with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
                dados = json.load(f)

            print("Conteúdo lido do JSON:", dados)

            if isinstance(dados, list) and len(dados) > 0:
                noticia = dados[-1]
            elif isinstance(dados, dict):
                noticia = dados
            else:
                await interaction.response.send_message(
                    "O arquivo de notícias está vazio.", ephemeral=True
                )
                return

            embed, view = criar_embed_noticia(noticia)
            
            await interaction.response.send_message(embed=embed, view=view)

        except Exception as e:
            await interaction.response.send_message(
                f"Erro ao ler o arquivo de notícias: {e}", ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(TestEmbedCog(bot))