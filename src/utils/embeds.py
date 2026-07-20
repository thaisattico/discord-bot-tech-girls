import discord

def criar_embed_noticia(dados_json):
    """Mapeia o dicionário retornado pelo Gemini para um Embed do Discord."""

    resumo = dados_json.get("texto-resumo", "Sem resumo disponível.")
    link = dados_json.get("link-de-acesso", "")
    tags = dados_json.get("tags", [])

    tags_formatadas = " ".join([f"#{tag}" for tag in tags])

    embed = discord.Embed(
        title=" Nova Notícia de Tecnologia Aprovada!",
        url=link,  # Torna o título clicável levando direto para a notícia
        description=resumo,  # As 3 linhas de resumo fornecidas pela IA
        color=0xFF69B4,  # Cor em Hexadecimal (Exemplo: Hot Pink)
    )


    embed.add_field(
        name=" Assuntos", value=tags_formatadas, inline=False
    )


    embed.set_footer(text="Curadoria Inteligente • Tech Girls Bot")

    return embed