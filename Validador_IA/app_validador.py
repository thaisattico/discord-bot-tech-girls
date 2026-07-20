import json
import os
import urllib.request
from bs4 import BeautifulSoup
from google import genai 
from google.genai import types

def verificar_historico_noticias():
    """Lê os arquivos JSON locais, compara o link atual com o histórico

    e define se a notícia é inédita ou repetida.
    """
    caminho_modulo = os.path.dirname(os.path.abspath(__file__))
    arquivo_entrada = os.path.join(
        caminho_modulo, "dados_teste", "link_noticias.json"
    )
    arquivo_banco = os.path.join(
        caminho_modulo, "dados_teste", "noticias_postadas.json"
    )

    try:
        with open(arquivo_entrada, "r", encoding="utf-8") as f:
            dados = json.load(f)
            # CORREÇÃO: Verifica se o JSON é uma lista ou um dicionário direto
            if isinstance(dados, list):
                noticia_atual = dados[0] if dados else {}
            else:
                noticia_atual = dados
            link_atual = noticia_atual.get("link")
    except FileNotFoundError:
        return "erro: arquivo link_noticias.json não encontrado"

    if not link_atual:
        return "erro: link não encontrado no arquivo de entrada"

    if os.path.exists(arquivo_banco):
        with open(arquivo_banco, "r", encoding="utf-8") as f:
            try:
                historico = json.load(f)
            except json.JSONDecodeError:
                historico = []
    else:
        historico = []

    links_postados = [
        noticia["link"] for noticia in historico if "link" in noticia
    ]

    if link_atual in links_postados:
        return "erro: link já postado"
    else:
        return "enviando para ia validar"


def enviar_para_ia_validar():
    """Acessa o link do arquivo de entrada, extrai o conteúdo do texto,

    lê o prompt do sistema a partir do arquivo markdown em docs,
    envia para a validação da IA do Gemini e exibe o JSON resultante.
    """
    caminho_modulo = os.path.dirname(os.path.abspath(__file__))
    arquivo_entrada = os.path.join(
        caminho_modulo, "dados_teste", "link_noticias.json"
    )
    arquivo_prompt = os.path.join(
        caminho_modulo, "docs", "leitura_de_noticias.md"
    )
    arquivo_banco = os.path.join(
        caminho_modulo, "dados_teste", "noticias_postadas.json"
    )

    # 1. Ler a notícia de entrada com correção para listas
    try:
        with open(arquivo_entrada, "r", encoding="utf-8") as f:
            dados = json.load(f)
            if isinstance(dados, list):
                noticia_atual = dados[0] if dados else {}
            else:
                noticia_atual = dados
            link_atual = noticia_atual.get("link")
    except FileNotFoundError:
        print("Erro: Arquivo link_noticias.json não encontrado.")
        return None

    # 2. Ler o prompt estruturado
    try:
        with open(arquivo_prompt, "r", encoding="utf-8") as f:
            prompt_sistema = f.read()
    except FileNotFoundError:
        print(
            f"Erro: O arquivo de prompt não foi encontrado em: '{arquivo_prompt}'"
        )
        return None

    print(f"-> [Web Scraping] Acessando a página: {link_atual}...")

    # 3. Web Scraping
    try:
        req = urllib.request.Request(
            link_atual, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read()

        soup = BeautifulSoup(html, "html.parser")
        paragrafos = soup.find_all("p")
        texto_noticia = "\n".join([p.get_text() for p in paragrafos])
        texto_noticia = texto_noticia[:4000]

    except Exception as e:
        print(f"Erro ao acessar ou ler o link da notícia: {e}")
        return None

    print("-> [IA] Enviando conteúdo extraído para análise do Gemini...")

    # 4. Configurar e chamar o novo cliente google-genai
    try:
        # Inicializa o cliente puxando a chave automaticamente do ambiente
        client = genai.Client()

        conteudo_prompt = (
            f"{prompt_sistema}\n\nConteúdo da Notícia:\n{texto_noticia}"
        )

        # Nova sintaxe oficial do SDK atualizado
        resposta = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=conteudo_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )

        dados_validacao = json.loads(resposta.text)

        # 5. Persistir no histórico se for aprovada
        if dados_validacao.get("relevante") is True:
            dados_validacao["link-de-acesso"] = link_atual

            if os.path.exists(arquivo_banco):
                with open(arquivo_banco, "r", encoding="utf-8") as f:
                    try:
                        historico = json.load(f)
                    except json.JSONDecodeError:
                        historico = []
            else:
                historico = []

            historico.append(dados_validacao)

            with open(arquivo_banco, "w", encoding="utf-8") as f:
                json.dump(historico, f, indent=4, ensure_ascii=False)

            print("\n=== NOTÍCIA APROVADA! RETORNO DO ARQUIVO EM JSON ===")
            print(json.dumps(dados_validacao, indent=4, ensure_ascii=False))
            print("====================================================\n")
        else:
            print(
                f"-> [IA] Notícia Descartada. Motivo: {dados_validacao.get('justificativa')}"
            )

        return dados_validacao

    except Exception as e:
        print(f"Erro na comunicação com a API do Gemini: {e}")
        return None