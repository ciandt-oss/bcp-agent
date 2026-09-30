
# D11 · Quality Attributes

Esta dimensão mede os requisitos de qualidade **explícitos** da story: performance, tempo de
resposta, throughput, latência, escalabilidade, uptime/SLA, confiabilidade e disponibilidade.
Só conta o que está declarado como requisito — nunca o que é detalhe de implementação.

## O que o avaliador procura

- Requisitos de qualidade declarados com **limiar mensurável**: tempo de resposta máximo,
  percentual de uptime, volume de transações por minuto, retenção de logs
- Menções vagas sem limiar ("carregar rápido", "ser confiável") são registradas, mas com
  peso mínimo — a exigência não está definida
- Quão exigentes são os limiares declarados: expectativa padrão de sistema interno é uma
  coisa; missão crítica com resposta abaixo de 100ms e disponibilidade multi-região é outra
- A exigência vem declarada na story — o avaliador não infere requisito de qualidade a
  partir do comportamento funcional nem de escolhas de implementação

## O que torna a escrita fraca

- Mencionar qualidade sem limiar: "o sistema deve ser rápido", "deve suportar a carga
  esperada", "tem que ser confiável"
- Misturar implementação com requisito: "vamos usar Redis para cache de sessão" descreve
  uma decisão técnica, não um requisito de qualidade — se a intenção é exigir performance,
  declare o alvo ("lista de produtos carrega em menos de 1 segundo")
- Deixar no ar se a exigência é obrigatória ou desejável: SLA é compromisso, não aspiração
- Declarar o requisito na dimensão errada: criptografia e autenticação pertencem a
  Security & Compliance (D12) mesmo quando têm custo de performance; WCAG e responsividade
  pertencem a UX & Accessibility (D13), não a Quality Attributes

## O que deixar explícito

- **Qual qualidade** está sendo exigida: tempo de resposta, throughput, disponibilidade,
  escalabilidade, retenção
- **O limiar mensurável**: "menos de 1s", "99,9% de uptime", "mil transações por minuto"
- **O contexto de exigência**: sistema interno com expectativa padrão vs. plataforma pública
  com SLA contratual vs. operação crítica em tempo real
- Se caching, replicação ou auto-scaling são **requisitos** (e não decisões de implementação),
  escreva-os como requisitos com o objetivo de qualidade que atendem

## Exemplos de escrita

### ❌ Fraca
> A tela de relatórios tem que abrir rápido porque os usuários reclamam de lentidão.

### ✅ Bem escrita
> A tela de relatórios deve carregar em menos de 1 segundo para o volume atual de dados
> (até 50 mil registros). O sistema deve manter disponibilidade de 99,9% em horário
> comercial.

## Perguntas típicas para o questionário

- Há algum requisito explícito de tempo de resposta, throughput ou latência? Qual o limiar?
- Existe compromisso de disponibilidade ou SLA (ex.: 99,9% de uptime)?
- A story exige escalabilidade (ex.: auto-scaling por carga) como requisito, ou é apenas
  uma decisão de implementação?
- Caching, replicação ou failover são exigências da story ou escolhas técnicas da equipe?
- A exigência de qualidade é obrigatória (contratual/SLA) ou uma expectativa interna?
