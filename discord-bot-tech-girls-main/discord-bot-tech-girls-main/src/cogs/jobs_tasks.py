import discord
from discord.ext import commands, tasks
from database.database import buscar_servidores
from services.jobs_search import search_jobs
from utils.embeds import criar_embed_vaga

class JobsTasksBot(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.fila_vagas: list[dict] = []
		self.vagas_vistas: set[str] = set()

	#async def cog_load(self):
		#if not self.busca_vagas_task.is_running():
			#self.busca_vagas_task.start()
		#if not self.envio_vagas_task.is_running():
			#self.envio_vagas_task.start()

	def cog_unload(self):
		if self.busca_vagas_task.is_running():
			self.busca_vagas_task.cancel()
		if self.envio_vagas_task.is_running():
			self.envio_vagas_task.cancel()

	@tasks.loop(minutes=1)  # Executa a requisicao de busca a cada 4 horas
	async def busca_vagas_task(self):
		canais = buscar_servidores("vagas")
		if not canais:
			print("[JobsTask] Nenhum canal configurado. Busca cancelada neste ciclo.")
			return

		vagas = await search_jobs(limit=8)
		adicionadas = 0

		for vaga in vagas:
			chave = (vaga.get("id_vaga") or vaga.get("link") or "").strip()
			if not chave or chave in self.vagas_vistas:
				continue

			self.vagas_vistas.add(chave)
			self.fila_vagas.append(vaga)
			adicionadas += 1

		print(
			f"[JobsTask] Busca concluida com 1 requisicao externa. "
			f"Recebidas: {len(vagas)} | Enfileiradas: {adicionadas}"
		)

	@busca_vagas_task.before_loop
	async def before_busca_vagas_task(self):
		await self.bot.wait_until_ready()

	@busca_vagas_task.error
	async def busca_vagas_task_error(self, error):
		print(f"[JobsTask] Erro na busca de vagas: {error}")

	@tasks.loop(minutes=1)
	async def envio_vagas_task(self):
		if not self.fila_vagas:
			return

		canais = buscar_servidores("vagas")
		if not canais:
			return

		vaga = self.fila_vagas.pop(0)
		embed, view = criar_embed_vaga(vaga)

		enviados = 0
		for id_canal in canais:
			canal = self.bot.get_channel(id_canal)
			if canal:
				await canal.send(embed=embed, view=view)
				enviados += 1

		print(f"[JobsTask] Vaga enviada para {enviados} canal(is): {vaga.get('titulo')}")

	@envio_vagas_task.before_loop
	async def before_envio_vagas_task(self):
		await self.bot.wait_until_ready()

	@envio_vagas_task.error
	async def envio_vagas_task_error(self, error):
		print(f"[JobsTask] Erro no envio de vagas: {error}")


async def setup(bot: commands.Bot):
	await bot.add_cog(JobsTasksBot(bot))
