
# D4 · Roles & Permissions

Esta dimensão mede a profundidade da estrutura de papéis e permissões que precisa ser compreendida para implementar a story: quantos níveis (eixos) de diferenciação de permissão precisam ser analisados — não quantos papéis existem.

## O que o avaliador procura

- Toda story funcional tem pelo menos um contexto de permissão implícito, mesmo quando todos os usuários têm o mesmo acesso — a dimensão está sempre presente.
- Apenas papéis e permissões explicitamente declarados na story; o avaliador não infere hierarquia ou permissões não descritas.
- O número de níveis (eixos) de diferenciação, como na criação de personagem de um jogo de tabuleiro: raça (Orc, Humano, Elfo) é um eixo; classe de batalha (Mago, Guerreiro, Arqueiro) é outro eixo. Uma habilidade que exige verificar dois eixos ("apenas Paladinos Elfos") é mais profunda que uma que exige um só ("apenas Magos").
- Quantidade de papéis não é profundidade: três papéis (Pesquisador, Revisor, Admin) distinguidos por um único eixo (qual papel o usuário tem) formam um nível só.
- Autenticação sem diferenciação de papéis ("todo usuário autenticado pode") é o caso base — nenhum eixo de diferenciação a analisar.
- Em evoluções de funcionalidades existentes, apenas a diferenciação NOVA introduzida pela mudança conta: herdar uma restrição já existente não adiciona nível.
- Na ambiguidade sobre quantos níveis existem, o avaliador assume o menor nível.

## O que torna a escrita fraca

- Não mencionar papéis quando a permissão importa: "o usuário pode aprovar transações" — qual usuário? Se só alguns podem, o papel precisa estar escrito.
- Listar muitos papéis sem dizer o que os distingue: o avaliador pode interpretar como um único eixo ou como vários — e na dúvida assume o menor, o que pode subavaliar uma estrutura realmente multi-eixo.
- Em evoluções, não deixar claro se a restrição citada já existe no sistema ou está sendo introduzida agora — herdar restrição existente não adiciona diferenciação.
- Confiar que a hierarquia é óbvia: o avaliador pontua apenas o que está explícito, nunca o que "todo mundo sabe".

## O que deixar explícito

- Quais papéis ou perfis de usuário participam da story, nomeados.
- O que cada papel pode ou não pode fazer, quando houver diferença entre eles.
- Cada eixo de diferenciação quando houver mais de um: tipo de papel E senioridade, E departamento, E região — cada "E" é um nível a declarar.
- Em evoluções: se a funcionalidade herda uma restrição de permissão que já existe ou se cria uma restrição nova.
- Se todos os usuários têm exatamente as mesmas permissões, diga isso ("qualquer usuário autenticado") — é uma informação válida e fecha a dimensão.

## Exemplos de escrita

### ❌ Fraca
> Usuários podem gerenciar artigos no sistema.

### ✅ Bem escrita
> Administradores podem criar, editar e excluir artigos. Usuários comuns podem apenas visualizar artigos.

### ❌ Fraca
> Adicionar a habilidade de escapar de masmorras para personagens apropriados.

### ✅ Bem escrita
> Adicionar a habilidade de escapar de masmorras para personagens que já possuem a habilidade de conjurar magias — restrição de classe já existente no sistema, que esta nova habilidade apenas herda.

### ❌ Fraca
> Aprovação de transações de alto risco será restrita.

### ✅ Bem escrita
> Apenas revisores sêniores do departamento de compliance podem aprovar transações de alto risco — a permissão exige cruzar dois eixos: senioridade do revisor e departamento.

## Perguntas típicas para o questionário

- Quem pode executar a ação desta story? Todos os usuários ou apenas alguns?
- Quais papéis estão envolvidos e o que diferencia o que cada um pode fazer?
- Para determinar se alguém tem permissão, quantos eixos independentes precisam ser verificados (papel? senioridade? departamento? região)?
- Se a story é uma evolução: a restrição de permissão citada já existe no sistema ou está sendo criada agora?
- Todos os usuários autenticados têm exatamente o mesmo acesso nesta funcionalidade?
