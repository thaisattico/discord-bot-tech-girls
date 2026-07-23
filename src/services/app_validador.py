import json
import os
import urllib.request
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

def enviar_para_ia_validar(url_noticia):
    """
    Recebe uma URL enviada pelo serviço de busca, raspa seu conteúdo, 
    consulta o prompt em docs e valida a relevância via Gemini.
    """
    if not url_noticia:
        print("[Validador] Erro: Nenhuma URL fornecida para validação.")
        return None

    # 1. Mapeamento dinâmico apenas para o arquivo de prompt (.md)
    caminho_modulo = os.path.dirname(os.path.abspath(__file__))
    arquivo_prompt = os.path.join(caminho_modulo, "docs", "leitura_de_noticias.md")

    # 2. Ler o prompt do sistema
    try:
        with open(arquivo_prompt, "r", encoding="utf-8") as f:
            prompt_sistema = f.read()
    except FileNotFoundError:
        print(f"[Validador] Erro: Arquivo de prompt não encontrado em: '{arquivo_prompt}'")
        return None

    print(f"-> [Web Scraping] Acessando a página: {url_noticia}...")

    # 3. Web Scraping do conteúdo HTML
    try:
        req = urllib.request.Request(
            url_noticia, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read()

        soup = BeautifulSoup(html, "html.parser")
        paragrafos = soup.find_all("p")
        texto_noticia = "\n".join([p.get_text() for p in paragrafos])
        texto_noticia = texto_noticia[:4000]  # Limite para otimizar tokens

    except Exception as e:
        print(f"[Validador] Erro ao acessar o link extraído: {e}")
        return None

    print("-> [IA] Enviando conteúdo para análise do Gemini...")

    # 4. Chamada da API com google-genai
    try:
        client = genai.Client()
        conteudo_prompt = f"{prompt_sistema}\n\nConteúdo da Notícia:\n{texto_noticia}"

        # Usando a string do modelo estável que validamos anteriormente
        resposta = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=conteudo_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )

        dados_validacao = json.loads(resposta.text)

        # 5. Injeta o link e devolve o JSON pronto para o bot
        if dados_validacao.get("relevante") is True:
            dados_validacao["link-de-acesso"] = url_noticia

            print("\n=== NOTÍCIA APROVADA COM SUCESSO! ===")
            print(json.dumps(dados_validacao, indent=4, ensure_ascii=False))
            print("=====================================\n")
        else:
            print(f"-> [IA] Notícia Descartada. Motivo: {dados_validacao.get('justificativa')}")

        return dados_validacao

    except Exception as e:
        print(f"[Validador] Erro na comunicação com a API do Gemini: {e}")
        return None