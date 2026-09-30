
# D10 · Audits

Esta dimensão conta as entidades de domínio que exigem trilha de auditoria — o registro respondível a um auditor ou regulador de QUEM fez O QUÊ e QUANDO sobre cada conceito de negócio. Contam entidades auditadas, não eventos nem campos.

## O que o avaliador procura

- Entidades de domínio com necessidade explícita de trilha de accountability: foi alterada? quando? por quem?
- Um requisito de auditoria é explícito quando a story descreve sem ambiguidade o rastreamento de quem/o quê/quando para fins de prestação de contas — mesmo sem usar as palavras "auditoria" ou "log". "O sistema deve responder quem alterou o quê e quando" já caracteriza uma entidade auditada.
- A contagem é por entidade, independente da quantidade de eventos auditáveis: auditar criação + modificação + exclusão + acesso de Order continua sendo uma entidade.
- A contagem é por entidade, independente da quantidade de campos do registro: um log com 8 campos (user_id, action, timestamp, IP, valores antigo e novo...) sobre uma entidade continua sendo uma entidade.

O que NÃO é auditoria:

- Logging operacional e observabilidade: structured logging, métricas, tracing, monitoramento, request ID — são ferramentas de desenvolvedor para depurar e operar o software, não trilha de negócio.
- Logs de manutenção criados para debug e operação — são requisitos não funcionais, não auditoria.
- Declarações vagas de capacidade: "garantir que todas as ações sejam auditáveis", "o sistema deve ser auditável", "deve suportar audit logging" — atributo de qualidade sem escopo definido, sem dizer QUE entidade é auditada.
- Frases com verbos como "garantir"/"ensure" sem especificar a entidade auditada — lembrete ao desenvolvedor, não requisito contável; é lacuna a esclarecer.

## O que torna a escrita fraca

- Escrever "garantir auditabilidade" ou "todas as ações devem ser auditáveis" sem nomear nenhuma entidade — o avaliador não consegue contar e marca como lacuna.
- Misturar observabilidade com auditoria na mesma frase ("adicionar logs de auditoria com tracing e request ID") — o avaliador separa os dois, e a ambiguidade gera descarte do requisito.
- Detalhar campos do log ("registrar ID do artigo, ID do usuário, data/hora, IP, ação") sem deixar claro qual entidade está sendo auditada — os campos não contam, a entidade sim.
- Listar eventos auditáveis como se fossem requisitos separados ("auditar criação, auditar modificação, auditar exclusão") sem amarrá-los à mesma entidade — o avaliador agrupa por entidade, e a redação fragmentada gera instabilidade.
- Deixar implícito que "é claro" que algo precisa de trilha — só o explícito conta.

## O que deixar explícito

- O nome de cada entidade de domínio que precisa de trilha: Article, Order, Customer, User.
- A finalidade de accountability: poder responder quem fez o quê e quando sobre aquela entidade.
- Os eventos auditáveis como características da entidade, não como requisitos soltos: "auditar criação e modificação de Order" é uma entidade com dois eventos.
- A distinção de vocabulário: trilha de auditoria (quem/o quê/quando, respondível a auditor) versus logging operacional (debug, métricas, tracing) — se ambos existirem, escreva-os como requisitos separados.

## Exemplos de escrita

### ❌ Fraca
> "Garantir que todas as ações do sistema sejam auditáveis, com logs estruturados e request ID para rastreabilidade."

### ✅ Bem escrita
> "O sistema deve manter trilha de auditoria da entidade Course, registrando o que foi alterado, quando e por qual instrutor, de forma respondível a uma auditoria. (Logging operacional com request ID é requisito não funcional separado.)"

### ❌ Fraca
> "Auditar criação, modificação e exclusão; registrar user_id, timestamp, IP, ação, valor antigo e novo; e logar acessos."

### ✅ Bem escrita
> "Duas entidades exigem trilha de auditoria: Order (quem criou e quem modificou, e quando) e Customer (quem acessou os dados, e quando)."

## Perguntas típicas para o questionário

- Quais entidades de negócio precisam de trilha de quem fez o quê e quando? Liste pelo nome.
- Para cada entidade, quais eventos são auditáveis (criação, modificação, exclusão, acesso)?
- A menção a "log" na story é trilha de negócio (respondível a auditor/regulador) ou logging operacional para debug e monitoramento?
- Há frases com "garantir"/"assegurar auditabilidade" sem entidade definida? Qual entidade concreta está por trás?
