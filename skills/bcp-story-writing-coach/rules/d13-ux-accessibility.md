
# D13 · UX & Accessibility

Esta dimensão mede os requisitos **explícitos** de experiência do usuário e acessibilidade:
padrões de acessibilidade (WCAG), navegação por teclado, leitores de tela, design
responsivo/adaptativo, internacionalização (i18n) e padrões de UX declarados. Só conta o que
está declarado como requisito — elemento visual descrito funcionalmente não é requisito de UX.

## O que o avaliador procura

- Padrões de acessibilidade citados nominalmente com nível: "WCAG 2.1 nível AA"
- Requisitos de navegação por teclado, suporte a leitor de tela, HTML semântico, textos
  alternativos
- Mandatos de design responsivo/adaptativo: "funcionar em desktop e mobile"
- Necessidades de internacionalização: quantos idiomas, suporte a RTL (right-to-left)
- Palavras-chave bilíngues que o avaliador reconhece: "WCAG", "accessibility/acessibilidade",
  "responsive/responsivo", "screen reader/leitor de tela", "keyboard navigation/navegação
  por teclado", "i18n"

## O que torna a escrita fraca

- Descrever elementos de interface ("o dashboard exibe gráficos") sem declarar nenhum
  requisito de experiência — elemento de UI é Interface Elements (D2), não UX & Accessibility
- Mencionar acessibilidade genericamente: "a tela deve ser acessível" sem padrão, nível ou
  comportamento concreto deixa a exigência indeterminada
- Não declarar responsividade quando ela é esperada: se a story vale para mobile e desktop,
  escreva — o avaliador não presume
- Confundir performance com UX: "a página carrega em menos de 2 segundos" é Quality
  Attributes (D11), não UX & Accessibility

## O que deixar explícito

- **O padrão e o nível de acessibilidade** exigidos (ex.: WCAG 2.1 nível AA), ou declare
  que não há requisito de acessibilidade
- **Os dispositivos alvo**: apenas desktop, responsivo desktop+mobile, app nativo
- **Os comportamentos de acessibilidade concretos**: navegação por teclado, atalhos,
  compatibilidade com leitor de tela, HTML semântico, textos alternativos em imagens
- **Os idiomas suportados** e a necessidade de suporte a RTL, quando houver
- Requisitos de UX pattern específicos: PWA, onboarding guiado, personalização

## Exemplos de escrita

### ❌ Fraca
> A nova tela de consulta deve ser bonita e funcionar bem em qualquer lugar.

### ✅ Bem escrita
> A nova tela de consulta é responsiva (desktop e mobile) e deve atender a WCAG 2.1 nível A:
> navegação completa por teclado e textos alternativos em todas as imagens. Suporte a
> português e inglês, com seleção de idioma no perfil do usuário.

## Perguntas típicas para o questionário

- Há requisito de acessibilidade? Qual padrão e nível (ex.: WCAG 2.1 A, AA)?
- A funcionalidade precisa ser responsiva ou adaptativa? Para quais dispositivos?
- Navegação por teclado ou suporte a leitor de tela são exigências?
- A story envolve mais de um idioma (i18n)? Quantos? Há suporte a RTL?
- Existe algum padrão de UX mandatório (PWA, design system específico, personalização)?
