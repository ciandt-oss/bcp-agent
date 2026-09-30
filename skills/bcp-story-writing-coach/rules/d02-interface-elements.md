
# D2 · Interface Elements

Esta dimensão mede a complexidade dos elementos visuais de interface que o usuário vê ou com os quais interage: quantos elementos distintos a story introduz ou altera, se são estáticos ou dinâmicos, e se o contexto é novo ou existente.

## O que o avaliador procura

- Apenas elementos visuais voltados ao usuário: telas, formulários, campos de entrada, botões, grids, modais, tooltips, ícones, notificações, banners e componentes similares.
- Cada elemento visualmente independente contado exatamente uma vez, mesmo que mencionado em vários critérios de aceite.
- Tipos de componente reutilizados contam uma única vez: "adicionar tooltip em 5 cards de produto" é um elemento tooltip, não cinco.
- Uma página ou tela só conta como elemento quando criada do zero; modificar uma página existente conta apenas os elementos individuais alterados.
- Qualidades não visuais não são elementos: responsividade mobile, conformidade de acessibilidade, otimizações de performance e suporte cross-browser são preocupações de implementação.
- Classificação de cada elemento:
  - **Estático**: conteúdo, posição, estado ou visualização não mudam depois de apresentado (inputs de texto, labels, mensagens de erro/sucesso, upload de imagem, grids que apenas exibem dados, banners fixos, botões que só navegam, badges que exibem valores computados).
  - **Dinâmico**: após apresentado, permite interações que mudam seu próprio conteúdo/estado ou o de outros elementos da tela (date pickers com navegação de calendário, dropdowns que mostram/escondem seções, filtros que recarregam grids, abas que trocam painéis, campos dependentes que recalculam outros, contadores que atualizam em tempo real, seções condicionais).
- O contexto: **existente** (a story referencia explicitamente uma tela, formulário ou módulo já existente) ou **novo** (introduz capacidade ou tela inédita). Palavras-sinal de existente: "adicionar ao existente", "atualizar o atual", "modificar a tela/formulário/módulo". Sinais de novo: "criar nova", "construir", "introduzir", "implementar nova tela/fluxo". Na dúvida, o avaliador assume contexto novo.

## O que torna a escrita fraca

- Misturar trabalho de backend (endpoints, queries, modelos de dados, integrações, mappers) com a descrição de UI — backend não conta aqui, mas polui a leitura.
- Não deixar claro se a tela/formulário já existe ou está sendo criado — a ambiguidade faz o avaliador assumir contexto novo.
- Descrever elementos interativos como se fossem estáticos ("campo de data") sem dizer que abre um calendário navegável, ou que um dropdown atualiza outro campo.
- Listar o mesmo componente várias vezes ("tooltip no card A, tooltip no card B") em vez de declarar um tipo de componente reutilizado.
- Título de "Spike", "POC" ou "Research" sem descrição — se a descrição contém elementos de UI, eles contam; sem descrição, nada pode ser avaliado.

## O que deixar explícito

- Cada elemento de UI distinto, com nome reconhecível (campo X, botão Y, modal Z).
- Se a tela ou formulário já existe no sistema ou está sendo criado do zero — use palavras-sinal explícitas.
- O comportamento de cada elemento interativo: o que acontece quando o usuário interage (abre overlay? recarrega grid? habilita/desabilita botão? atualiza outro campo?).
- Mensagens de erro e sucesso — são elementos contáveis.
- Quando um componente é reutilizado em vários lugares, diga isso ("o mesmo tooltip se aplica a todos os cards").

## Exemplos de escrita

### ❌ Fraca
> Melhorar o formulário de cadastro de funcionário adicionando data de admissão e localização.

### ✅ Bem escrita
> No formulário de cadastro de funcionário já existente, adicionar:
> - Campo de data de admissão com date picker que abre um calendário navegável entre meses e anos.
> - Dropdown de País que, ao ser selecionado, atualiza as opções do dropdown de Estado.
> - Dropdown de Estado que, ao ser selecionado, atualiza as opções do dropdown de Cidade.

### ❌ Fraca
> Criar tela de erro.

### ✅ Bem escrita
> Criar uma nova tela de reporte de erros onde o usuário pode visualizar e enviar relatos de bugs:
> - Lista de relatos já enviados (apenas exibição).
> - Área de texto para descrever o erro.
> - Botão de envio.
> - Mensagem de erro exibida ao tentar enviar com a descrição vazia.

## Perguntas típicas para o questionário

- Essa tela/formulário já existe no sistema ou está sendo criado do zero?
- Quais elementos o usuário vê ou com que interage? Consegue enumerar um a um?
- Algum desses elementos muda de conteúdo ou estado depois de exibido, ou muda outros elementos da tela? Qual comportamento exatamente?
- Esse componente aparece em vários lugares? É o mesmo tipo de componente reutilizado?
- Há mensagens de erro, sucesso ou validação? Elas também contam como elementos.
