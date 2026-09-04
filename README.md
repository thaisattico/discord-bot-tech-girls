# Onboarding - Discord Bot Tech Girls 💜

## 1. Sobre o projeto

O Discord Bot Tech Girls é um projeto desenvolvido para a comunidade Tech Girls.

Este documento apresenta os primeiros passos necessários para uma nova integrante acessar o projeto e começar a trabalhar no desenvolvimento do bot.

O objetivo do onboarding é facilitar a entrada no projeto, apresentar sua estrutura e indicar onde encontrar as informações necessárias para iniciar uma atividade.

> **Importante:** não é necessário conhecer todo o projeto antes de começar. As informações devem ser consultadas conforme a atividade que será realizada.

---

## 2. Acesso ao projeto

O projeto está hospedado no GitHub.

Antes de iniciar uma atividade no código, a participante deve obter uma cópia do repositório para trabalhar localmente.

### 2.1 Fork do repositório

O fork cria uma cópia do repositório na conta da participante.

Para realizar o fork:

1. Acesse o repositório do projeto no GitHub.
2. Clique em **Fork**.
3. Selecione a conta em que o repositório deverá ser criado.
4. Aguarde a criação do repositório.

### 2.2 Clone do projeto

Depois de realizar o fork, o projeto deve ser clonado para o computador.

1. Acesse o repositório criado a partir do fork.
2. Clique em **Code**.
3. Copie a URL do repositório.
4. Abra o terminal na pasta em que deseja armazenar o projeto.
5. Execute o comando abaixo:

```bash
git clone URL_DO_REPOSITORIO
```

6. Entre na pasta do projeto:

```bash
cd discord-bot-tech-girls
```

### 2.3 Abrir o projeto

Depois de clonar o projeto, abra a pasta na IDE de sua preferência.

No Visual Studio Code:

1. Abra o Visual Studio Code.
2. Selecione **File > Open Folder**.
3. Selecione a pasta do projeto clonada.

A partir desse momento, os arquivos do projeto poderão ser consultados e alterados localmente.

---

## 3. Configuração do ambiente

A configuração do ambiente deve ser realizada quando for necessário executar ou desenvolver o projeto localmente.

### 3.1 Arquivo `.env`

O projeto possui um arquivo `.env.example`, que apresenta as variáveis de ambiente utilizadas pelo projeto.

Para criar o arquivo de configuração local:

1. Localize o arquivo `.env.example` na raiz do projeto.
2. Crie uma cópia desse arquivo.
3. Renomeie a cópia para `.env`.
4. Preencha as variáveis de ambiente com os valores fornecidos pela equipe.

> **Importante:** informações sensíveis, como tokens e chaves de API, não devem ser compartilhadas ou adicionadas ao repositório.

### 3.2 Dependências

As dependências utilizadas pelo projeto estão descritas nos arquivos de requisitos do repositório.

Consulte o `README.md` e os arquivos de requisitos para seguir as orientações de instalação.

As instruções de instalação não precisam ser repetidas neste documento quando já estiverem descritas em outros arquivos do projeto.

---

## 4. Conhecendo a estrutura do projeto

Depois de acessar o repositório, é importante conhecer a localização dos principais arquivos e diretórios.

### `src/`

Diretório relacionado ao código-fonte do projeto.

Os arquivos relacionados à implementação do bot devem ser consultados nesse diretório.

### `tests/`

Diretório destinado aos testes do projeto.

Os testes devem ser consultados e utilizados de acordo com a atividade que está sendo realizada.

### `docs/`

Diretório destinado à documentação do projeto.

Nele estão disponíveis materiais de orientação e documentação relacionados ao desenvolvimento do projeto.

### `.env.example`

Arquivo utilizado como referência para as variáveis de ambiente necessárias para o projeto.

### `requirements.txt`

Arquivo que contém as dependências utilizadas pelo projeto.

### `Dockerfile`

Arquivo relacionado à configuração da imagem utilizada para execução do projeto com Docker.

### `docker-compose.yml`

Arquivo utilizado para definir a configuração dos serviços executados com Docker Compose.

### `README.md`

Documento que apresenta informações gerais e orientações sobre o projeto.

---

## 5. Primeiros passos para trabalhar no bot

Depois de acessar o projeto e realizar a configuração necessária, a participante deve:

1. Consultar o `README.md`.
2. Consultar a documentação disponível em `docs/`.
3. Identificar a atividade que deverá realizar.
4. Entender o objetivo da atividade antes de alterar o código.
5. Localizar os arquivos relacionados à atividade.
6. Consultar os testes existentes quando necessário.
7. Realizar a alteração solicitada.
8. Verificar o funcionamento da alteração.
9. Compartilhar o resultado com a equipe para revisão.

Não é necessário conhecer todo o código do bot antes de começar uma atividade.

O ideal é entender primeiro o contexto da tarefa e localizar os arquivos relacionados ao que precisa ser alterado.

---

## 6. Fluxo de trabalho

Ao receber uma atividade, siga as etapas:

1. Leia a descrição da atividade.
2. Identifique o que precisa ser realizado.
3. Consulte a documentação relacionada.
4. Localize os arquivos envolvidos.
5. Realize a alteração.
6. Execute as verificações ou testes necessários.
7. Verifique se a alteração funciona conforme esperado.
8. Compartilhe o resultado com a equipe para revisão.

Durante o desenvolvimento, registre as dúvidas ou dificuldades encontradas.

Ao solicitar ajuda, informe:

- o que você estava tentando fazer;
- quais etapas já realizou;
- o que já foi pesquisado;
- qual erro ou dificuldade foi encontrada, quando houver.

---

## 7. Onde buscar informações

Antes de solicitar ajuda, consulte os materiais disponíveis no projeto.

### `README.md`

Utilize o README para consultar informações gerais e orientações iniciais sobre o projeto.

### `docs/`

Consulte a documentação disponível para encontrar informações específicas sobre o projeto e suas funcionalidades.

### `src/`

Consulte o código-fonte quando precisar localizar a implementação relacionada à atividade.

### `tests/`

Consulte os testes quando precisar verificar o comportamento esperado de uma funcionalidade ou validar uma alteração.

Caso a informação necessária não seja encontrada na documentação, procure a equipe responsável pela atividade.

---

## 8. Dúvidas frequentes

### O que devo fazer depois de acessar o repositório?

Faça um fork do repositório, clone o projeto para o computador e abra a pasta na IDE de sua preferência.

### Preciso conhecer todo o projeto antes de começar?

Não. O projeto pode ser conhecido gradualmente conforme as atividades forem realizadas.

### Onde encontro as dependências?

Consulte o `requirements.txt` e as orientações disponíveis no `README.md`.

### Onde encontro o código do bot?

O código-fonte do projeto está localizado no diretório `src/`.

### Onde encontro os testes?

Os testes estão localizados no diretório `tests/`.

### Onde encontro a documentação?

A documentação está localizada no diretório `docs/`, além das orientações gerais disponíveis no `README.md`.

### O que faço se encontrar um erro?

Primeiro, consulte a documentação e verifique a mensagem apresentada pelo erro.

Caso o problema permaneça, procure a equipe responsável pela atividade e informe o que você estava tentando fazer, quais etapas já realizou e qual erro foi apresentado.

---

## 9. Orientações importantes

- Consulte a documentação antes de realizar alterações no projeto.
- Não compartilhe tokens, chaves de API ou outras informações sensíveis.
- Não adicione informações sensíveis ao repositório.
- Consulte os testes disponíveis quando necessário.
- Ao pedir ajuda, informe o que já foi pesquisado e tentado.
- Em caso de dúvida sobre uma atividade, procure a equipe responsável.

> **O onboarding é um ponto de partida para conhecer o projeto e começar a contribuir. Para informações específicas sobre uma funcionalidade, consulte a documentação correspondente.**



# Manual de Ferramentas BOT Tech Girls 
 
## Docker 
A ferramenta Docker é uma plataforma de contêineres que permite a padronização do ambiente de execução e de aplicação, permitindo que os usuários executem o Bot em diferentes ambientes, ou seja, em diferentes máquinas. 
 
## GIT 
O Git é um sistema de controle de versão distribuído. Ele controla e registra as versões de um arquivo, ou seja, é como um histórico das modificações realizadas. Através dele conseguimos consultar passos anteriores e modificar o que se faz necessário sem perder todo o processo. 
 
## GitHub 
Github é como se fosse a rede social do desenvolvedor, ele permite que diversas pessoas, em diversos locais consigam desenvolver juntas através de commits e pull requests. E é no GitHub que o projeto está hospedado. 
 
## Python 
Python é a linguagem de programação utilizada no desenvolvimento do bot. Toda a lógica da aplicação, incluindo integrações com APIs e gerenciamento do banco de dados, foi realizada nessa linguagem. 
 
## Discord API (através do discord.py) 
A Discord API permite que aplicações externas interajam com a plataforma Discord. Neste projeto, ela é utilizada para possibilitar que o bot envie informações, publique notícias e execute comandos dentro dos servidores da comunidade. 
 
## SQLite 
SQLite é o banco de dados utilizado pelo projeto para armazenar informações persistentes. Neste bot, ele é responsável por registrar notícias já publicadas e armazenar os canais configurados para receber conteúdo. 
 
# Referências 
 
https://docs.docker.com 
https://git-scm.com 
https://docs.github.com 
https://www.python.org 
https://docs.discord.com 
https://sqlite.org



# Documentação de APIs e Serviços Técnicos
Este documento descreve as integrações de APIs externas e os comandos do bot do Discord para a comunidade Tech Girls.

## Sumário
1. Visão Geral 
2. APIs e Serviços Externos
    - 2.1 API do TabNews
    - 2.2 API do JSearch 
    - 2.3 API do Gemini 3.5-flash

## 1. Visão Geral
O projeto consiste em um bot automatizado desenvolvido para realizar a pesquisa de conteúdos e oportunidades de mercado na área da tecnologia. Ele opera através da integração de três APIs principais.

## 2. APIs e Serviços Externos
Serviços Externos são plataformas/ banco de dados/ ferramentas de terceiros hospedadas fora do servidor do bot. Ou seja, ao invés de criar as funções complexas do zero, o bot consulta esses serviços prontos. 

O termo API (Application Programming Interface) se refere a uma "ponte" de comunicação padronizada que permite o trafego de informações entre diferentes sistemas. Ou seja, permite que o código do bot converse com serviços externos, de forma que o bot envia um pedido (requisição) no formato exigido e a API responde com as informações solicitadas.

### 2.1 API do TabNews

* **Descrição:** Busca os conteúdos e notícias mais recentes publicados no TabNews para divulgar nos canais do Discord
* **URL/ Endpoint:** "https://www.tabnews.com.br/api/v1/contents"
* **Método:** GET => o bot está apenas lendo/buscando notícias do TabNews
* **Autenticação:** API pública
* **Parâmetros Principais:** 
   - Nenhum parâmetro obrigatório é passado nessa função (busca a lista padrão de notícias)
* **O que devolve:** Uma lista JSON em `new_list`
    - Exemplo: `{`
                `"id_noticia": ["id"],`
                `"titulo" : ["title"],`
                `"autor" : ["owner_username"]`
                `}`

### 2.2 API do JSearch via RapidAPI (Busca de vagas)

* **Descrição:** Serviço responsável por buscar oportunidades de trabalho na área de tecnologia
* **URL/ Endpoint:** https://jsearch.p.rapidapi.com/search
* **Método:** GET => o bot está apenas consultando/filtrando vagas no JSearch
* **Autenticação:** requer API Key da RapidAPI (armazenada como `RAPIDAPI_KEY` no arquivo `.env`)
* **Parâmetros Principais:** 
    - `query`: termo de busca das vagas ("software engineer"/"backend developer")
    - `country`: país da oportunidade ("br")
    - `date_posted`: filtro de data ("all")
    - `num_pages`: numero de páginas retornadas ("1")
* **O que devolve:** Uma resposta no formato JSON contendo uma lista de vagas encontradas.
    - Exemplo: status da requisição e uma lista com os detalhes da vaga
        `{"status": "OK",`
         `"data": [`
           ` {`
                `"TECH_QUERY": "Software Engineer",`
                `"JSEARCH_FALLBACK_QUERY = "backend developer"`
                `"JSEARCH_COUNTRY" : "br"`
                `"JSEARCH_DATE_POSTED" : "all" `
            `}]}`


### 2.3 API do Gemini 3.5-flash

* **Descrição:** Serviço de IA responsável por analisar/validar o conteúdo das notícias coletadas
* **URL/ Endpoint:**  acesso via SDK oficial (`google-genai`)
* **Método:** chamada de SDK/ POST
* **Autenticação:** requer API Key do Google AI Studio (armazenada como `GEMINI_API_KEY` no arquivo `.env`)
* **Parâmetros Principais:** 
    - chave de acesso(`api_key`): chave de autenticação enviada ao cliente SDK (puxada de `GEMINI_API_KEY` no arquivo `.env`)
    - `contents`: O texto enviado para processamento `conteudo_prompt`, composto pela junção de `prompt_sistema` e `texto_noticia`
        - `prompt_sistema`: instrução pré-definida para a IA sobre como analisar a notícia
        - `texto_noticia`: o conteudo completo do artigo/noticia coletado do TabNews
    - modelos de IA (`modelos_candidatos`): lista de versões do Gemini 
        - testadas via lista de fallback:
            - `gemini-3.6-flash`
            - `gemini-2.0-flash`
            - `gemini-3.5-flash`
* **O que devolve:** `resposta.text` => um texto em formato JSON contendo a análise/resumo gerado pela IA, depois que passar por uma limpeza (limpeza_resposta_json)
    - Exemplo: 
            - Exemplo (notícia aprovada):
                json
                `{`
                    `"relevante": True,`
                    `"titulo": titulo.strip(),`
                    `"tags": tags_validadas,`
                    `"texto-resumo":` 
                    `resumo_normalizado,`
                    `"link-de-acesso": target_url,`
                `}`

                # **Glossário Técnico — Tech Girls**



## **Glossário técnico**


## **A**

### **Algoritmo**

* **O que significa:** É uma sequência organizada de passos para resolver um problema ou realizar uma tarefa.  
* **Para que serve:** Serve como um caminho que o programa segue para chegar a um resultado.

### **Ambiente de desenvolvimento**

* **O que significa:** É o conjunto de ferramentas e configurações usadas para criar e testar um programa.  
* **Para que serve:** Serve para permitir que uma pessoa desenvolva, execute e teste um projeto em seu computador.

### **Ambiente de execução**

* **O que significa:** É o conjunto de condições e recursos necessários para que um programa funcione.  
* **Para que serve:** Serve para fornecer ao programa o que ele precisa para ser executado corretamente.

### **API (Application Programming Interface)**

* **O que significa:** É uma forma de comunicação que permite que diferentes sistemas troquem informações.  
* **Para que serve:** Serve para um sistema enviar um pedido a outro sistema e receber uma resposta.

### **Aplicação**

* **O que significa:** É um programa criado para realizar uma ou mais tarefas.  
* **Para que serve:** Serve para executar funções específicas de acordo com o que foi programado.

### **Arquivo de configuração**

* **O que significa:** É um arquivo que guarda informações usadas para definir como um programa deve funcionar.  
* **Para que serve:** Serve para alterar configurações da aplicação sem precisar modificar diretamente o código.

### **Autenticação**

* **O que significa:** É o processo de confirmar a identidade de uma pessoa ou aplicação.  
* **Para que serve:** Serve para controlar quem pode acessar determinado sistema ou serviço.

---

## **B**

### **Banco de dados**

* **O que significa:** É um sistema usado para armazenar, organizar e consultar informações.  
* **Para que serve:** Serve para guardar dados que a aplicação precisa utilizar posteriormente.

### **Backend**

* **O que significa:** É a parte de um sistema que funciona por trás daquilo que o usuário vê.  
* **Para que serve:** Serve para processar informações, executar regras e cuidar dos dados da aplicação.

### **Board**

* **O que significa:** É um quadro visual utilizado para organizar tarefas de um projeto.  
* **Para que serve:** Serve para a equipe acompanhar as atividades e saber o que está sendo feito.

### **Bot**

* **O que significa:** É um programa criado para realizar tarefas automaticamente.  
* **Para que serve:** Serve para executar ações sem que uma pessoa precise realizar cada etapa manualmente.

### **Bug**

* **O que significa:** É um erro que faz um programa apresentar um comportamento diferente do esperado.  
* **Para que serve:** O registro de um bug ajuda a identificar o que precisa ser investigado e corrigido.

---

## **C**

### **Cache**

* **O que significa:** É um espaço usado para guardar temporariamente informações que podem ser utilizadas novamente.  
* **Para que serve:** Serve para evitar que o sistema precise buscar ou processar a mesma informação várias vezes.

### **Card**

* **O que significa:** É um item dentro de um board que representa uma tarefa ou atividade.  
* **Para que serve:** Serve para organizar uma tarefa, indicar quem é responsável por ela e acompanhar seu andamento.

### **Cliente**

* **O que significa:** É o programa ou dispositivo que faz um pedido a outro sistema.  
* **Para que serve:** Serve para solicitar ou enviar informações para um servidor.

### **Código**

* **O que significa:** É um conjunto de instruções escritas para dizer ao computador o que ele deve fazer.  
* **Para que serve:** Serve para criar o funcionamento de programas e sistemas.

### **Commit**

* **O que significa:** É um registro de alterações realizadas em um projeto.  
* **Para que serve:** Serve para guardar no histórico o que foi modificado no código.

### **Contêiner**

* **O que significa:** É um ambiente isolado que reúne uma aplicação e os recursos necessários para seu funcionamento.  
* **Para que serve:** Serve para ajudar uma aplicação a funcionar de maneira padronizada em diferentes computadores.

### **Controle de versão**

* **O que significa:** É o processo de registrar e acompanhar as alterações feitas em um projeto.  
* **Para que serve:** Serve para consultar mudanças anteriores e acompanhar a evolução do projeto.

### **Configuração**

* **O que significa:** É o conjunto de ajustes e informações necessários para definir como um programa deve funcionar.  
* **Para que serve:** Serve para preparar a aplicação de acordo com as necessidades do projeto.

---

## **D**

### **Debug (depuração)**

* **O que significa:** É o processo de investigar um programa para encontrar a causa de um erro.  
* **Para que serve:** Serve para localizar e corrigir problemas no funcionamento do código.

### **Dependência**

* **O que significa:** É um recurso externo que um projeto precisa para funcionar.  
* **Para que serve:** Serve para permitir que o programa utilize recursos ou funções já existentes.

### **Deploy**

* **O que significa:** É o processo de disponibilizar uma aplicação em um ambiente onde ela possa ser utilizada.  
* **Para que serve:** Serve para colocar o projeto em funcionamento para seus usuários.

### **Dados persistentes**

* **O que significa:** São informações que continuam armazenadas mesmo depois que um programa é fechado.  
* **Para que serve:** Servem para manter informações disponíveis quando a aplicação for utilizada novamente.

---

## **E**

### **Endpoint**

* **O que significa:** É um endereço específico de uma API usado para acessar uma informação ou realizar uma ação.  
* **Para que serve:** Serve para indicar para onde determinado pedido deve ser enviado.

### **Execução**

* **O que significa:** É o momento em que um programa realiza as instruções que foram escritas para ele.  
* **Para que serve:** Serve para fazer com que o código realmente realize as tarefas programadas.

---

## **F**

### **Fork**

* **O que significa:** É uma cópia de um repositório criada na conta de outra pessoa.  
* **Para que serve:** Serve para permitir alterações em um projeto sem modificar diretamente o repositório original.

### **Frontend**

* **O que significa:** É a parte de um sistema com a qual o usuário interage diretamente.  
* **Para que serve:** Serve para apresentar informações e permitir que o usuário realize ações no sistema.

---

## **I**

### **IDE (Ambiente Integrado de Desenvolvimento)**

* **O que significa:** É um programa que reúne diferentes ferramentas usadas para desenvolver software.  
* **Para que serve:** Serve para facilitar tarefas como escrever, testar e executar código.

### **Integração**

* **O que significa:** É a conexão entre diferentes sistemas ou ferramentas.  
* **Para que serve:** Serve para permitir que diferentes sistemas trabalhem juntos e troquem informações.

### **Interface**

* **O que significa:** É a forma pela qual uma pessoa ou programa interage com um sistema.  
* **Para que serve:** Serve para permitir a comunicação entre o usuário e o sistema ou entre diferentes programas.

---

## **J**

### **JSON**

* **O que significa:** É um formato de texto usado para organizar e trocar informações entre sistemas.  
* **Para que serve:** Serve para estruturar dados que podem ser enviados ou recebidos por uma aplicação.

---

## **L**

### **Linguagem de programação**

* **O que significa:** É uma forma de escrever instruções que o computador consegue interpretar.  
* **Para que serve:** Serve para criar programas e definir as tarefas que eles devem realizar.

### **Log**

* **O que significa:** É um registro dos acontecimentos de um sistema durante seu funcionamento.  
* **Para que serve:** Serve para ajudar a entender o que aconteceu, principalmente quando ocorre algum problema.

### **Lógica de programação**

* **O que significa:** É a forma de organizar instruções para resolver um problema.  
* **Para que serve:** Serve para definir a sequência de ações que um programa deve realizar.

---

## **M**

### **Merge**

* **O que significa:** É a ação de juntar alterações feitas em uma parte do projeto com outra versão do projeto.  
* **Para que serve:** Serve para reunir o trabalho realizado por diferentes pessoas em um único projeto.

---

## **P**

### **Pacote (Package)**

* **O que significa:** É um conjunto de códigos prontos que pode ser utilizado em um projeto.  
* **Para que serve:** Serve para adicionar recursos ao programa sem precisar criar tudo do zero.

### **Pull Request (PR)**

* **O que significa:** É uma solicitação para que alterações feitas em um projeto sejam revisadas.  
* **Para que serve:** Serve para permitir que outras pessoas analisem as mudanças antes de elas serem adicionadas ao projeto principal.

### **Persistência de dados**

* **O que significa:** É a capacidade de manter informações armazenadas mesmo depois que um programa é encerrado.  
* **Para que serve:** Serve para que os dados continuem disponíveis quando forem necessários novamente.

### **Projeto**

* **O que significa:** É um conjunto de arquivos, códigos, tarefas e recursos criados para desenvolver uma solução.  
* **Para que serve:** Serve para organizar o trabalho necessário para alcançar determinado objetivo.

---

## **Q**

### **Query**

* **O que significa:** É um pedido feito para buscar informações em um banco de dados ou serviço.  
* **Para que serve:** Serve para solicitar dados específicos de acordo com uma necessidade.

---

## **R**

### **Repositório**

* **O que significa:** É o local onde os arquivos de um projeto e seu histórico de alterações ficam armazenados.  
* **Para que serve:** Serve para organizar o projeto e permitir que diferentes pessoas trabalhem nele.

### **Requisição (Request)**

* **O que significa:** É um pedido enviado por um sistema para outro sistema.  
* **Para que serve:** Serve para solicitar uma informação ou pedir que determinada ação seja realizada.

### **Resposta (Response)**

* **O que significa:** É a informação devolvida por um sistema depois de receber uma requisição.  
* **Para que serve:** Serve para informar o resultado do pedido realizado.

---

## **S**

### **Servidor**

* **O que significa:** É um computador ou sistema responsável por receber pedidos e fornecer informações ou serviços.  
* **Para que serve:** Serve para processar solicitações feitas por outros programas e enviar respostas.

### **Serviço externo**

* **O que significa:** É um serviço fornecido por outro sistema e utilizado por uma aplicação.  
* **Para que serve:** Serve para utilizar recursos de outros sistemas sem precisar desenvolver essas funções dentro do próprio projeto.

### **Sistema**

* **O que significa:** É um conjunto de elementos que trabalham juntos para realizar determinadas funções.  
* **Para que serve:** Serve para organizar recursos e processos para alcançar um objetivo.

### **Software**

* **O que significa:** É um programa ou conjunto de programas utilizados para realizar tarefas em um computador ou outro dispositivo.  
* **Para que serve:** Serve para executar funções específicas de acordo com o que foi programado.

---

## **T**

### **Terminal**

* **O que significa:** É uma ferramenta que permite interagir com o computador digitando comandos.  
* **Para que serve:** Serve para executar programas, instalar recursos e realizar tarefas por meio de comandos de texto.

### **Token**

* **O que significa:** É um código usado para identificar ou autorizar o acesso de uma aplicação a determinado serviço.  
* **Para que serve:** Serve para permitir que uma aplicação seja reconhecida e tenha acesso autorizado.

---

## **U**

### **URL (Uniform Resource Locator)**

* **O que significa:** É o endereço usado para localizar um recurso na internet.  
* **Para que serve:** Serve para indicar onde uma página, arquivo ou outro recurso pode ser encontrado.

---

## **V**

### **Variável**

* **O que significa:** É um espaço usado pelo programa para armazenar uma informação.  
* **Para que serve:** Serve para guardar valores que podem ser utilizados ou alterados durante a execução do programa.

### **Variável de ambiente**

* **O que significa:** É uma informação usada para configurar o funcionamento de um programa.  
* **Para que serve:** Serve para guardar configurações que podem variar de acordo com o ambiente em que a aplicação está sendo executada.

### **Versionamento**

* **O que significa:** É o processo de registrar diferentes versões de um projeto ao longo do tempo.  
* **Para que serve:** Serve para acompanhar alterações, comparar versões e recuperar estados anteriores do projeto.

### **Versão**

* **O que significa:** É o estado de um arquivo ou projeto em determinado momento.  
* **Para que serve:** Serve para identificar e acompanhar diferentes momentos do desenvolvimento.

---

## **W**

### **Webhook**

* **O que significa:** É um mecanismo que permite que um sistema envie automaticamente uma informação para outro quando determinado evento acontece.  
* **Para que serve:** Serve para criar comunicações automáticas entre diferentes sistemas.


 ### Equipe e Responsabilidades

| Responsável | Função / Atribuição |
| :--- | :--- |
| **@keilaGuimaraes9** | Onboarding e roteiro de boas-vindas |
| **@greicesantellano** | Manuais de ferramentas |
| **@larijbpg** | Documentação de dados e APIs |
| **@luanapersouzza** | Definição de formato padrão e revisão final |
| **@EmanuellePereira10** | Glossário e revisão de conteúdo |
