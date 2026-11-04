import html
import json
import os
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")
RAPIDAPI_ENDPOINT = os.getenv("RAPIDAPI_ENDPOINT", "/search")
if not RAPIDAPI_ENDPOINT.startswith("/"):
	RAPIDAPI_ENDPOINT = f"/{RAPIDAPI_ENDPOINT}"
JSEARCH_URL = f"https://{RAPIDAPI_HOST}{RAPIDAPI_ENDPOINT}"

TECH_QUERY = os.getenv("JSEARCH_QUERY", "software engineer")
JSEARCH_FALLBACK_QUERY = os.getenv("JSEARCH_FALLBACK_QUERY", "backend developer")
JSEARCH_COUNTRY = os.getenv("JSEARCH_COUNTRY", "br")
JSEARCH_DATE_POSTED = os.getenv("JSEARCH_DATE_POSTED", "all")
JSEARCH_NUM_PAGES = os.getenv("JSEARCH_NUM_PAGES", "1")


def _texto_indica_brasil(texto: str) -> bool:
	texto_norm = (texto or "").strip().lower()
	if not texto_norm:
		return False

	tokens = ["brasil", "brazil", " br ", ", br", "- br", "br-"]
	return any(token in f" {texto_norm} " for token in tokens)


def _extrair_fonte(item: dict[str, Any], link: str) -> str:
	publisher = (item.get("job_publisher") or "").strip()
	if publisher:
		return publisher

	try:
		dominio = urlparse(link).netloc.lower().replace("www.", "")
		if not dominio:
			return "Fonte nao identificada"
		base = dominio.split(".")[0]
		return base.capitalize() if base else dominio
	except Exception:
		return "Fonte nao identificada"


def _vaga_eh_brasileira(item: dict[str, Any]) -> bool:
	country = (item.get("job_country") or "").strip().lower()
	if country in {"br", "brazil", "brasil"}:
		return True

	location = item.get("job_location") or ""
	city = item.get("job_city") or ""
	state = item.get("job_state") or ""

	return any(_texto_indica_brasil(v) for v in [location, city, state])


def _normalizar_vaga(item: dict[str, Any]) -> dict[str, Any] | None:
	link = (item.get("job_apply_link") or item.get("job_google_link") or "").strip()
	titulo = (item.get("job_title") or "").strip()

	if not link or not titulo:
		return None

	id_vaga = (item.get("job_id") or link).strip()
	localizacao = (
		item.get("job_location")
		or item.get("job_city")
		or item.get("job_state")
		or item.get("job_country")
		or "Brasil"
	)

	# Outros sites com a mesma vaga, usados se o link principal nao abrir na verificacao
	links_alternativos = []
	for opcao in item.get("apply_options") or []:
		link_opcao = (opcao.get("apply_link") or "").strip()
		if link_opcao and link_opcao != link and link_opcao not in [l["link"] for l in links_alternativos]:
			links_alternativos.append({"link": link_opcao, "fonte": (opcao.get("publisher") or "").strip() or _extrair_fonte({}, link_opcao)})

	return {
		"id_vaga": id_vaga,
		"titulo": titulo,
		"empresa": (item.get("employer_name") or "").strip(),
		"link": link,
		"localizacao": localizacao,
		"fonte": _extrair_fonte(item, link),
		"publicado_em": item.get("job_posted_at_datetime_utc") or "",
		"descricao_api": item.get("job_description") or "",
		"links_alternativos": links_alternativos,
	}


def _extrair_jobs_do_payload(payload: Any) -> list[dict[str, Any]]:
	dados: list[dict[str, Any]] = []
	if isinstance(payload, dict):
		data_field = payload.get("data", [])
		if isinstance(data_field, list):
			dados = data_field
		elif isinstance(data_field, dict):
			jobs_field = data_field.get("jobs", [])
			if isinstance(jobs_field, list):
				dados = jobs_field
	return [item for item in dados if isinstance(item, dict)]


def _filtrar_e_normalizar_vagas(dados: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
	vagas: list[dict[str, Any]] = []
	vistos: set[str] = set()

	for item in dados:
		if not _vaga_eh_brasileira(item):
			continue

		vaga = _normalizar_vaga(item)
		if not vaga:
			continue

		chave = (vaga.get("id_vaga") or vaga.get("link") or "").strip()
		if not chave or chave in vistos:
			continue

		vistos.add(chave)
		vagas.append(vaga)

		if len(vagas) >= limit:
			break

	return vagas


async def search_jobs(limit: int = 8) -> list[dict[str, Any]]:
	"""Busca vagas tech na RapidAPI e faz 1 fallback de query caso venha sem vagas BR."""
	if not RAPIDAPI_KEY:
		print("[Jobs] RAPIDAPI_KEY nao configurada no arquivo .env")
		return []

	headers = {
		"x-rapidapi-key": RAPIDAPI_KEY,
		"x-rapidapi-host": RAPIDAPI_HOST,
	}
	queries = [TECH_QUERY]
	fallback = JSEARCH_FALLBACK_QUERY.strip()
	if fallback and fallback.lower() != TECH_QUERY.strip().lower():
		queries.append(fallback)

	try:
		timeout = httpx.Timeout(20.0)
		async with httpx.AsyncClient(timeout=timeout) as client:
			for idx, query in enumerate(queries):
				params = {
					"query": query,
					"num_pages": JSEARCH_NUM_PAGES,
					"country": JSEARCH_COUNTRY,
					"date_posted": JSEARCH_DATE_POSTED,
				}
				response = await client.get(JSEARCH_URL, headers=headers, params=params)
				response.raise_for_status()

				payload = response.json()
				dados = _extrair_jobs_do_payload(payload)
				vagas = _filtrar_e_normalizar_vagas(dados, limit)

				req_num = idx + 1
				print(
					f"[Jobs] Requisicao {req_num}/{len(queries)} com query='{query}' "
					f"retornou {len(dados)} itens; {len(vagas)} vagas BR validas."
				)

				if vagas:
					return vagas

				if idx < len(queries) - 1:
					print("[Jobs] Nenhuma vaga BR valida. Executando fallback de query...")

		return []

	except httpx.HTTPStatusError as err:
		status = err.response.status_code if err.response else "desconhecido"
		body = ""
		if err.response is not None:
			try:
				body = err.response.text[:500]
			except Exception:
				body = "<falha ao ler corpo da resposta>"
		print(f"[Jobs] Erro HTTP ao consultar RapidAPI: {status} | body: {body}")
		return []
	except Exception as err:
		print(f"[Jobs] Falha ao buscar vagas na RapidAPI: {err}")
		return []


# --- Verificacao da vaga no link antes da postagem ---

NAVEGADOR_HEADERS = {
	"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
	"Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}
# Frases completas: "Vaga expirada" sozinha aparece em formularios de denuncia de vagas abertas
VAGA_ENCERRADA = re.compile(
	r"no longer accepting applications|não está mais aceitando candidaturas|esta vaga (foi encerrada|expirou|não está mais disponível)"
	r"|this job has expired|this job is no longer available",
	re.IGNORECASE,
)


def _texto_limpo(html_ou_texto: str) -> str:
	# Alguns sites (ex.: LinkedIn) mandam a descricao com o HTML escapado (&lt;p&gt;)
	texto = BeautifulSoup(html.unescape(html_ou_texto or ""), "html.parser").get_text(" ")
	return re.sub(r"\s+", " ", texto).strip()


def _job_posting_da_pagina(soup: BeautifulSoup) -> dict[str, Any] | None:
	"""Le o bloco JSON-LD padrao (schema.org/JobPosting) que a maioria dos sites de vaga publica."""
	for script in soup.find_all("script", type="application/ld+json"):
		try:
			dados = json.loads(script.string or "")
		except (json.JSONDecodeError, TypeError):
			continue
		candidatos = dados if isinstance(dados, list) else dados.get("@graph", [dados])
		for item in candidatos:
			if isinstance(item, dict) and item.get("@type") == "JobPosting":
				return item
	return None


def _prazo_vencido(posting: dict[str, Any]) -> bool:
	prazo = posting.get("validThrough")
	if not prazo:
		return False
	try:
		data = datetime.fromisoformat(str(prazo).replace("Z", "+00:00"))
	except ValueError:
		return False
	if data.tzinfo is None:
		data = data.replace(tzinfo=timezone.utc)
	return data < datetime.now(timezone.utc)


def _descricao_conferida(pagina: str, descricao_api: str) -> str | None:
	"""Devolve a descricao confirmada na pagina, ou None se a pagina nao confirma a vaga aberta."""
	soup = BeautifulSoup(pagina, "html.parser")
	if VAGA_ENCERRADA.search(soup.get_text(" ")):
		return None

	posting = _job_posting_da_pagina(soup)
	if posting:
		if _prazo_vencido(posting):
			return None
		descricao = _texto_limpo(posting.get("description") or "")
		if descricao:
			return descricao

	# Sem JSON-LD: aceita se o comeco da descricao da API aparece no texto da pagina
	descricao_api = _texto_limpo(descricao_api)
	trecho = descricao_api[:60]
	if trecho and trecho in _texto_limpo(pagina):
		return descricao_api
	return None


async def verificar_vaga(vaga: dict[str, Any]) -> dict[str, Any] | None:
	"""Acessa o link da vaga (e os alternativos) e devolve a vaga com a descricao conferida.
	Retorna None quando nenhum link abre com a vaga aberta: nesse caso ela nao deve ser postada."""
	opcoes = [{"link": vaga.get("link"), "fonte": vaga.get("fonte")}] + list(vaga.get("links_alternativos") or [])

	async with httpx.AsyncClient(timeout=httpx.Timeout(15.0), follow_redirects=True, headers=NAVEGADOR_HEADERS) as client:
		for opcao in opcoes:
			if not opcao.get("link"):
				continue
			try:
				response = await client.get(opcao["link"])
			except httpx.HTTPError as err:
				print(f"[Jobs] Link da vaga nao abriu ({opcao['link']}): {err}")
				continue
			if response.status_code != 200:
				print(f"[Jobs] Link da vaga respondeu {response.status_code}: {opcao['link']}")
				continue

			descricao = _descricao_conferida(response.text, vaga.get("descricao_api") or "")
			if descricao:
				return {**vaga, "link": opcao["link"], "fonte": opcao.get("fonte") or vaga.get("fonte"), "descricao": descricao}

	print(f"[Jobs] Vaga nao confirmada em nenhum link, nao sera postada: {vaga.get('titulo')}")
	return None
