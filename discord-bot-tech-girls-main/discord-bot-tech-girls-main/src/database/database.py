import sqlite3

# --- Inicializa o banco criando as tabelas ---
def inicializar_banco():
    conexao = sqlite3.connect("bot_teste.db")
    cursor = conexao.cursor()
    
    #Le o arquivo e executa todo o script de uma vez
    with open("src/database/criacao_schema.sql", "r", encoding="utf-8") as f:
        script_sql = f.read()
        
    cursor.executescript(script_sql)
    conexao.commit()
    conexao.close()


#--- Insere as noticias "publicadas" no discord no banco de dados para evitar noticias duplicadas ---
def inserir_noticia(id_noticia, titulo, autor, url, postado_em, tag):
    conexao = sqlite3.connect("bot_teste.db")
    cursor = conexao.cursor()

    try:
        cursor.execute("INSERT INTO noticias_postadas (id_noticia, titulo, autor, url, postado_em, tag) VALUES (?, ?, ?, ?, ?, ?)", (id_noticia, titulo, autor, url, postado_em, tag))
        conexao.commit()
        return ("noticia aceita", id_noticia)
    except:
        cursor.execute("SELECT id_noticia FROM noticias_postadas WHERE url = ?", (url,))
        resultado = cursor.fetchone()
        return ("noticia recusada", resultado[0])
    
    
# --- Busca as noticias no banco de dados ---
def buscar_noticias(id_noticia):
    conexao = sqlite3.connect("bot_teste.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id_noticia, titulo, autor, url, postado_em, tag FROM noticias_postadas WHERE id_noticia = ?", (id_noticia,))
    resultado = cursor.fetchone()
    
    if resultado is not None:
        return resultado #Retorna a tupla com as noticias (True)
    else:
        return False #Passa a retornar false
    
    
# --- Busca os canais configurados para o envio das noticias ---
def buscar_servidores(tipo):
    conexao = sqlite3.connect("bot_teste.db")
    cursor = conexao.cursor()

    # Adiciona a filtragem pelo tipo do canal ('noticias' ou 'vagas')
    cursor.execute(
        "SELECT id_channel FROM canais_configurados WHERE tipo = ?", (tipo,)
    )
    resultado = cursor.fetchall()
    conexao.close()

    if resultado:
        return [int(linha[0]) for linha in resultado]
    else:
        return []
    
    
# --- Insere o id do canal e do servidor onde serao encaminhadas no banco de dados ---
def inserir_canal_servidor(id_guild, id_channel, tipo, criado_em):
    conexao = sqlite3.connect("bot_teste.db")
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO canais_configurados(id_guild, id_channel, tipo, criado_em) VALUES (?, ?, ?, ?)", (id_guild, id_channel, tipo, criado_em))
    conexao.commit()
    id_gerado = cursor.lastrowid
    return ("canal inserido", id_gerado)
