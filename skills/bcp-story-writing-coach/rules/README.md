# Regras pedagógicas das 13 dimensões BCP

Um arquivo por dimensão — 10 funcionais (D1–D10) e 3 não-funcionais (D11–D13).
Cada arquivo responde, em formato pedagógico:

- **O que o avaliador procura** — o que a dimensão mede
- **O que torna a escrita fraca** — os erros que geram instabilidade ou subavaliação
- **O que deixar explícito** — o que a story precisa declarar para ser bem avaliada
- **Exemplos de escrita** — fraca vs. bem escrita
- **Perguntas típicas para o questionário** — lacunas recorrentes desta dimensão

## Regras globais (valem para todos os arquivos)

1. **Sem tiers, sem números.** Nenhum arquivo expõe classificações de tamanho (XS, S, M, L,
   XL) nem valores numéricos de scoring. As regras são explicadas em termos de escrita:
   "quantas condições a regra tem", não "quantos pontos ela vale".
2. **Sem invenção.** As regras ensinam a *explicitar* o que existe, nunca a *adicionar*
   requisitos que a story não tem.
3. **Dimensões ortogonais.** Cada requisito pertence a exatamente uma dimensão. Quando houver
   ambiguidade de classificação (ex.: performance vs. UX, segurança vs. regra funcional), o
   arquivo da dimensão indica a fronteira.
4. **Só o explícito conta.** O avaliador BCP pontua apenas o que está declarado na story.
   Informação implícita não dedutível é tratada como ausente — daí a importância de
   explicitar.

## Índice

| Arquivo | Dimensão | Tema em uma frase |
|---------|----------|-------------------|
| `d01-business-rules.md` | D1 · Business Rules | Condições, aninhamento e fontes de dados de cada regra |
| `d02-interface-elements.md` | D2 · Interface Elements | Elementos visuais distintos, estáticos vs. dinâmicos, contexto novo vs. existente |
| `d03-boundaries.md` | D3 · Boundaries | Sistemas externos e dispositivos; natureza perene vs. volátil do dado trocado |
| `d04-roles-permissions.md` | D4 · Roles & Permissions | Níveis (eixos) de diferenciação de permissão — não a quantidade de papéis |
| `d05-solution-variabilities.md` | D5 · Solution Variabilities | Caminhos distintos que convergem ao mesmo resultado indistinguível |
| `d06-domain-entities.md` | D6 · Domain Entities | Entidades de negócio distintas manipuladas pela story |
| `d07-new-domain-entities.md` | D7 · New Domain Entities | Novidade no modelo: entidades novas vs. entidades existentes com novos atributos/relações |
| `d08-background-processes.md` | D8 · Background Processes | Como o processo é disparado (agenda, evento, externo, manual) |
| `d09-notifications.md` | D9 · Notifications | Eventos de negócio distintos que disparam mensagens a pessoas |
| `d10-audits.md` | D10 · Audits | Entidades que exigem trilha de quem fez o quê e quando |
| `d11-quality-attributes.md` | D11 · Quality Attributes | Requisitos explícitos de performance, SLA, escalabilidade com limiares |
| `d12-security-compliance.md` | D12 · Security & Compliance | Autenticação, autorização, criptografia, frameworks de compliance |
| `d13-ux-accessibility.md` | D13 · UX & Accessibility | Padrões de acessibilidade, responsividade, internacionalização |
