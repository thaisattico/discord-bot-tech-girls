# Documentação de Testes — Discord Bot Tech Girls

Este documento reúne as instruções, diretrizes e descrições dos testes utilizados no desenvolvimento do projeto.

---

## Sumário
- [Visão Geral](#-visão-geral)
- [Descrição dos Módulos de Teste](#-descrição-dos-módulos-de-teste)

---

## Visão Geral

Os testes têm como objetivo garantir que:
1. As buscas e validações de notícias estejam funcionando antes do envio ao Discord.
2. A montagem e formatação de `Embeds` não estourem os limites do Discord API.
3. As tarefas agendadas (`tasks`) funcionem corretamente sem falhas de conexão.

---

## Descrição dos Módulos de Teste

### 1. `teste_noticias.py`
* **Objetivo:** Valida a busca e retorno de notícias da `services/news_search.py`.
* **O que testa:**
  * Retorno correto da API em dicionario e Corpo das notícias.

### 2. `teste_embed.py`
* **Objetivo:** Garante que a criação de `discord.Embed` em `utils/embeds.py` ocorra sem falhas.
* **O que testa:**
  * Presença de campos obrigatórios (título, descrição, URL) utilizando dados simulados para teste.
  * Formatação e exibição correta das cores e imagens padrão.

### 3. `tasks_teste.py`
* **Objetivo:** Testa os loops de automatizacao dos bots (sem o banco de dados) `tasks_teste.py`.
* **O que testa:**
  * Disparo correto do evento de busca, validação e envio automático de notícias.

### 3. `main_teste.py`
