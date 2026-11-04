"""Avalia modelos do Gemini no agente de noticias com um conjunto fixo de casos.

Usa o mesmo prompt (docs/leitura_de_noticias.md), a mesma raspagem e a mesma validacao
do contrato JSON do bot (services/app_validador.py). Chama a API de verdade: precisa de
GEMINI_API_KEY no .env.

Rodar da raiz do projeto:
    .venv/bin/python tests/avaliar_modelos_ia.py gemini-3.6-flash gemini-3.5-flash-lite
"""
import json
import os
import sys
import time

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(RAIZ, "src"))

from dotenv import load_dotenv
from google import genai
from google.genai import types

from services.app_validador import (
    _obter_caminho_prompt,
    _validar_payload_ia,
    extrair_conteudo_pagina,
    limpar_resposta_json,
)

load_dotenv(os.path.join(RAIZ, ".env"))

CASOS = os.path.join(RAIZ, "tests", "data", "casos_ia_noticias.json")
CACHE = os.path.join(RAIZ, "tests", "data", ".cache_noticias")  # fora do git: texto de outros autores
TENTATIVAS = 3  # repete em erro temporario (503/429) para nao medir instabilidade como erro do modelo


def texto_do_caso(caso: dict) -> str | None:
    """Raspa a noticia uma vez e reaproveita, para todos os modelos lerem o mesmo texto."""
    os.makedirs(CACHE, exist_ok=True)
    arquivo = os.path.join(CACHE, f"{caso['id']}.txt")
    if os.path.exists(arquivo):
        with open(arquivo, encoding="utf-8") as f:
            return f.read()
    texto = extrair_conteudo_pagina(caso["url"])
    if texto:
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(texto)
    return texto


def avaliar(client, modelo: str, casos: list[dict], prompt: str) -> dict:
    linhas = []
    for caso in casos:
        texto = texto_do_caso(caso)
        conteudo = f"{prompt}\n\nConteúdo da Notícia:\n{texto}"
        resultado = {"titulo": caso["titulo"], "esperado": caso["esperado_relevante"]}
        inicio = time.time()
        for tentativa in range(1, TENTATIVAS + 1):
            try:
                resposta = client.models.generate_content(
                    model=modelo,
                    contents=conteudo,
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )
                payload = json.loads(limpar_resposta_json(resposta.text or ""))
                validado = _validar_payload_ia(payload, caso["url"])
                contrato_ok = isinstance(payload, dict) and (
                    validado.get("relevante") == payload.get("relevante")
                )
                uso = resposta.usage_metadata
                resultado.update(
                    obtido=payload.get("relevante") if isinstance(payload, dict) else None,
                    contrato_ok=contrato_ok,
                    motivo_contrato=None if contrato_ok else validado.get("justificativa"),
                    tokens_entrada=uso.prompt_token_count or 0,
                    tokens_saida=(uso.candidates_token_count or 0) + (uso.thoughts_token_count or 0),
                    erro=None,
                )
                break
            except json.JSONDecodeError:
                resultado.update(obtido=None, contrato_ok=False, motivo_contrato="JSON invalido", erro=None)
                break
            except Exception as e:
                resultado.update(obtido=None, contrato_ok=False, erro=str(e)[:120])
                if tentativa < TENTATIVAS and any(c in str(e) for c in ("503", "429", "UNAVAILABLE")):
                    time.sleep(10 * tentativa)
                    continue
                break
        resultado["segundos"] = round(time.time() - inicio, 1)
        resultado["acertou"] = resultado.get("obtido") == caso["esperado_relevante"]
        linhas.append(resultado)
        marca = "✅" if resultado["acertou"] else "❌"
        print(f"  {marca} {caso['titulo'][:60]:60} esp={caso['esperado_relevante']!s:5} "
              f"obt={resultado.get('obtido')!s:5} contrato={'ok' if resultado['contrato_ok'] else 'X'} "
              f"{resultado['segundos']}s {resultado.get('erro') or resultado.get('motivo_contrato') or ''}")
        time.sleep(2)

    validos = [r for r in linhas if r.get("erro") is None]
    return {
        "modelo": modelo,
        "acertos": sum(r["acertou"] for r in linhas),
        "total": len(linhas),
        "contrato_ok": sum(r["contrato_ok"] for r in linhas),
        "erros_api": len(linhas) - len(validos),
        "tempo_medio_s": round(sum(r["segundos"] for r in linhas) / len(linhas), 1),
        "tokens_entrada": sum(r.get("tokens_entrada", 0) for r in validos),
        "tokens_saida": sum(r.get("tokens_saida", 0) for r in validos),
        "casos": linhas,
    }


def main():
    modelos = sys.argv[1:] or ["gemini-3.6-flash", "gemini-3.5-flash-lite"]
    with open(CASOS, encoding="utf-8") as f:
        casos = json.load(f)
    with open(_obter_caminho_prompt(), encoding="utf-8") as f:
        prompt = f.read()

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    resumo = []
    for modelo in modelos:
        print(f"\n=== {modelo}")
        resumo.append(avaliar(client, modelo, casos, prompt))

    print("\nmodelo | acertos | contrato JSON ok | erros de API | tempo médio | tokens entrada/saída")
    for r in resumo:
        print(f"{r['modelo']} | {r['acertos']}/{r['total']} | {r['contrato_ok']}/{r['total']} | "
              f"{r['erros_api']} | {r['tempo_medio_s']}s | {r['tokens_entrada']}/{r['tokens_saida']}")

    saida = os.path.join(RAIZ, "tests", "data", ".resultado_avaliacao_ia.json")
    with open(saida, "w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
