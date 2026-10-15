PRAGMA foreign_keys = off;

BEGIN TRANSACTION;

-- Tabela: canais_configurados
CREATE TABLE IF NOT EXISTS canais_configurados (
    id_canal INTEGER PRIMARY KEY,
    id_guild TEXT,
    id_channel TEXT,
    tipo TEXT,
    criado_em TEXT,
    UNIQUE (id_guild, tipo)
);

-- Tabela: noticias_postadas
CREATE TABLE IF NOT EXISTS noticias_postadas (
    id_noticia TEXT PRIMARY KEY,
    titulo TEXT,
    url TEXT,
    autor TEXT,
    postado_em TEXT,
    tag TEXT
);

COMMIT TRANSACTION;

PRAGMA foreign_keys = on;