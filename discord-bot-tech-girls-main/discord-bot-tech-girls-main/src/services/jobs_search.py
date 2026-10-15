import os
from typing import Any
from urllib.parse import urlparse

import httpx
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

	return {
		"id_vaga": id_vaga,
		"titulo": titulo,
		"link": link,
		"localizacao": localizacao,
		"fonte": _extrair_fonte(item, link),
		"publicado_em": item.get("job_posted_at_datetime_utc") or "",
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
				# response = await client.get(JSEARCH_URL, headers=headers, params=params)
				# response.raise_for_status()
				print("[Jobs] Requisicao externa desativada temporariamente para testes locais.")
				return []

				
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