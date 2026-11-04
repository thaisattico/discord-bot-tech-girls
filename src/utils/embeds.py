import discord

#Embeds para as noticias
class NoticiaView(discord.ui.View): # Botao de ver mais

    def __init__(self, url: str | None):
        super().__init__()
        if url:
            self.add_item(
                discord.ui.Button(
                    label="Ver Mais",
                    url=url,
                    style=discord.ButtonStyle.link,
                    emoji="🔗",
                )
            )


def criar_embed_noticia(
    noticia: dict,
) -> tuple[discord.Embed, discord.ui.View]:
    """Cria um Embed mapeando os campos do noticias_postadas.json."""

    titulo = noticia.get("assunto") or noticia.get("titulo") or "Notícia Tech"

    descricao = (
        noticia.get("texto-resumo")
        or noticia.get("resumo")
        or "Sem resumo disponível."
    )

    url = noticia.get("link-de-acesso") or noticia.get("link") or None

    embed = discord.Embed(
        title=titulo,
        description=descricao,
        url=url,
        color=discord.Color.purple(),
    )

    tags = noticia.get("tags") or noticia.get("topicos")
    if tags and isinstance(tags, list):
        tags_formatadas = " ".join([f"`#{tag}`" for tag in tags])
        embed.add_field(name="Tags", value=tags_formatadas, inline=False)

    embed.set_footer(text="Tech Girls • Noticias da Tecnologia")

    return embed, NoticiaView(url=url)


#Embeds para as vagas
class VagaView(discord.ui.View):
	def __init__(self, url: str, fonte: str | None = None):
		super().__init__()
		label = "Acessar vaga"
		if fonte:
			label = f"Ver no {fonte}"[:80]
		self.add_item(
			discord.ui.Button(
				label=label,
				url=url,
				style=discord.ButtonStyle.link,
				emoji="🔗",
			)
		)


def _resumir_descricao(texto: str, limite: int = 600) -> str:
	"""Corta a descricao no fim da ultima frase que cabe no limite."""
	texto = (texto or "").strip()
	if len(texto) <= limite:
		return texto
	corte = texto[: limite - 1]
	fim_frase = corte.rfind(". ")
	if fim_frase > limite // 2:
		return corte[: fim_frase + 1]
	return corte.rsplit(" ", 1)[0] + "…"


def criar_embed_vaga(vaga: dict) -> tuple[discord.Embed, discord.ui.View]:
	titulo = (vaga.get("titulo") or "Vaga Tech")[:256]
	url = vaga.get("link") or ""
	fonte = vaga.get("fonte")

	embed = discord.Embed(
		title=titulo,
		url=url,
		description=_resumir_descricao(vaga.get("descricao") or ""),
		color=discord.Color.blue(),
	)
	if vaga.get("empresa"):
		embed.add_field(name="Empresa", value=vaga["empresa"][:1024], inline=True)
	if vaga.get("localizacao"):
		embed.add_field(name="Local", value=str(vaga["localizacao"])[:1024], inline=True)
	embed.set_footer(text="Tech Girls • Vagas de Tecnologia")

	return embed, VagaView(url=url, fonte=fonte)