import asyncio
import json
import os
import re
import urllib.request
from typing import Any, Dict, Optional
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Carrega variáveis de ambiente (.env)
load_dotenv()


def _retorno_invalido(motivo: str) -> Dict[str, Any]:
    """Retorno padronizado para respostas inválidas do validador."""
    return {"relevante": False, "justificativa": motivo}


def _url_valida(url: str) -> bool:
    """Valida se a URL está em formato HTTP/HTTPS simples."""
    return bool(re.match(r"^https?://\S+$", url.strip()))


def _normalizar_resumo(texto: str) -> str:
    """Normaliza o resumo preservando as quebras de linha relevantes."""
    linhas = [linha.strip() for linha in texto.replace("\r\n", "\n").split("\n")]
    linhas = [linha for linha in linhas if linha]
    return "\n".join(linhas)


def _validar_resumo_3_linhas(texto: str, max_palavras_por_linha: int = 15) -> tuple[bool, Optional[str], Optional[str]]:
    """Valida se o resumo possui exatamente 3 linhas e até 15 palavras por linha."""
    if not isinstance(texto, str) or not texto.strip():
        return False, None, "Campo 'texto-resumo' ausente ou vazio."

    resumo = _normalizar_resumo(texto)
    linhas = resumo.split("\n")

    if len(linhas) != 3:
        return False, None, "Campo 'texto-resumo' deve conter exatamente 3 linhas."

    for idx, linha in enumerate(linhas, start=1):
        palavras = linha.split()
        if len(palavras) > max_palavras_por_linha:
            return (
                False,
                None,
                f"Linha {idx} de 'texto-resumo' excede {max_palavras_por_linha} palavras.",
            )

    return True, resumo, None


def _validar_tags(tags: Any, max_tags: int = 3) -> tuple[bool, Optional[list[str]], Optional[str]]:
    """Valida e normaliza as tags para lista curta de strings."""
    if not isinstance(tags, list):
        return False, None, "Campo 'tags' deve ser uma lista."

    tags_normalizadas: list[str] = []
    for item in tags:
        if not isinstance(item, str):
            return False, None, "Todas as 'tags' devem ser strings."

        tag_limpa = item.strip()
        if tag_limpa:
            tags_normalizadas.append(tag_limpa)

    # Remove duplicadas preservando a ordem
    tags_unicas = list(dict.fromkeys(tags_normalizadas))

    if not tags_unicas:
        return False, None, "Campo 'tags' não pode estar vazio."

    if len(tags_unicas) > max_tags:
        return False, None, f"Campo 'tags' deve conter no máximo {max_tags} itens."

    return True, tags_unicas, None


def _validar_payload_rejeitado(payload: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Valida o contrato para respostas rejeitadas."""
    justificativa = payload.get("justificativa")
    if not isinstance(justificativa, str) or not justificativa.strip():
        return False, "Campo 'justificativa' é obrigatório quando relevante=false."
    return True, None


def _validar_payload_aprovado(payload: Dict[str, Any], target_url: str) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Valida e normaliza o contrato para respostas aprovadas."""
    titulo = payload.get("titulo")
    if not isinstance(titulo, str) or not titulo.strip():
        return False, None, "Campo 'titulo' é obrigatório quando relevante=true."

    ok_tags, tags_validadas, erro_tags = _validar_tags(payload.get("tags"))
    if not ok_tags:
        return False, None, erro_tags

    ok_resumo, resumo_normalizado, erro_resumo = _validar_resumo_3_linhas(payload.get("texto-resumo"))
    if not ok_resumo:
        return False, None, erro_resumo

    payload_final = {
        "relevante": True,
        "titulo": titulo.strip(),
        "tags": tags_validadas,
        "texto-resumo": resumo_normalizado,
        "link-de-acesso": target_url,
    }

    if not _url_valida(payload_final["link-de-acesso"]):
        return False, None, "Campo 'link-de-acesso' inválido."

    return True, payload_final, None


def _validar_payload_ia(payload: Any, target_url: str) -> Dict[str, Any]:
    """Orquestra a validação final do payload retornado pela IA."""
    if not isinstance(payload, dict):
        return _retorno_invalido("Resposta da IA deve ser um objeto JSON.")

    if "relevante" not in payload or not isinstance(payload.get("relevante"), bool):
        return _retorno_invalido("Campo 'relevante' ausente ou inválido no retorno da IA.")

    if payload["relevante"] is False:
        ok_rejeitado, erro_rejeitado = _validar_payload_rejeitado(payload)
        if not ok_rejeitado:
            return _retorno_invalido(erro_rejeitado or "Payload rejeitado inválido.")

        return {
            "relevante": False,
            "justificativa": payload["justificativa"].strip(),
        }

    ok_aprovado, payload_aprovado, erro_aprovado = _validar_payload_aprovado(payload, target_url)
    if not ok_aprovado:
        return _retorno_invalido(erro_aprovado or "Payload aprovado inválido.")

    return payload_aprovado or _retorno_invalido("Falha ao normalizar resposta aprovada.")


def _obter_caminho_prompt() -> str:
    """
    Retorna o caminho absoluto dinâmico para o arquivo docs/leitura_de_noticias.md,
    independentemente de onde o script seja executado.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_dir, "docs", "leitura_de_noticias.md")


def extrair_url(url_ou_texto: str) -> str:
    """
    Sanitiza e extrai uma URL HTTP/HTTPS válida de uma string.
    Suporta textos formatados do TabNews (ex: 'Id: ... Url: https://...').
    """
    match = re.search(r"https?://[^\s]+", url_ou_texto)
    if match:
        return match.group(0)
    return url_ou_texto.strip()


def extrair_conteudo_pagina(url: str) -> Optional[str]:
    """
    Realiza o Web Scraping do conteúdo HTML da página informada via URL.
    Extrai o texto dos parágrafos (<p>), limitado a 4000 caracteres.
    """
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read()

        soup = BeautifulSoup(html, "html.parser")
        paragrafos = soup.find_all("p")
        texto_noticia = "\n".join([p.get_text() for p in paragrafos]).strip()

        if not texto_noticia:
            # Fallback caso a página não use a tag <p> padrão
            texto_noticia = soup.get_text()

        return texto_noticia[:4000]

    except Exception as e:
        print(f"[Validador] Erro ao acessar a URL {url}: {e}")
        return None


def limpar_resposta_json(texto: str) -> str:
    """
    Remove marcadores de bloco de código Markdown (```json ... ```) da resposta do modelo.
    """
    texto_limpo = texto.strip()
    if texto_limpo.startswith("```"):
        texto_limpo = re.sub(r"^```(?:json)?\s*", "", texto_limpo, flags=re.IGNORECASE)
        texto_limpo = re.sub(r"\s*```$", "", texto_limpo)
    return texto_limpo.strip()


async def enviar_para_ia_validar(url_noticia: str) -> Optional[Dict[str, Any]]:
    """
    Recebe uma URL ou dados de notícia do TabNews, raspa o conteúdo, 
    processa as regras em docs/leitura_de_noticias.md e valida a relevância via Gemini.

    Esta função é assíncrona para integração transparente com bots do Discord (discord.py).
    """
    if not url_noticia:
        print("[Validador] Erro: Nenhuma URL fornecida para validação.")
        return _retorno_invalido("Nenhuma URL fornecida para validação.")

    # 1. Sanitiza a URL informada
    target_url = extrair_url(url_noticia)
    if not target_url.startswith("http"):
        print(f"[Validador] Erro: URL inválida fornecida: '{url_noticia}'")
        return _retorno_invalido(f"URL inválida: {url_noticia}")

    # 2. Carrega as regras de curadoria contidas em docs/leitura_de_noticias.md
    caminho_prompt = _obter_caminho_prompt()
    try:
        with open(caminho_prompt, "r", encoding="utf-8") as f:
            prompt_sistema = f.read()
    except FileNotFoundError:
        print(f"[Validador] Erro: Arquivo de prompt não encontrado em '{caminho_prompt}'")
        return _retorno_invalido(f"Arquivo de regras não encontrado: {caminho_prompt}")

    print(f"-> [Web Scraping] Acessando a página: {target_url}...")

    # 3. Web Scraping executado em thread para não bloquear o loop de eventos
    texto_noticia = await asyncio.to_thread(extrair_conteudo_pagina, target_url)
    if not texto_noticia:
        print(f"[Validador] Não foi possível extrair o conteúdo de: {target_url}")
        return _retorno_invalido("Falha ao extrair o conteúdo da página para análise.")

    print("-> [IA] Enviando conteúdo para análise do Gemini...")

    # 4. Verificação da API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[Validador] Erro: A variável de ambiente GEMINI_API_KEY não foi encontrada.")
        return _retorno_invalido("Chave de API do Gemini (GEMINI_API_KEY) não configurada.")

    # 5. Chamada à API do Gemini usando o SDK google-genai (com fallback de modelos)
    modelos_candidatos = ["gemini-3.6-flash", "gemini-2.0-flash", "gemini-3.5-flash"]
    client = genai.Client(api_key=api_key)
    conteudo_prompt = f"{prompt_sistema}\n\nConteúdo da Notícia:\n{texto_noticia}"

    resposta = None
    ultimo_erro = None

    for m in modelos_candidatos:
        try:
            def _chamar_gemini(m_nome=m):
                return client.models.generate_content(
                    model=m_nome,
                    contents=conteudo_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )

            resposta = await asyncio.to_thread(_chamar_gemini)
            break
        except Exception as e:
            ultimo_erro = e
            print(f"[Validador] Aviso: Modelo '{m}' indisponível ou com erro ({e}). Tentando próximo...")

    if not resposta or not resposta.text:
        print(f"[Validador] Erro na comunicação com a API do Gemini: {ultimo_erro}")
        return _retorno_invalido(f"Erro de comunicação com o serviço de IA: {str(ultimo_erro)}")

    raw_text = resposta.text
    texto_limpo = limpar_resposta_json(raw_text)

    # 6. Parsing e Fallback de JSON
    try:
        dados_validacao = json.loads(texto_limpo)
    except json.JSONDecodeError as exc:
        print(f"[Validador] Erro ao decodificar JSON retornado pela IA: {exc}")
        return _retorno_invalido("Resposta da IA não veio em formato JSON válido.")

    # 7. Validação final do contrato retornado pela IA
    dados_validacao = _validar_payload_ia(dados_validacao, target_url)

    if dados_validacao.get("relevante") is True:
        print("\n=== NOTÍCIA APROVADA COM SUCESSO! ===")
        print(json.dumps(dados_validacao, indent=4, ensure_ascii=False))
        print("=====================================\n")
    else:
        print(f"-> [IA] Notícia Descartada. Motivo: {dados_validacao.get('justificativa')}")

    return dados_validacao


def enviar_para_ia_validar_sync(url_noticia: str) -> Optional[Dict[str, Any]]:
    """
    Invólucro síncrono para enviar_para_ia_validar, permitindo execução simples
    em scripts síncronos sem gerenciar manualmente o loop de eventos.
    """
    return asyncio.run(enviar_para_ia_validar(url_noticia))