
# D12 · Security & Compliance

Esta dimensão mede os requisitos **explícitos** de segurança e conformidade: autenticação,
autorização, criptografia, proteção de dados, trilhas de auditoria de segurança e frameworks
de compliance (LGPD, GDPR, PCI-DSS, HIPAA, SOX). Só conta o que está declarado como
requisito — menção casual não é requisito.

## O que o avaliador procura

- Requisitos de autenticação e autorização declarados: login, MFA, OAuth, SSO, RBAC, ABAC
- Frameworks de compliance citados nominalmente, com o escopo do que é exigido
  (ex.: "LGPD — consentimento e portabilidade de dados")
- Mandatos de criptografia: em repouso, em trânsito, campos sensíveis específicos
- Necessidade de trilha de auditoria de segurança (quem acessou o quê, quando)
- Palavras-chave bilíngues que o avaliador reconhece: "authentication/autenticação",
  "authorization/autorização", "encryption/criptografia", "RBAC", "audit/auditoria",
  "LGPD", "GDPR", "PCI-DSS"

## O que torna a escrita fraca

- Não dizer se a funcionalidade exige autenticação — a diferença entre "nenhum requisito de
  segurança" e "requisito básico de autenticação" muda completamente a avaliação
- Mencionar compliance sem escopo: "precisa estar em conformidade com LGPD" sem dizer o que
  é exigido (consentimento? portabilidade? direito ao esquecimento?) deixa a exigência
  indeterminada
- Confundir regra de negócio funcional com controle de acesso: "usuários veem apenas seus
  próprios dados" é regra funcional, a menos que a story referencie explicitamente
  autorização/controle de acesso
- Classificar na dimensão errada: tempo de resposta na autenticação é Quality Attributes
  (D11); o requisito de autenticação em si é Security & Compliance

## O que deixar explícito

- **Se há ou não requisito de segurança** — inclusive quando não há: "sem dados sensíveis,
  acesso interno com login padrão" é uma declaração útil
- **O nível de controle exigido**: autenticação básica, gestão de sessão, MFA, OAuth/SSO
- **O framework de compliance nominal e o escopo**: qual regulação se aplica e quais
  obrigações dela a story precisa atender
- **O que é criptografado**: campos sensíveis específicos, dados em repouso, tráfego
- **Trilha de auditoria de segurança**: se é preciso registrar acessos e ações para
  prestação de contas

## Exemplos de escrita

### ❌ Fraca
> O sistema guarda dados de clientes e precisa ser seguro.

### ✅ Bem escrita
> O sistema armazena dados pessoais de clientes (nome, CPF, endereço) e deve atender à LGPD:
> consentimento explícito no cadastro e portabilidade dos dados mediante solicitação.
> Campos sensíveis (CPF) criptografados em repouso. Acesso à consulta restrito a usuários
> autenticados com perfil de atendente.

## Perguntas típicas para o questionário

- A funcionalidade exige autenticação? De que tipo (login simples, MFA, SSO/OAuth)?
- Há diferenciação de acesso por perfil envolvendo controle de autorização explícito?
- A story lida com dados pessoais ou sensíveis? Algum framework de compliance se aplica
  (LGPD, GDPR, PCI-DSS, HIPAA, SOX)? Quais obrigações específicas?
- Há exigência de criptografia? Sobre quais dados — em repouso, em trânsito?
- É preciso registrar trilha de quem acessou ou alterou dados para fins de auditoria?
