
# D5 · Solution Variabilities

Esta dimensão mede os caminhos comportamentais distintos declarados na story que convergem para o mesmo resultado final — olhando apenas o output, não dá para dizer qual caminho foi percorrido. Variações de papéis/permissões e de filtros de interface não pertencem aqui: pertencem às dimensões próprias delas.

## O que o avaliador procura

- Apenas variabilidades explicitamente declaradas na story — nada é inferido.
- Um ponto de decisão dentro de uma regra de negócio que leva a caminhos distintos que convergem ao mesmo output. Exemplo-âncora: os quatro tipos de chave PIX (CPF, e-mail, telefone, UUID) têm validações e mensagens de erro distintas, mas o resultado final é sempre o mesmo — "chave validada, dados do destinatário exibidos". O tipo da chave é invisível no resultado.
- O teste do output indistinguível: se os caminhos produzem resultados finalmente diferentes (usuário Free recebe relatório resumido; Premium recebe relatório detalhado com gráficos), NÃO é variabilidade — os outputs são distinguíveis.
- O "output" é o resultado de negócio final entregue ao usuário quando a operação conclui com sucesso — não estados intermediários, mensagens de erro, feedback de validação ou passos de processamento.
- Exclusões obrigatórias, verificadas para cada candidata:
  - Variação por papel/perfil de usuário (controle de acesso) → pertence a Roles & Permissions.
  - Variação de filtros ou opções de interface (seletores de período, toggles de visualização, ordenação) → pertence a Interface Elements.
  - Tipos de usuário diferentes sem variação comportamental explícita → Roles & Permissions.
- Quando há variabilidade legítima, a semelhança entre os caminhos: se os caminhos têm quantidade e características de passos parecidas (mesma estrutura, pequenas variações — como fórmulas diferentes para calcular área de salas de formatos diferentes), é uma complexidade moderada; se os caminhos divergem significativamente (passos em quantidade diferente, mecanismos diferentes — aprovação automática vs. manual com trilha de auditoria), é uma complexidade alta.
- Com múltiplas variabilidades, conta a mais complexa — não se somam.

## O que torna a escrita fraca

- Declarar variação de forma vaga: "o sistema suporta múltiplas configurações" — sem listar quais, não há ponto de decisão identificável.
- Misturar variação de permissão com variação de solução: "campos obrigatórios dependem do perfil do usuário" é Roles & Permissions, não variabilidade — escrevê-la aqui gera ruído.
- Não deixar claro se os caminhos convergem ao mesmo resultado: se a story não diz qual é o output final de cada caminho, o avaliador não consegue aplicar o teste do output indistinguível.
- Mencionar variações futuras ou hipotéticas ("poderá variar por país") — só conta o que está explicitamente declarado agora.
- Não descrever o quanto os caminhos divergem: sem os passos de cada caminho, não há como distinguir caminhos semelhantes de caminhos radicalmente diferentes.

## O que deixar explícito

- O ponto de decisão: qual parâmetro ou condição faz o comportamento variar (tipo de chave, formato da sala, tenant).
- Cada caminho distinto, com seus passos ou regras específicas.
- O output final comum a todos os caminhos — a frase que prova a convergência ("todos retornam a área em m²", "o resultado é sempre a chave validada").
- O quanto os caminhos se assemelham ou divergem: número de passos, mecanismos usados, etapas exclusivas de cada caminho.
- Se houver variações por perfil ou por filtro de tela, escrevê-las como o que são (permissões, elementos de interface) — não como variabilidades de solução.

## Exemplos de escrita

### ❌ Fraca
> O sistema valida a chave PIX informada pelo usuário.

### ✅ Bem escrita
> O sistema valida a chave PIX informada conforme seu tipo: CPF exige validação de dígitos verificadores; e-mail exige validação de formato; telefone exige DDD e nono dígito; chave aleatória exige formato UUID. Em todos os casos, o resultado é o mesmo: chave validada e dados do destinatário exibidos na tela.

### ❌ Fraca
> O comportamento do sistema muda conforme o cliente.

### ✅ Bem escrita
> O processamento de solicitações varia por tenant: o tenant A usa um fluxo de aprovação em 4 etapas com notificações por e-mail; o tenant B aprova imediatamente sem notificações; o tenant C exige aprovação manual com trilha de auditoria separada. Para todos, o resultado final é "solicitação processada" — o fluxo usado é invisível no output.

### ❌ Fraca
> O dashboard pode exibir mês, trimestre ou ano.

### ✅ Bem escrita (reescrita como elemento de interface, não como variabilidade)
> O dashboard tem um seletor de período com as opções mês, trimestre e ano, que recarrega o grid de resultados conforme a seleção.

## Perguntas típicas para o questionário

- Existe algum ponto na regra de negócio em que o comportamento varia conforme uma condição ou parâmetro? Qual parâmetro?
- Quais são os caminhos distintos a partir desse ponto? Quais os passos de cada um?
- Todos os caminhos terminam no mesmo resultado final, ou os resultados são visivelmente diferentes entre si?
- Essa variação é por perfil de usuário ou por filtro/opção de tela? (Se sim, ela pertence a outra dimensão.)
- Os caminhos têm passos parecidos em quantidade e tipo, ou divergem significativamente?
