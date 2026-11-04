"""Casos de teste da busca de vagas (RapidAPI/JSearch simulada, sem rede).

Rodar da raiz do projeto: .venv/bin/python -m pytest tests/test_vagas.py -v
"""
import httpx
import pytest

from services import jobs_search
from cogs import jobs_tasks


def vaga_api(job_id, titulo="Desenvolvedora Python", pais="BR", link=None, **extra):
    item = {
        "job_id": job_id,
        "job_title": titulo,
        "job_apply_link": link if link is not None else f"https://vagas.exemplo.com/{job_id}",
        "job_country": pais,
        "job_city": "São Paulo" if pais == "BR" else "Lisboa",
        "job_publisher": "LinkedIn",
        "job_posted_at_datetime_utc": "2026-11-01T10:00:00.000Z",
    }
    item.update(extra)
    return item


@pytest.fixture
def api(monkeypatch):
    """Simula a RapidAPI: cada chamada devolve o proximo payload da lista `respostas`."""
    estado = {"respostas": [], "requisicoes": []}

    def handler(request: httpx.Request) -> httpx.Response:
        estado["requisicoes"].append(request)
        status, payload = estado["respostas"][len(estado["requisicoes"]) - 1]
        return httpx.Response(status, json=payload)

    cliente_original = httpx.AsyncClient

    def cliente_falso(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        return cliente_original(*args, **kwargs)

    monkeypatch.setattr(jobs_search.httpx, "AsyncClient", cliente_falso)
    monkeypatch.setattr(jobs_search, "RAPIDAPI_KEY", "chave-de-teste")
    monkeypatch.setattr(jobs_search, "TECH_QUERY", "software engineer")
    monkeypatch.setattr(jobs_search, "JSEARCH_FALLBACK_QUERY", "backend developer")
    return estado


# --- search_jobs ---

async def test_retorna_vagas_brasileiras(api):
    api["respostas"] = [(200, {"data": [vaga_api("1"), vaga_api("2")]})]
    vagas = await jobs_search.search_jobs()
    assert [v["id_vaga"] for v in vagas] == ["1", "2"]
    assert vagas[0]["fonte"] == "LinkedIn"
    assert vagas[0]["link"] == "https://vagas.exemplo.com/1"


async def test_aceita_payload_search_v2_com_data_jobs(api):
    api["respostas"] = [(200, {"data": {"jobs": [vaga_api("1")]}})]
    vagas = await jobs_search.search_jobs()
    assert [v["id_vaga"] for v in vagas] == ["1"]


async def test_descarta_vagas_de_fora_do_brasil(api):
    api["respostas"] = [(200, {"data": [vaga_api("1", pais="PT"), vaga_api("2")]})]
    vagas = await jobs_search.search_jobs()
    assert [v["id_vaga"] for v in vagas] == ["2"]


async def test_aceita_vaga_com_brasil_so_na_localizacao(api):
    item = vaga_api("1", pais="", job_city="", job_location="Remoto, Brasil")
    api["respostas"] = [(200, {"data": [item]})]
    vagas = await jobs_search.search_jobs()
    assert [v["id_vaga"] for v in vagas] == ["1"]


async def test_remove_vagas_duplicadas(api):
    api["respostas"] = [(200, {"data": [vaga_api("1"), vaga_api("1"), vaga_api("2")]})]
    vagas = await jobs_search.search_jobs()
    assert [v["id_vaga"] for v in vagas] == ["1", "2"]


async def test_respeita_o_limite(api):
    api["respostas"] = [(200, {"data": [vaga_api(str(i)) for i in range(10)]})]
    vagas = await jobs_search.search_jobs(limit=3)
    assert len(vagas) == 3


async def test_ignora_vaga_sem_link_ou_sem_titulo(api):
    sem_link = vaga_api("1", link="", job_google_link="")
    sem_titulo = vaga_api("2", titulo="")
    api["respostas"] = [(200, {"data": [sem_link, sem_titulo, vaga_api("3")]})]
    vagas = await jobs_search.search_jobs()
    assert [v["id_vaga"] for v in vagas] == ["3"]


async def test_usa_query_de_fallback_quando_a_primeira_nao_traz_vaga_br(api):
    api["respostas"] = [
        (200, {"data": [vaga_api("1", pais="US")]}),
        (200, {"data": [vaga_api("2")]}),
    ]
    vagas = await jobs_search.search_jobs()
    assert [v["id_vaga"] for v in vagas] == ["2"]
    assert [r.url.params["query"] for r in api["requisicoes"]] == ["software engineer", "backend developer"]


async def test_sem_vaga_br_nas_duas_queries_retorna_lista_vazia(api):
    api["respostas"] = [(200, {"data": []}), (200, {"data": []})]
    assert await jobs_search.search_jobs() == []
    assert len(api["requisicoes"]) == 2


async def test_envia_chave_e_filtros_para_a_api(api):
    api["respostas"] = [(200, {"data": [vaga_api("1")]})]
    await jobs_search.search_jobs()
    req = api["requisicoes"][0]
    assert req.headers["x-rapidapi-key"] == "chave-de-teste"
    assert req.url.params["country"] == "br"


async def test_erro_http_da_api_retorna_lista_vazia(api):
    api["respostas"] = [(429, {"message": "Too many requests"})]
    assert await jobs_search.search_jobs() == []


async def test_sem_chave_da_api_retorna_lista_vazia(monkeypatch):
    monkeypatch.setattr(jobs_search, "RAPIDAPI_KEY", None)
    assert await jobs_search.search_jobs() == []


# --- tarefa periodica (cogs/jobs_tasks.py) ---

def cog_de_vagas(monkeypatch, vagas):
    async def busca_falsa(limit=8):
        return vagas

    monkeypatch.setattr(jobs_tasks, "buscar_servidores", lambda tipo: [123])
    monkeypatch.setattr(jobs_tasks, "search_jobs", busca_falsa)
    return jobs_tasks.JobsTasksBot(bot=None)


async def test_tarefa_nao_quebra_quando_a_busca_nao_tem_chave(monkeypatch):
    monkeypatch.setattr(jobs_tasks, "buscar_servidores", lambda tipo: [123])
    monkeypatch.setattr(jobs_search, "RAPIDAPI_KEY", None)
    cog = jobs_tasks.JobsTasksBot(bot=None)
    await cog.busca_vagas_task.coro(cog)
    assert cog.fila_vagas == []


async def test_tarefa_enfileira_vagas_novas_sem_repetir(monkeypatch):
    vagas = [{"id_vaga": "1", "titulo": "A", "link": "x"}, {"id_vaga": "2", "titulo": "B", "link": "y"}]
    cog = cog_de_vagas(monkeypatch, vagas)
    await cog.busca_vagas_task.coro(cog)
    await cog.busca_vagas_task.coro(cog)
    assert [v["id_vaga"] for v in cog.fila_vagas] == ["1", "2"]


# --- inicializacao do bot (src/bot.py) ---

async def test_bot_carrega_o_modulo_de_vagas(monkeypatch):
    import bot as modulo_bot

    carregadas = []

    async def load_extension_falso(nome):
        carregadas.append(nome)

    async def sync_falso(*args, **kwargs):
        return []

    instancia = modulo_bot.TechNews()
    monkeypatch.setattr(modulo_bot, "inicializar_banco", lambda: None)
    monkeypatch.setattr(instancia, "load_extension", load_extension_falso)
    monkeypatch.setattr(instancia.tree, "sync", sync_falso)

    await instancia.setup_hook()

    assert "cogs.jobs_tasks" in carregadas
    assert "cogs.setup_jobs" in carregadas
