# Discord Bot - Tech Girls

## Objetivo

Desenvolver um bot para a comunidade Tech Girls, integrada ao Discord, que automatize o compartilhamento de notícias de tecnologia por meio da API do TabNews e divulgue vagas na área tech.

## Equipe

- Thais
- Maria
- Lucila
- Andressa
  
## Stack

- Python 3.14
- discord.py
- SQLite Studio
- API TabNews

## Banco de Dados

Tabela 1: noticias_postadas

Guarda o ID da notícia, evitando duplicidade.

Colunas
- id_noticia - id da notícia conforme no site TabNews
- titulo - título da notícia postada no TabNews
- url - url da notícia
- autor - identificação de quem postou a notícia no site
- tag - classificador de assunto da notícia
- postado_em - data em que a notícia foi postada no bot

Tabela 2: canais_configurados

Guarda em qual servidor/canal o bot deve postar

Colunas
- id_canal - id gerado internamente para o canal de notícias
- id_guild - id do servidor discord
- id_channel - identificador do discord
- criado_em - data de criação do servidor


## Dependências

Para rodar o bot e os serviços de busca de notícias, o projeto utiliza as seguintes bibliotecas Python:

* **`discord.py`**: Framework para interação com a API do Discord.
* **`aiohttp`**: Biblioteca assíncrona para requisições HTTP (instalada automaticamente junto com o `discord.py`), utilizada na integração com a API do TabNews.
* **`python-dotenv`**: Gerenciamento de variáveis de ambiente (chaves de API, ID do servidor de testes e tokens).

### Para instalar as dependências
No terminal, instale os pacotes necessários:

```bash
pip install discord.py python-dotenv
