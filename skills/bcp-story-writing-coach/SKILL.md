---
name: bcp-story-writing-coach
description: >
  (flow-ciandt) Reescreve stories existentes usando as regras de scoring das 13 dimensões BCP
  como guia de escrita — sem calcular BCP, sem pontuar, sem inventar requisitos.
  Use quando o usuário quiser melhorar a qualidade de escrita de uma story, revisar uma story
  antes do cálculo de BCP, ou tornar explícito o que está implícito/ausente via questionário
  dirigido por lacunas. Triggers: "melhorar escrita da story", "revisar story BCP",
  "reescrever story", "story writing coach", "bcp-story-writing-coach", "coach de escrita BCP".
---

# BCP Story Writing Coach

A análise estatística dos batches de BCP mostrou que parte significativa da instabilidade de
pontuação vem da **qualidade de escrita da story**, não do modelo nem do prompt. Nenhum ajuste de prompt resolve story mal escrita — é preciso atacar a causa na origem.

Esta skill reescreve stories existentes usando as **regras de scoring das 13 dimensões BCP**
como guia de escrita. Ela **não calcula BCP**, **não pontua**, **não inventa requisitos** —
só torna explícito o que já está implícito ou ausente, via questionário dirigido por lacunas.

| Responsabilidade | Skill |
|------------------|-------|
| Calcular BCP, CMS, IMS | `bcp-calculator-13d` |
| Gerar stories do zero com alta maturidade | `feature-refinement-bcp-high-maturity` |
| **Reescrever story existente para melhorar escrita** | **esta skill** |

### 🌐 Idioma

**O output segue o idioma da story original.** Se a story está em pt-BR, a versão limpa, o diff anotado, o racional e as perguntas do questionário são em pt-BR. Os nomes das dimensões
(D1 · Business Rules, D12 · Security & Compliance, etc.) mantêm o nome original em inglês —
são termos do domínio.

### ⚠️ Princípio inviolável — Sem invenção

Toda alteração na story reescrita deve ser rastreável a uma destas fontes:

1. **Conteúdo explícito** — já escrito na story original
2. **Conteúdo implícito** — dedução direta e óbvia do texto (ex.: "formulário de cadastro"
   implica campos de input; a reescrita pode nomeá-los como tal)
3. **Resposta do usuário** — obtida no questionário dirigido por lacunas

Lacunas que o usuário não respondeu ficam **explicitamente marcadas como "não endereçado"**
no output, com o impacto explicado. Nunca preencha uma lacuna por conta própria.

### 📏 Calibragem de expectativa — o que a skill entrega

O valor entregue depende diretamente das respostas ao questionário:

- **Story bem encaminhada + questionário respondido** → a versão limpa sai completa e avaliável; esse é o caso ideal
- **Story muito vaga + questionário respondido** → a versão limpa melhora muito, porque o conteúdo estava fora do texto (na cabeça do PO) e o questionário o trouxe para dentro
- **Questionário não respondido (ou respondido parcialmente)** → o produto útil é o
**mapa de lacunas + o questionário dirigido**, não a versão limpa. A reescrita sairá honesta, mas modesta — isso é o comportamento correto, não uma falha. Uma reescrita "rica" sem respostas seria invenção. Comunique isso ao usuário quando a story for pobre: a versão limpa é tão boa quanto as respostas que ela recebe.

---

## Passo 1 — Receber a story

| Fonte | Como obter |
|-------|-----------|
| Texto colado no chat | Use diretamente |
| Arquivo `.md` | Leia o arquivo inteiro |
| Pasta de stories | Processe uma por vez — confirme com o usuário qual reescrever primeiro |

Se o usuário acionar a skill **sem fornecer uma story**, solicite o conteúdo antes de
prosseguir. Não tente reescrever sem input.

---

## Passo 2 — Análise estática: dimensões relevantes e lacunas

Leia a story e determine, **para cada uma das 13 dimensões**, se ela é:

- **Relevante e coberta** — a dimensão se aplica à story e já está bem escrita
- **Relevante com lacunas** — a dimensão se aplica, mas há informação implícita ou ausente
- **Não relevante** — a dimensão não se aplica a esta story (ex.: D9 · Notifications numa
  story sem nenhum evento que dispare notificação a humano)

Use os arquivos em `rules/` como guia de leitura — um arquivo por dimensão:

```
rules/
├── README.md                      # índice + como ler as regras
├── d01-business-rules.md          # D1  · Business Rules
├── d02-interface-elements.md      # D2  · Interface Elements
├── d03-boundaries.md              # D3  · Boundaries
├── d04-roles-permissions.md       # D4  · Roles & Permissions
├── d05-solution-variabilities.md  # D5  · Solution Variabilities
├── d06-domain-entities.md         # D6  · Domain Entities
├── d07-new-domain-entities.md     # D7  · New Domain Entities
├── d08-background-processes.md    # D8  · Background Processes
├── d09-notifications.md           # D9  · Notifications
├── d10-audits.md                  # D10 · Audits
├── d11-quality-attributes.md      # D11 · Quality Attributes (NFR)
├── d12-security-compliance.md     # D12 · Security & Compliance (NFR)
└── d13-ux-accessibility.md        # D13 · UX & Accessibility (NFR)
```

Cada arquivo descreve, em formato pedagógico e **sem expor tiers nem valores numéricos de
scoring**, o que o avaliador BCP procura naquela dimensão — e portanto o que a story precisa
deixar explícito para ser bem avaliada.

**Leia apenas os arquivos das dimensões candidatas.** Nem toda story toca as 13 dimensões:
leia primeiro a story, liste as dimensões candidatas pelo conteúdo, e só então carregue os
arquivos correspondentes (progressive disclosure).

**Regras da análise estática:**

- **Nunca pergunte sobre dimensões não relevantes.** Se a story não tem nenhum processo em
  background, D8 está fora do questionário.
- Uma **lacuna** é qualquer informação que a dimensão relevante precisa e que não está nem
  explícita nem implicitamente dedutível do texto.
- Registre a lacuna no formato: `<dimensão> — <o que falta> — <por que importa para a
  avaliação>`.

### Gate de escopo — épico disfarçado de story

Antes de abrir o questionário, cheque o tamanho do que a story pede. Sinais de épico disfarçado: vários módulos ou subsistemas independentes no mesmo pedido (ex.: "gerencie alunos, pagamentos, check-in, relatórios e app"), um sistema inteiro descrito em uma frase, ou escopo que nenhum questionário consegue fechar em poucas rodadas.

Nesse caso, **pare antes do questionário** e diga explicitamente:

- A story é grande demais para ser reescrita como uma unidade avaliável
- Recomende o fatiamento, sugerindo o corte pelas fronteiras que já aparecem no texto (ex.: um módulo por story)
- Pergunte se o usuário quer (a) escolher uma fatia para reescrever agora ou (b) seguir com a story inteira mesmo assim — neste caso, registre o escopo como a primeira linha da tabela de lacunas não endereçadas, com o impacto ("avaliação instável por escopo composto: cada módulo pontuaria diferente isoladamente")

---

## Passo 3 — Questionário dirigido por lacunas

Apresente as lacunas ao usuário em **rodadas de no máximo ~5 perguntas**, priorizadas por
impacto na avaliação (lacunas que afetam a dimensão central da story primeiro).

### Fallback por relevância

Se a story for vaga demais para detectar dimensões com confiança (ex.: uma linha sem nenhum
detalhe), não tente adivinhar. Rode o **questionário de fallback por relevância**: pergunte
ao usuário quais dimensões se aplicam, apresentando a lista em linguagem de negócio:

```
Esta story está muito resumida para eu detectar as dimensões relevantes com segurança.
Quais destes temas ela toca?

  [ ] Regras de negócio com condições/cálculos (D1)
  [ ] Telas, formulários ou componentes visuais (D2)
  [ ] Integração com sistemas externos ou dispositivos (D3)
  [ ] Diferença de acesso entre perfis de usuário (D4)
  [ ] Comportamento que varia por condição, convergindo ao mesmo resultado (D5)
  [ ] Entidades de negócio manipuladas (D6)
  [ ] Criação de novas entidades ou novos atributos em entidades existentes (D7)
  [ ] Processos agendados, assíncronos ou disparados por eventos (D8)
  [ ] Notificações a pessoas (e-mail, SMS, push, in-app) (D9)
  [ ] Trilha de auditoria de quem fez o quê e quando (D10)
  [ ] Requisitos de performance, SLA, escalabilidade (D11)
  [ ] Autenticação, autorização, criptografia, compliance (D12)
  [ ] Acessibilidade, responsividade, internacionalização (D13)
```

Só prossiga com as dimensões marcadas.

### Modo misto — detectável, mas não dedutível

Há um caso intermediário entre "vaga demais" e "detectável": a story dá sinais suficientes para **detectar** dimensões candidatas (ex.: menciona uma tela, um papel, um sistema externo), mas não permite **deduzir** nada dentro delas. Não é um ou outro — combine:

1. Liste as dimensões detectadas, marcando-as como "candidatas — confirme"
2. Apresente também a lista de fallback em linguagem de negócio para o usuário marcar o que mais se aplica
3. Só então rode o questionário dirigido sobre as dimensões confirmadas

Não pule a confirmação: detectar sem confirmar infla o questionário com verificações de irrelevância que o usuário teria resolvido em uma rodada.

### Formato das perguntas

- Uma pergunta por lacuna, direta e respondível ("O cálculo de frete considera apenas CEP,
  ou também peso e dimensões?")
- Agrupe por dimensão quando houver mais de uma lacuna na mesma dimensão
- Ao final de cada rodada, pergunte se o usuário quer responder mais ou seguir para a reescrita com o que já respondeu

### Contradições internas

Se a story contém afirmações que se contradizem (ex.: "recomendações baseadas em tudo que usuário assistiu" + "não usar histórico de visualização"), trate a contradição como **bloqueio**, não como lacuna comum:

1. Nomeie a contradição explicitamente, citando os dois trechos
2. **Não reescreva o trecho contraditório** — qualquer versão escolheria um lado por conta própria, o que viola o princípio sem invenção
3. A primeira pergunta do questionário deve ser a resolução da contradição
4. Se restar sem resposta, o trecho entra na versão limpa marcado como
   **"⚠️ Contradição não resolvida"**, e na tabela do Bloco 4 com o impacto
   ("a dimensão X fica inavaliável — os dois lados puxam avaliações opostas")

### Lacunas não respondidas

Toda lacuna que restar sem resposta entra no output final marcada como
**"⚠️ Não endereçado"**, com o impacto explicado: qual dimensão fica subavaliada ou
instável e por quê.

---

## Passo 4 — Reescrita da story

Reescreva a story incorporando:

1. **Explícito** — reorganize e clarifique o que já estava escrito, sem mudar o sentido
2. **Implícito tornado explícito** — nomeie o que o texto já presume (ex.: "o formulário"
   → "o formulário com campos X e Y", desde que X e Y estejam no texto original)
3. **Respostas do questionário** — incorpore como fatos da story

**Restrições duras:**

- Não adicione requisitos, edge cases, regras ou entidades que não venham das 3 fontes acima
- Preserve a estrutura de seções da story original quando existir (Narrativa de Negócio,
  Narrativa Técnica, Critérios de Aceite). Se a story não tiver estrutura, use a estrutura
  padrão do time Flow:
  - `## Narrativa de Negócio` (com `### Regras de Negócio` e `### Edge Cases relevantes`)
  - `## Narrativa Técnica`
  - `## Critérios de Aceite`
- Preserve o idioma original da story
- Critérios de aceite que são **riscos ou dependências** não são verificáveis e não medem comportamento do sistema. Reposicione-os numa seção `## Riscos e Dependências` da versão limpa, declarados explicitamente, sem convertê-los em requisitos novos.
- Não exponha tiers (XS, S, M, L, XL) nem valores numéricos de scoring em nenhuma parte do
  output — nem no diff, nem na versão limpa, nem no racional. As regras são explicadas em
  termos de escrita ("deixe explícito quantas fontes de dados a regra consulta"), nunca em
  termos de pontuação ("isso vale 3 pontos")

---

## Passo 5 — Apresentar o output

O output tem **4 blocos obrigatórios**, nesta ordem:

### 1. Diff anotado

Mostre cada alteração como um trecho antes/depois, anotado com a fonte:

```
### Alteração 1 — Regras de Negócio (D1)

**Antes:**
> O sistema calcula o frete.

**Depois:**
> O sistema calcula o frete consultando o CEP do destino e a tabela de transportadora
> (2 fontes de dados). O cálculo considera o peso do pacote: até 5kg tarifa fixa,
> acima de 5kg tarifa por kg adicional.

**Fonte:** resposta do usuário no questionário (rodada 1, pergunta 2)
**Por quê:** a regra tem condições e múltiplas fontes de dados que estavam invisíveis;
explicitá-las estabiliza a avaliação de D1.
```

### 2. Versão limpa

A story completa reescrita, em markdown, pronta para copiar. Sem anotações de coaching.

### 3. Racional por dimensão

Uma tabela cobrindo **apenas as dimensões relevantes** (dimensões avaliadas e descartadas
não entram — a escolha de não perguntar sobre elas já foi feita no Passo 2):

```
| # | Dimensão | O que mudou na escrita |
|---|----------|------------------------|
| D1 | Business Rules | Condições e fontes de dados da regra de frete explícitas |
| D3 | Boundaries | Tabela da transportadora identificada como fonte externa perene |
```

### 4. Lacunas não endereçadas

```
### ⚠️ Lacunas não endereçadas

| # | Dimensão | Lacuna | Impacto |
|---|----------|--------|---------|
| D12 | Security & Compliance | Não respondido se a story exige autenticação | Avaliação de segurança fica instável — pode variar entre "nenhum requisito" e "requisito básico" |
```

Se não houver lacunas restantes, escreva explicitamente: `✅ Todas as lacunas foram
endereçadas.`

---

## Fluxo completo resumido

```
Passo 1: Receber a story (chat, arquivo ou pasta)
Passo 2: Análise estática — dimensões relevantes + lacunas (rules/ como guia) + gate de escopo (épico disfarçado → recomendar fatiamento)
Passo 3: Questionário dirigido por lacunas (~5 perguntas/rodada, fallback por relevância, modo misto quando detectável mas não dedutível; contradições = bloqueio)
Passo 4: Reescrita sem invenção (explícito + implícito + respostas; critérios-risco → seção Riscos e Dependências)
Passo 5: Output — diff anotado + versão limpa + racional por dimensão + lacunas não endereçadas
```

## Exemplos de acionamento

- "Reescreve essa story pra melhorar a qualidade antes de calcular o BCP: <story>"
- "Revisa a story `docs/stories/story-042.md` com o story writing coach"
- "Essa story tá instável no BCP 13d, melhora a escrita dela"
- "bcp-story-writing-coach" (acionamento direto pelo nome)
