# Registro de testes

Como rodar (da raiz do projeto):

```bash
.venv/bin/python -m pytest tests/test_vagas.py -v
```

Os testes simulam a RapidAPI (JSearch) com `httpx.MockTransport`: não usam rede, chave de API nem token do Discord.

---

## 2026-11-03: busca de vagas voltou a funcionar

**O que mudou e por quê:** a busca de vagas não postava nada no Discord. Ao ler o código, apareceram três bugs que travavam a busca:

1. `src/services/jobs_search.py`: um `return []` deixado para "testes locais" logo depois da chamada à API. As vagas nunca eram processadas. **Removido.**
2. `src/bot.py`: o cog `cogs.jobs_tasks` nunca era carregado, então o `/setupjobs` não achava as tarefas de busca e envio para iniciar. **Carregado no `setup_hook`.** O `bot.run()` passou para dentro de `if __name__ == "__main__"`, para o bot poder ser importado nos testes.
3. `src/services/jobs_search.py`: sem `RAPIDAPI_KEY`, a função devolvia `None`, e a tarefa quebrava no `for vaga in vagas`. **Agora devolve `[]`.**

**Casos usados (15):** `tests/test_vagas.py`
- busca (12): vagas BR, payload `data` e `data.jobs` (search-v2), filtro de fora do Brasil, Brasil só na localização, duplicadas, limite, vaga sem link/título, fallback de query, nenhuma vaga nas duas queries, chave e filtros enviados à API, erro HTTP 429, sem chave;
- tarefa periódica (2): sem chave não quebra; enfileira sem repetir vaga já vista;
- inicialização do bot (1): `setup_hook` carrega `cogs.jobs_tasks`.

**Resultado:**

| | Acertos | Tempo da suíte |
|---|---|---|
| Antes (marco zero) | **3 / 15** | 2,4 s |
| Depois | **15 / 15** | 1,4 s |

**O que falhava antes e por quê:**
- 9 casos de busca: o `return []` antecipado devolvia lista vazia para qualquer resposta da API;
- "sem chave" e "tarefa sem chave": `None` no lugar de lista;
- "bot carrega vagas": importar o `bot.py` já tentava conectar ao Discord (`bot.run`), e o cog de vagas não estava na lista de extensões.

Os 3 casos que já passavam (chave e filtros enviados, erro HTTP, enfileirar sem repetir) cobrem trechos que os bugs não afetavam.

**Decisão:** manter as três correções. Ainda falta testar com a API e o Discord de verdade (precisa de `.env` com `BOT_TOKEN` e `RAPIDAPI_KEY`).

**Bugs mapeados que ficaram para depois:** busca a cada 1 minuto (o comentário diz 4 horas; gasta a cota da API), tarefas não voltam sozinhas depois que o bot reinicia, `/setupjobs` dá erro na segunda vez no mesmo servidor, vagas já enviadas se repetem depois de reiniciar, `httpx` duplicado no `requirements.txt`, caminhos relativos do banco e conexões do SQLite que não são fechadas.

---

## 2026-11-03: teste com as chaves reais (Discord e Gemini)

Teste de fumaça com o `.env` preenchido (ainda sem `RAPIDAPI_KEY`). Não mudou código.

| O que | Resultado |
|---|---|
| Token do Discord | ✅ login, conexão ao Gateway, comandos `setupnews` e `setupjobs` registrados |
| `DEV_GUILD_ID` | ❌ → ✅ estava com o ID do bot, e não do servidor (deu 403 Missing Access); corrigido para o ID do servidor |
| Chave do Gemini | ✅ responde (`gemini-3.6-flash` e `gemini-3.5-flash`) |
| Agente de notícias (TabNews → Gemini → JSON) | ✅ 30 notícias buscadas; 1 aprovada com o JSON completo, mas só pelo modelo reserva |

**Achados:**
- `gemini-2.0-flash`, o 2º modelo da lista de reserva em `app_validador.py`, foi desativado pelo Google (404).
- Quando todos os modelos falham (ex.: 503 de alta demanda), a notícia volta como `relevante=False`. A falha da IA vira "notícia descartada" sem diferença no log de envio.

---

## 2026-11-03: modelo do agente de notícias → gemini-3.5-flash-lite

**O que mudou e por quê:** a lista de modelos em `src/services/app_validador.py` era `gemini-3.6-flash` → `gemini-2.0-flash` → `gemini-3.5-flash`. O `gemini-2.0-flash` foi desativado (404). O `gemini-2.5-flash-lite`, primeira escolha para substituí-lo, também não serve: o Google não libera mais esse modelo para contas novas (404). A lista nova é `gemini-3.5-flash-lite` → `gemini-3.6-flash` → `gemini-3.5-flash`.

**Casos usados (18):** `tests/data/casos_ia_noticias.json`, notícias reais do TabNews de 2026-11-03.
- 11 devem ser aprovadas (segurança, tutoriais, IA, cursos, mulher na tecnologia);
- 7 devem ser descartadas (mercado financeiro, estoque de hardware, meme e 4 difíceis: regulação, opinião sobre uma pessoa, contrato de empresa, política comercial).
- A resposta esperada foi definida pelo Claude a partir das regras do prompt, **a conferir pela Lucila**.

O texto de cada notícia é raspado uma vez e reaproveitado por todos os modelos (cache fora do git). O script repete até 3 vezes em erro temporário (503/429).

```bash
.venv/bin/python tests/avaliar_modelos_ia.py gemini-3.6-flash gemini-3.5-flash-lite
```

**Resultado (cada modelo sozinho, mesmos 18 casos):**

| Modelo | Acertos | JSON no contrato | Erros de API | Tempo médio | Tokens entrada / saída |
|---|---|---|---|---|---|
| gemini-3.6-flash (antigo principal) | 4/18 | 4/18 | 14 (503 e 429) | 47,4 s | 7.084 / 4.812 |
| gemini-2.0-flash (antigo reserva) | 0/18 | 0/18 | 18 (404) | 0,4 s | 0 |
| gemini-3.5-flash (antigo reserva) | 0/18 | 0/18 | 18 (429) | 32,0 s | 0 |
| **gemini-3.5-flash-lite (novo principal)** | **15/18** | **17/18** | **0** | **3,1 s** | 24.626 / 2.092 |

**O que falhou e por quê:**
- **Modelos flash:** o plano grátis permite **20 pedidos por dia** por modelo (`generate_content_free_tier_requests, limit: 20`). Os testes anteriores do dia já tinham gastado parte da cota, e o `gemini-3.6-flash` estourou o limite no 5º caso. Como o bot busca até 30 notícias por ciclo, com os modelos flash ele pararia de funcionar no primeiro ciclo do dia. Nos 4 casos que o `gemini-3.6-flash` respondeu, acertou os 4: não dá para dizer que o lite classifica melhor, só que **funciona dentro da cota**.
- **gemini-3.5-flash-lite (3 erros de classificação):**
  - "mulher desabafando sobre desenvolvimento" → descartou como "opinião especulativa sobre IA"; o esperado era aprovar (regra 5: mulheres na tecnologia);
  - "índice chinês STAR50 despenca" → aprovou; o esperado era descartar (mercado financeiro);
  - "Kinghost: armadilhas no contrato" → aprovou; o esperado era descartar.
- **gemini-3.5-flash-lite (1 erro de contrato):** em "somar horas em JavaScript", uma linha do resumo passou de 15 palavras. O validador do bot transforma isso em "não relevante", então **no bot o resultado é 14/18**.
- O lite gasta mais tokens de entrada porque leu os 18 textos inteiros. Os modelos flash leram só os 4 que responderam.

**Decisão:** usar o `gemini-3.5-flash-lite` como principal e manter os dois flash como reserva. Depois da troca, o fluxo real (TabNews → Gemini → JSON) aprovou 3 notícias de 3 em 3,3 a 3,7 s, sem cair para outro modelo. Próximos passos possíveis: reforçar no prompt a regra 5 e o limite de 15 palavras, e medir de novo com estes mesmos casos.

---

## 2026-11-04: bloqueios para rodar o bot completo

**O que mudou e por quê:** com a `RAPIDAPI_KEY` no `.env`, uma busca real trouxe 5 vagas brasileiras numa requisição (11 s). Antes de ligar o bot completo, apareceram três bloqueios:

1. `src/database/database.py`: o `/setupjobs` e o `/setupnews` faziam `INSERT` sobre a regra `UNIQUE(id_guild, tipo)`. O banco já tinha canais salvos para o servidor, então o comando dava `IntegrityError` antes de responder e as tarefas nunca começavam. **Agora o comando troca o canal (`ON CONFLICT ... DO UPDATE`) e fecha a conexão.**
2. `src/cogs/jobs_tasks.py`: a busca de vagas rodava a cada 1 minuto e podia fazer 2 requisições por vez. O plano grátis da RapidAPI dá 200 requisições por mês, e a cota acabaria em 2 a 3 horas. **Agora roda a cada 8 horas: no pior caso, 180 por mês.** A primeira proposta foi 4 horas, mas o teste mostrou que o pior caso daria 360 por mês.
3. `src/cogs/tasks.py`: as notícias descartadas pela IA não ficavam salvas e voltavam para o Gemini em cada ciclo (umas 25 chamadas a cada 2 ou 3 minutos). As aprovadas que ainda esperavam na fila eram enfileiradas de novo e podiam ser postadas duplicadas. **Agora o cog guarda as notícias já avaliadas.**

**Casos usados (7 novos):** `tests/test_bloqueios.py`
- setup do mesmo tipo duas vezes; vagas e notícias em canais diferentes no mesmo servidor; `/setupjobs` e `/setupnews` repetidos respondem e iniciam as tarefas (2 casos);
- intervalo da busca de vagas cabe nas 200 requisições/mês;
- notícia descartada não volta para a IA; notícia aprovada na fila não é enfileirada de novo.

**Resultado:**

| | Testes novos | Suíte inteira | Tempo da suíte |
|---|---|---|---|
| Antes (marco zero) | **1 / 7** | 16 / 22 | 6,0 s |
| Depois | **7 / 7** | **22 / 22** | 3,2 s |

O caso que já passava era o de vagas e notícias em canais diferentes, que a regra `UNIQUE(id_guild, tipo)` já permitia.

**Limitação conhecida:** as notícias avaliadas ficam só na memória. Depois de reiniciar, o bot reavalia uma vez as cerca de 30 notícias da página do TabNews. Se o Gemini falhar (503) numa notícia, ela é tratada como descartada até o bot reiniciar.

**Decisão:** manter as três correções. Bot ligado com as chaves reais em 2026-11-04: login, Gateway e comandos registrados.

**Teste ao vivo (2026-11-04, 12:08 às 12:14), depois de `/setupjobs` e `/setupnews` no servidor "Tech News Bot":**
- Vagas: 1 requisição à RapidAPI, 4 vagas BR enfileiradas, 2 enviadas ao canal no primeiro minuto e meio (1 por minuto).
- Notícias: 5 avaliadas, 2 aprovadas, 1 enviada ao canal e salva no banco. 2 caíram porque **os três modelos do Gemini deram 503** (alta demanda) ao mesmo tempo. Pela limitação acima, essas 2 ficam marcadas como avaliadas e não voltam até o bot reiniciar.

---

## 2026-11-04: vaga postada com função, empresa e descrição conferida no link

**O que mudou e por quê:** a mensagem da vaga no Discord só tinha o título e o botão. Pedido: mostrar **nome da função, empresa e descrição da função**, e **acessar o link para conferir a descrição antes de postar**.
- `src/services/jobs_search.py`:
  - a vaga guarda a empresa (`employer_name`), a descrição da API e os links alternativos (`apply_options`);
  - a função nova `verificar_vaga` abre o link da vaga (e os alternativos, se o principal falhar) e lê a descrição no bloco padrão `JobPosting` (JSON-LD) da página. Se a página não tiver esse bloco, aceita quando o começo da descrição da API aparece no texto da página;
  - a vaga é recusada se nenhum link abrir, se o prazo (`validThrough`) estiver vencido ou se a página disser que ela foi encerrada.
- `src/cogs/jobs_tasks.py`: antes de postar, confere a vaga; as não confirmadas são puladas e a próxima da fila é tentada.
- `src/utils/embeds.py`: o embed tem a função como título, os campos "Empresa" e "Local" e a descrição cortada no fim de uma frase (até 600 caracteres).

**Casos usados (12 novos):** `tests/test_vaga_verificada.py`
- empresa e links alternativos na vaga;
- descrição lida da página (JSON-LD), página sem JSON-LD que mostra a descrição, link bloqueado que cai no alternativo, nenhum link confirma, prazo vencido, página dizendo que a vaga foi encerrada;
- embed com função, empresa e descrição dentro do limite; envio pula a vaga não confirmada e posta a próxima;
- 2 casos achados com vagas reais (abaixo).

**Resultado:**

| | Testes novos | Suíte inteira | Vagas reais confirmadas (10 da RapidAPI) |
|---|---|---|---|
| Antes (marco zero) | **0 / 10** | 22 / 32 | não havia conferência |
| 1ª versão | 10 / 10 | 32 / 32 | 7 / 10, descrição com tags `<p>` |
| Depois dos 2 casos novos | **12 / 12** | **34 / 34** | **8 / 10**, texto limpo, ~2,1 s por vaga |

**O que falhou e por quê:**
- **Tags `<p>` na descrição:** o LinkedIn manda a descrição com o HTML escapado (`&lt;p&gt;`). Agora o texto é "desescapado" antes de limpar. Virou o caso `test_descricao_com_html_escapado_vira_texto`.
- **Vaga aberta recusada (Alignerr, trabajo.org):** a página tem um formulário de denúncia com a opção "Vaga expirada", e a regra de vaga encerrada pegou essa expressão solta. Agora só valem frases completas ("esta vaga expirou", "no longer accepting applications" etc.). Virou o caso `test_opcao_vaga_expirada_no_formulario_de_denuncia_nao_bloqueia`.
- **2 vagas reais continuam sem postar, de propósito:** o Indeed bloqueia acesso automático (401), e a página do ProgramaThor não traz a descrição no HTML. No endpoint `/search-v2`, o `apply_options` vem só com o próprio link principal, então não houve link alternativo para tentar.

**Limitação:** a descrição é o começo do texto da vaga. Em muitas vagas, ele apresenta a empresa antes de falar da função (ex.: Superlógica).

**Decisão:** postar só vagas confirmadas no link. Bot reiniciado com o código novo em 2026-11-04 12:20.

**Teste ao vivo (2026-11-04 12:21 às 12:23), depois de `/setupjobs`:** 1 requisição à RapidAPI trouxe 5 vagas BR, e 2 já foram conferidas e postadas. Lidas de volta no canal pela API do Discord: título com a função, campos Empresa e Local, descrição em texto limpo (457 e 506 caracteres) e botão do site. Detalhe visual: na vaga da Enter (Ashby), o site de origem vem como "Jobs", e o botão ficou "Ver no Jobs".
