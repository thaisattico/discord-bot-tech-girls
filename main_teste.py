import os
from dotenv import load_dotenv

load_dotenv()

from src.services.news_search import search_news as buscar_noticias_tabnews
from Validador_IA.app_validador import enviar_para_ia_validar


def main():
    print("====================================================")
    print("   INICIANDO FLUXO PRINCIPAL DO BOT (TABNEWS + IA)  ")
    print("====================================================\n")

    print("-> [Busca] Consultando API do TabNews...")
    url_noticia = buscar_noticias_tabnews()

    if not url_noticia:
        print("[Erro] Nenhuma URL retornada pela busca.")
        return

    print(f"-> [Busca] URL encontrada: {url_noticia}\n")

    dados_embed_json = enviar_para_ia_validar(url_noticia)

    if dados_embed_json is None:
        print("[Erro] Ocorreu uma falha no processo de validação.")
        return

    if dados_embed_json.get("relevante") is True:
        print("[Main] ✨ Sucesso! Notícia aprovada e pronta para o Embed:")
        print(f"   • Tags: {dados_embed_json.get('tags')}")
        print(f"   • Resumo:\n{dados_embed_json.get('texto-resumo')}")
        print(f"   • Link: {dados_embed_json.get('link-de-acesso')}")
    else:
        print("[Main] 🚫 Notícia descartada pela IA.")
        print(f"   • Motivo: {dados_embed_json.get('justificativa')}")

    print("\n====================================================")
    print("             FIM DA EXECUÇÃO DO FLUXO               ")
    print("====================================================")


if __name__ == "__main__":
    main() 