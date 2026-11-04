"""Casos da vaga postada com funcao, empresa e descricao conferida no link da vaga.
Paginas simuladas com httpx.MockTransport: sem rede e sem Discord.

Rodar da raiz do projeto: .venv/bin/python -m pytest tests/test_vaga_verificada.py -v
"""
import json

import httpx
import pytest

from cogs import jobs_tasks
from services import jobs_search
from utils.embeds import criar_embed_vaga

DESCRICAO = (
    "<p>Buscamos uma pessoa desenvolvedora backend para construir APIs em Python. "
    "Você vai trabalhar com FastAPI, PostgreSQL e filas. Requisitos: 3 anos de experiência.</p>"
)


def item_api(**extra):
    item = {
        "job_id": "1",
        "job_title": "Desenvolvedora Backend Python",
        "employer_name": "Empresa Exemplo",
        "job_apply_link": "https://vagas.exemplo.com/1",
        "job_country": "BR",
        "job_city": "São Paulo",
        "job_publisher": "LinkedIn",
        "job_description": "Buscamos uma pessoa desenvolvedora backend para construir APIs em Python. Requisitos: 3 anos.",
        "apply_options": [
            {"publisher": "LinkedIn", "apply_link": "https://vagas.exemplo.com/1"},
            {"publisher": "Gupy", "apply_link": "https://gupy.exemplo.com/1"},
        ],
    }
    item.update(extra)
    return item


def pagina_json_ld(descricao=DESCRICAO, valid_through=None):
    posting = {"@context": "https://schema.org", "@type": "JobPosting", "title": "Dev", "description": descricao}
    if valid_through:
        posting["validThrough"] = valid_through
    return f'<html><head><script type="application/ld+json">{json.dumps(posting)}</script></head><body>Vaga</body></html>'


@pytest.fixture
def paginas(monkeypatch):
    """Simula os sites das vagas: url -> (status, html)."""
    mapa = {}
    acessadas = []

    def handler(request: httpx.Request) -> httpx.Response:
        acessadas.append(str(request.url))
        status, html = mapa.get(str(request.url), (404, "nao encontrada"))
        return httpx.Response(status, text=html)

    cliente_original = httpx.AsyncClient

    def cliente_falso(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        return cliente_original(*args, **kwargs)

    monkeypatch.setattr(jobs_search.httpx, "AsyncClient", cliente_falso)
    return mapa, acessadas


def vaga_normalizada(**extra):
    return jobs_search._normalizar_vaga(item_api(**extra))


# --- dados da vaga vindos da API ---

def test_vaga_normalizada_traz_a_empresa():
    assert vaga_normalizada()["empresa"] == "Empresa Exemplo"


def test_vaga_normalizada_guarda_os_links_alternativos():
    links = vaga_normalizada()["links_alternativos"]
    assert {"link": "https://gupy.exemplo.com/1", "fonte": "Gupy"} in links
    assert all(l["link"] != "https://vagas.exemplo.com/1" for l in links)  # sem repetir o principal


# --- conferencia no link antes de postar ---

async def test_usa_a_descricao_da_pagina_da_vaga(paginas):
    mapa, _ = paginas
    mapa["https://vagas.exemplo.com/1"] = (200, pagina_json_ld())
    vaga = await jobs_search.verificar_vaga(vaga_normalizada())
    assert vaga["descricao"].startswith("Buscamos uma pessoa desenvolvedora backend")
    assert "<p>" not in vaga["descricao"]


async def test_aceita_pagina_sem_json_ld_que_mostra_a_descricao_da_api(paginas):
    mapa, _ = paginas
    html = "<html><body><h1>Vaga</h1><p>Buscamos uma pessoa desenvolvedora backend para construir APIs em Python. Requisitos: 3 anos.</p></body></html>"
    mapa["https://vagas.exemplo.com/1"] = (200, html)
    vaga = await jobs_search.verificar_vaga(vaga_normalizada())
    assert vaga["descricao"].startswith("Buscamos uma pessoa desenvolvedora backend")


async def test_link_bloqueado_tenta_o_link_alternativo(paginas):
    mapa, _ = paginas
    mapa["https://vagas.exemplo.com/1"] = (401, "bloqueado")
    mapa["https://gupy.exemplo.com/1"] = (200, pagina_json_ld())
    vaga = await jobs_search.verificar_vaga(vaga_normalizada())
    assert vaga["link"] == "https://gupy.exemplo.com/1"
    assert vaga["fonte"] == "Gupy"


async def test_nenhum_link_confirma_a_vaga_entao_nao_posta(paginas):
    mapa, _ = paginas
    mapa["https://vagas.exemplo.com/1"] = (401, "bloqueado")
    mapa["https://gupy.exemplo.com/1"] = (200, "<html><body>Outra coisa</body></html>")
    assert await jobs_search.verificar_vaga(vaga_normalizada()) is None


async def test_vaga_com_prazo_vencido_nao_e_postada(paginas):
    mapa, _ = paginas
    mapa["https://vagas.exemplo.com/1"] = (200, pagina_json_ld(valid_through="2020-01-01T00:00:00Z"))
    mapa["https://gupy.exemplo.com/1"] = (404, "")
    assert await jobs_search.verificar_vaga(vaga_normalizada()) is None


async def test_vaga_encerrada_na_pagina_nao_e_postada(paginas):
    mapa, _ = paginas
    html = pagina_json_ld().replace("<body>Vaga</body>", "<body>Esta vaga não está mais aceitando candidaturas</body>")
    mapa["https://vagas.exemplo.com/1"] = (200, html)
    mapa["https://gupy.exemplo.com/1"] = (404, "")
    assert await jobs_search.verificar_vaga(vaga_normalizada()) is None


# --- mensagem no Discord ---

def test_embed_mostra_funcao_empresa_e_descricao():
    vaga = {**vaga_normalizada(), "descricao": "Buscamos uma pessoa desenvolvedora backend. " * 40}
    embed, _ = criar_embed_vaga(vaga)
    assert embed.title == "Desenvolvedora Backend Python"
    assert {"name": "Empresa", "value": "Empresa Exemplo"} in [{"name": f.name, "value": f.value} for f in embed.fields]
    assert embed.description.startswith("Buscamos uma pessoa desenvolvedora backend.")
    assert len(embed.description) <= 600


# --- envio: so posta vaga conferida ---

class Canal:
    def __init__(self):
        self.enviados = []

    async def send(self, embed=None, view=None):
        self.enviados.append(embed)


async def test_envio_pula_vaga_nao_confirmada_e_posta_a_proxima(monkeypatch):
    canal = Canal()
    bot = type("Bot", (), {"get_channel": lambda self, id_canal: canal})()

    async def verificar_falso(vaga):
        return {**vaga, "descricao": "Descrição conferida."} if vaga["id_vaga"] == "2" else None

    monkeypatch.setattr(jobs_tasks, "buscar_servidores", lambda tipo: [123])
    monkeypatch.setattr(jobs_tasks, "verificar_vaga", verificar_falso, raising=False)

    cog = jobs_tasks.JobsTasksBot(bot)
    cog.fila_vagas = [
        {**vaga_normalizada(), "id_vaga": "1", "titulo": "Encerrada"},
        {**vaga_normalizada(), "id_vaga": "2", "titulo": "Aberta"},
    ]
    await cog.envio_vagas_task.coro(cog)

    assert [e.title for e in canal.enviados] == ["Aberta"]
    assert canal.enviados[0].description == "Descrição conferida."


# --- casos achados com vagas reais (2026-11-04) ---

async def test_descricao_com_html_escapado_vira_texto(paginas):
    mapa, _ = paginas
    mapa["https://vagas.exemplo.com/1"] = (200, pagina_json_ld(descricao="&lt;p&gt;Tecnologia que transforma&lt;/p&gt;&lt;p&gt;Na empresa&lt;/p&gt;"))
    vaga = await jobs_search.verificar_vaga(vaga_normalizada())
    assert vaga["descricao"] == "Tecnologia que transforma Na empresa"


async def test_opcao_vaga_expirada_no_formulario_de_denuncia_nao_bloqueia(paginas):
    mapa, _ = paginas
    html = pagina_json_ld().replace(
        "<body>Vaga</body>",
        "<body>Por que deseja denunciar esta vaga? Vaga falsa ou fraude Vaga expirada Informação incorreta</body>",
    )
    mapa["https://vagas.exemplo.com/1"] = (200, html)
    assert await jobs_search.verificar_vaga(vaga_normalizada()) is not None
