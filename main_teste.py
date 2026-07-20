import json
import os
from dotenv import load_dotenv  # Carrega as variáveis do arquivo .env

# 1. Inicializa as variáveis de ambiente antes de importar o validador
load_dotenv()

# 2. Importa a nova função do seu módulo de IA
from Validador_IA.app_validador import enviar_para_ia_validar


def main():
    print("====================================================")
    print("   INICIANDO FLUXO PRINCIPAL DO BOT (TESTE DE IA)   ")
    print("====================================================\n")

    # raspar a web, consultar o prompt e chamar a API do Gemini
    dados_embed_json = enviar_para_ia_validar()

    # 4. Analisa o resultado retornado pelo validador
    if dados_embed_json is None:
        print("Erro: Ocorreu uma falha durante o processo de validação.")
        return

    if dados_embed_json.get("relevante") is True:
        print("Sucesso! A notícia foi aprovada pela IA.")
        print("Dados recebidos prontos para o Embed do Discord:")

        # Aqui sua equipe do bot pode extrair as informações limpas
        print(f"   - Tags geradas: {dados_embed_json.get('tags')}")
        print(f"   - Resumo de 3 linhas:\n{dados_embed_json.get('texto-resumo')}")
        print(f"   - Link da postagem: {dados_embed_json.get('link-de-acesso')}")

        print(
            "\nPróximo passo: Repassar estes dados para a função que cria o card no Discord."
        )

    else:
        print(
            "Fluxo encerrado: A notícia foi descartada por não ser relevante."
        )
        print(f"   - Motivo do descarte: {dados_embed_json.get('justificativa')}")

    print("\n====================================================")
    print("             FIM DA EXECUÇÃO DO FLUXO               ")
    print("====================================================")


if __name__ == "__main__":
    main()