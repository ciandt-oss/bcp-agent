
# D7 · New Domain Entities

Esta dimensão mede a novidade que a story introduz no modelo de domínio: conceitos que o software nunca tratou antes e conceitos existentes que ganham novos atributos ou novas relações. Ela é ortogonal a D6 — D6 conta quantas entidades a story usa; D7 mede se há novidade no modelo.

## O que o avaliador procura

O avaliador separa as entidades da story em dois grupos, e cada entidade pertence a exatamente um deles:

- **Entidades existentes modificadas:** conceitos que já existem no modelo de domínio e recebem novos atributos ou novas relações nesta story. Não importa quantos atributos novos uma entidade ganha — o que conta é o número de entidades afetadas.
- **Entidades genuinamente novas:** conceitos que aparecem pela primeira vez no software — o domínio nunca lidou com eles antes.

Peso relativo: uma entidade nova no domínio pesa muito mais que modificações em entidades existentes, e os dois grupos são sempre registrados juntos — nunca se fica só com o mais "alto". Uma story com entidades modificadas E novas declara as duas coisas.

O que o avaliador descarta:

- CRUD sobre entidades existentes (criar, atualizar, excluir registros) sem novos atributos ou relações — isso é uso do modelo, não novidade; pertence apenas a D6.
- Paginação, ordenação, filtro e índice — são comportamento de consulta/interface, não mudança de estrutura de dados.
- Termos de infraestrutura técnica (cache, fila, API) — não são entidades.

## O que torna a escrita fraca

- Não deixar claro se uma entidade já existe no sistema ou está sendo introduzida agora — "adicionar Review aos artigos" é ambíguo; "introduzir a entidade Review, nova no domínio" não é.
- Confundir CRUD com novidade: "criar um artigo" quando Article já existe não introduz nada ao modelo.
- Misturar mudanças de consulta (paginar, ordenar, filtrar, indexar) com mudança de estrutura de dados.
- Escrever "atualizar perfil do usuário com novos campos" sem dizer que User já existe e está apenas ganhando atributos — a ambiguidade pode inflar a leitura para "entidade nova".
- Quando há os dois tipos de mudança, mencionar apenas a entidade nova e omitir as existentes que ganham relações com ela (ou vice-versa) — os dois blocos precisam aparecer.
- Assumir que o avaliador conhece o modelo atual. Ele só sabe o que a story declara: se não está escrito que Customer e Product já existem, a classificação fica instável.

## O que deixar explícito

- Para cada entidade citada, declare se ela já existe no domínio ou é nova.
- Para entidades existentes modificadas, declare o que muda: quais novos atributos ou quais novas relações.
- Para entidades novas, declare que o conceito é inédito no software e qual é seu papel no domínio.
- Quando houver os dois casos na mesma story, liste os dois grupos separadamente e completos.
- Não declare como novidade o que é apenas operação sobre registros (CRUD) ou comportamento de consulta (paginação, filtro, ordenação, índice).

## Exemplos de escrita

### ❌ Fraca
> "Criar gestão de pedidos com clientes e produtos."

### ✅ Bem escrita
> "Criar gestão de pedidos. Order é uma entidade nova no domínio. Customer e Product, que já existem no sistema, passam a se relacionar com Order."

### ❌ Fraca
> "Adicionar paginação na lista de artigos e permitir criar artigos novos."

### ✅ Bem escrita
> "Adicionar os atributos data de cancelamento e motivo de cancelamento à entidade Order, que já existe no domínio." (paginação e CRUD não são novidade de modelo — não pertencem a esta dimensão)

## Perguntas típicas para o questionário

- As entidades citadas já existem no sistema hoje, ou alguma está sendo introduzida pela primeira vez?
- Para as entidades existentes: há novos atributos ou novas relações sendo criados, ou é apenas CRUD sobre registros?
- Há mudança real de estrutura de dados, ou o descrito é paginação, ordenação, filtro ou índice?
- Existe uma entidade nova que obriga entidades existentes a ganhar relações com ela? Quais?
