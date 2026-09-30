
# D6 · Domain Entities

Esta dimensão mede quantas entidades de negócio distintas a story manipula — conceitos, pessoas ou objetos do domínio que têm características próprias e se relacionam entre si. A complexidade cresce com o número de conceitos de negócio diferentes que a story precisa declarar.

## O que o avaliador procura

- Termos de negócio nomeados explicitamente na story — palavras que o negócio reconhece e usa em discussões de requisitos (Order, Customer, Article, Doctor).
- Termos que têm atributos ou estados próprios (nome, status, valor, data; pendente, aprovado, cancelado).
- Termos que sofrem ações na story: são criados, modificados, excluídos, consultados ou mudam de estado.
- Termos que se relacionam com outros conceitos de negócio (um médico solicita um exame para um paciente).
- Deduplicação por conceito: sinônimos, apelidos e traduções contam uma única vez (Customer ≡ Client ≡ Buyer é uma só entidade).
- Em agregados, filhos nomeados como conceitos separados contam individualmente: "Order contém OrderItems" são duas entidades; uma entidade apenas referenciada (Product em "OrderItem referencia Product") também conta quando é um conceito de primeira classe com identidade própria.
- Em evoluções (mudança sobre sistema existente), o avaliador isola a mudança e considera apenas as entidades diretamente impactadas — com uma exceção: quando uma regra de negócio é impactada, entram TODAS as entidades envolvidas nessa regra.
- Escopo do fluxo: contam apenas as entidades do domínio do fluxo descrito na story, não do sistema inteiro.

## O que torna a escrita fraca

- Misturar termos de infraestrutura técnica (cache, fila, database, API, microservice, handler, mapper, DTO, controller) com conceitos de negócio — eles não têm semântica de negócio e não são entidades.
- Tratar enumerações e listas de status (OrderStatus, Priority, Category) como se fossem entidades — não são.
- Tratar atributos como entidades: "email do usuário", "status do artigo", "data de criação" são características de User e Article, não conceitos independentes.
- Mencionar o mesmo conceito por vários nomes (Customer, Client, Buyer) sem deixar claro que são sinônimos, gerando contagem instável.
- Nomear campos embutidos como se fossem entidades sem descrever operações sobre eles: "User com campos de endereço (rua, cidade, CEP)" descreve atributos de User; já "Address consultado e atualizado de forma independente, vinculado a vários Users" descreve uma entidade — o que decide não é o nome, são as operações e o significado de negócio.
- Em evoluções, listar todas as entidades do contexto ao redor ("o checkout usa Customer, PaymentMethod, Cart...") quando a mudança impacta apenas uma — ou, ao contrário, omitir entidades de uma regra de negócio afetada.
- Descrever entidades implícitas na ação sem nomeá-las — toda story funcional envolve pelo menos uma entidade, e se o avaliador não a identifica, a avaliação fica instável.

## O que deixar explícito

- O nome de cada entidade de negócio que a story cria, modifica, exclui, consulta ou cuja situação muda.
- Qual é o nome canônico de cada conceito, indicando sinônimos quando existirem ("Customer, também chamado de Client").
- Quando um agregado tiver filhos operados separadamente, nomeie-os como conceitos próprios (Order e OrderItem, não apenas "pedido com itens").
- Em evoluções, delimite a mudança: quais entidades são diretamente impactadas e, se uma regra de negócio é afetada, quais entidades participam dela. Exemplo de escopo estreito: "alterar o endereço de entrega no checkout" impacta apenas Order — Customer, PaymentMethod e Cart ficam de fora. Exemplo de expansão por regra: "desconto passa a variar por nível de fidelidade" envolve Customer, Order, Discount e LoyaltyTier.
- Delimite o domínio do fluxo: em "concluir o pagamento do carrinho", o fluxo de pagamento envolve Customer, Order e PaymentMethod; Cart, CartItem e Product são contexto de outro domínio.

## Exemplos de escrita

### ❌ Fraca
> "Atualizar os dados do cadastro, incluindo e-mail, status e endereço, e salvar no banco PostgreSQL via API."

### ✅ Bem escrita
> "Como Customer (também chamado de Client na área comercial), quero atualizar meu e-mail e meu Address — entidade própria, com rua, cidade e CEP, consultável e editável de forma independente — mantendo o histórico do status do cadastro."

## Perguntas típicas para o questionário

- Quais conceitos de negócio essa story cria, modifica, exclui ou consulta? Liste-os pelo nome.
- Algum desses nomes é sinônimo de outro (Customer/Client/Buyer)? Qual é o nome canônico?
- Os termos técnicos citados (fila, cache, API, DTO) representam conceitos de negócio ou só infraestrutura?
- Há filhos de agregado operados separadamente (OrderItem dentro de Order, Address vinculado a User)? Eles têm identidade e operações próprias na story?
- Se for uma evolução: qual é exatamente a mudança e quais entidades ela impacta — incluindo todas as envolvidas em alguma regra de negócio afetada?
