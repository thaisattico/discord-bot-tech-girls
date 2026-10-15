import asyncio
import json
import os
import sys
from dotenv import load_dotenv

# Injeta a raiz do projeto no sys.path para evitar ModuleNotFoundError
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Importações corrigidas dos serviços do projeto
from src.services.news_search import search_news as buscar_noticias_tabnews
from src.services.app_validador import enviar_para_ia_validar, extrair_url


async def main() -> None:
    """
    Função principal de orquestração do teste ponta a ponta (TabNews + Validador IA).
    """
    print("====================================================")
    print("   INICIANDO FLUXO PRINCIPAL DO BOT (TABNEWS + IA)  ")
    print("====================================================\n")

    try:
        # 1. Busca de notícias no TabNews
        print("-> [Busca] Consultando API do TabNews...")
        resultado_busca = await buscar_noticias_tabnews()

        if not resultado_busca or "Não foi possível" in resultado_busca:
            print(f"[Erro] Falha ao obter notícias do TabNews: {resultado_busca}")
            return

        # 2. Extração da primeira URL válida retornada
        url_noticia = extrair_url(resultado_busca)
        if not url_noticia.startswith("http"):
            print(f"[Erro] Nenhuma URL válida encontrada no retorno do TabNews:\n{resultado_busca}")
            return

        print(f"-> [Busca] URL encontrada: {url_noticia}\n")

        # 3. Envio para validação e resumo via agente de IA (Gemini)
        dados_embed_json = await enviar_para_ia_validar(url_noticia)

        if dados_embed_json is None:
            print("[Erro] Ocorreu uma falha grave durante o processo de validação.")
            return

        # 4. Exibição da saída em JSON perfeitamente formatado no terminal
        print("=== RESULTADO DA VALIDAÇÃO (JSON FORMATADO) ===")
        print(json.dumps(dados_embed_json, indent=2, ensure_ascii=False))
        print("===============================================\n")

        if dados_embed_json.get("relevante") is True:
            print("[Main] ✨ Sucesso! Notícia aprovada e pronta para exibição no Discord:")
            print(f"   • Título: {dados_embed_json.get('titulo')}")
            print(f"   • Tags: {dados_embed_json.get('tags')}")
            print(f"   • Resumo:\n{dados_embed_json.get('texto-resumo')}")
            print(f"   • Link: {dados_embed_json.get('link-de-acesso')}")
        else:
            print("[Main] 🚫 Notícia descartada pela IA.")
            print(f"   • Motivo: {dados_embed_json.get('justificativa')}")

    except Exception as e:
        print(f"\n[Main] Exceção inesperada durante a execução do fluxo: {e}")

    print("\n====================================================")
    print("             FIM DA EXECUÇÃO DO FLUXO               ")
    print("====================================================")


if __name__ == "__main__":
    asyncio.run(main())