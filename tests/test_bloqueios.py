"""Casos dos bloqueios para rodar o bot completo: setup repetido, intervalo das vagas e
noticias reavaliadas pela IA a cada ciclo. Sem rede, sem Discord e sem Gemini.

Rodar da raiz do projeto: .venv/bin/python -m pytest tests/test_bloqueios.py -v
"""
import os
import shutil
import sqlite3

import pytest

from cogs import jobs_tasks, setup_jobs, setup_news, tasks
from database import database

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def banco(tmp_path, monkeypatch):
    """Banco novo numa pasta temporaria (o modulo usa caminhos relativos a pasta atual)."""
    os.makedirs(tmp_path / "src" / "database")
    shutil.copy(os.path.join(RAIZ, "src", "database", "criacao_schema.sql"), tmp_path / "src" / "database")
    monkeypatch.chdir(tmp_path)
    database.inicializar_banco()
    return tmp_path / "bot_teste.db"


def canais(caminho, tipo):
    with sqlite3.connect(caminho) as conexao:
        return conexao.execute(
            "SELECT id_guild, id_channel FROM canais_configurados WHERE tipo = ?", (tipo,)
        ).fetchall()


# --- setup repetido no mesmo servidor ---

def test_configurar_o_mesmo_tipo_duas_vezes_nao_da_erro(banco):
    database.inserir_canal_servidor("10", "100", "vagas", "2026-11-04 10:00:00")
    database.inserir_canal_servidor("10", "200", "vagas", "2026-11-04 11:00:00")
    assert canais(banco, "vagas") == [("10", "200")]


def test_vagas_e_noticias_podem_usar_canais_diferentes_no_mesmo_servidor(banco):
    database.inserir_canal_servidor("10", "100", "vagas", "2026-11-04 10:00:00")
    database.inserir_canal_servidor("10", "300", "noticias", "2026-11-04 10:00:00")
    assert canais(banco, "vagas") == [("10", "100")]
    assert canais(banco, "noticias") == [("10", "300")]


class Tarefa:
    def __init__(self):
        self.rodando = False

    def is_running(self):
        return self.rodando

    def start(self):
        self.rodando = True


class Resposta:
    def __init__(self):
        self.mensagens = []

    async def send_message(self, texto, **kwargs):
        self.mensagens.append(texto)


class Interacao:
    def __init__(self, guild, canal):
        self.guild = type("Guild", (), {"id": guild})()
        self.channel = type("Canal", (), {"id": canal})()
        self.response = Resposta()


class BotFalso:
    def __init__(self, cog):
        self.cog = cog

    def get_cog(self, nome):
        return self.cog


@pytest.mark.parametrize(
    "modulo, classe, tipo, tarefas",
    [
        (setup_jobs, "SetupJobs", "vagas", ("busca_vagas_task", "envio_vagas_task")),
        (setup_news, "SetupChannel", "noticias", ("busca_task", "envio_task")),
    ],
)
async def test_comando_de_setup_repetido_responde_e_inicia_as_tarefas(banco, modulo, classe, tipo, tarefas):
    database.inserir_canal_servidor("10", "100", tipo, "2026-11-03 10:00:00")  # ja configurado antes

    cog_tarefas = type("CogTarefas", (), {nome: Tarefa() for nome in tarefas})()
    comando = getattr(modulo, classe)(BotFalso(cog_tarefas))
    interacao = Interacao(guild=10, canal=200)

    await comando.channel.callback(comando, interacao)

    assert interacao.response.mensagens, "o comando nao respondeu no Discord"
    assert all(getattr(cog_tarefas, nome).is_running() for nome in tarefas)
    assert canais(banco, tipo) == [("10", "200")]


# --- intervalo da busca de vagas (cota da RapidAPI: 200 requisicoes/mes) ---

def test_busca_de_vagas_cabe_na_cota_mensal_da_rapidapi():
    loop = jobs_tasks.JobsTasksBot.busca_vagas_task
    minutos = (loop.hours or 0) * 60 + (loop.minutes or 0) + (loop.seconds or 0) / 60
    requisicoes_por_mes = 2 * (30 * 24 * 60 / minutos)  # pior caso: query principal + fallback
    assert requisicoes_por_mes <= 200


# --- noticias reavaliadas pela IA a cada ciclo ---

NOTICIAS = [
    {"id_noticia": "a", "titulo": "Aprovada", "url": "https://x/a"},
    {"id_noticia": "b", "titulo": "Descartada", "url": "https://x/b"},
]


@pytest.fixture
def cog_noticias(monkeypatch):
    chamadas_ia = []

    async def search_news_falso():
        return list(NOTICIAS)

    async def ia_falsa(url):
        chamadas_ia.append(url)
        return {"relevante": url.endswith("/a")}

    async def sem_espera(segundos):
        return None

    monkeypatch.setattr(tasks, "buscar_servidores", lambda tipo: [123])
    monkeypatch.setattr(tasks, "buscar_noticias", lambda id_noticia: False)  # nada enviado ainda
    monkeypatch.setattr(tasks, "search_news", search_news_falso)
    monkeypatch.setattr(tasks, "enviar_para_ia_validar", ia_falsa)
    monkeypatch.setattr(tasks.asyncio, "sleep", sem_espera)
    cog = tasks.TasksBot(bot=None)
    return cog, chamadas_ia


async def test_noticia_descartada_nao_volta_para_a_ia_no_ciclo_seguinte(cog_noticias):
    cog, chamadas_ia = cog_noticias
    await cog.busca_task.coro(cog)
    await cog.busca_task.coro(cog)
    assert chamadas_ia.count("https://x/b") == 1


async def test_noticia_aprovada_na_fila_nao_e_enfileirada_de_novo(cog_noticias):
    cog, chamadas_ia = cog_noticias
    await cog.busca_task.coro(cog)
    await cog.busca_task.coro(cog)
    assert [n["dados_banco"]["id_noticia"] for n in cog.fila_noticias] == ["a"]
    assert chamadas_ia.count("https://x/a") == 1
