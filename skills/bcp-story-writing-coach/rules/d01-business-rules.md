
# D1 · Business Rules

Esta dimensão mede a complexidade lógica de cada regra de negócio declarada na story: quantas decisões ela precisa tomar, de quantas fontes de dados depende e em quantos contextos diferentes precisa funcionar. A avaliação é sobre a lógica da decisão, não sobre detalhes de implementação.

## O que o avaliador procura

- Cada regra lógica identificável na story, avaliada como um todo (não sub-passos isolados).
- Quantidade de condições que a regra precisa verificar.
- Níveis de aninhamento da lógica: sub-itens numerados (1.1, 1.2, 1.3) contam como passos aninhados da mesma regra; bullets ou travessões independentes são tratados como regras separadas, avaliadas uma a uma.
- Quantidade de fontes de dados distintas que a regra consulta.
- Se a regra envolve cálculo em múltiplas etapas ou validação que cruza dados de fontes diferentes.
- Se a regra envolve processamento em tempo real ou ramificação que depende do estado do sistema.
- O contexto em que a regra opera: a mesma regra validando contra um único sistema é mais simples do que validando contra vários sistemas ou atravessando múltiplos atores e estados.

## O que torna a escrita fraca

- Escrever a regra como uma frase única genérica ("validar o endereço") quando ela na verdade tem várias sub-etapas — o avaliador não tem como contar condições que não foram declaradas.
- Misturar passos dependentes e independentes na mesma estrutura: se os passos fazem parte de uma única decisão, escreva-os como sub-itens numerados; se são regras independentes, separe-as em itens distintos.
- Omitir de onde vêm os dados: "calcular o prêmio" sem dizer que consulta APIs externas, tabelas de tarifa e histórico do cliente esconde fontes de dados que definem a complexidade.
- Não deixar claro quando a regra depende de dados em tempo real ou de estado do sistema (ex.: histórico de sinistros atualizado no momento).
- Ambiguidade entre dois níveis de complexidade: na dúvida, o avaliador tende ao nível mais baixo — a menos que a regra tenha sub-passos aninhados explícitos, o que puxa para o mais alto.

## O que deixar explícito

- Cada condição que a regra verifica, enumerada de forma contável.
- Sub-passos de uma decisão composta como sub-itens numerados (1.1, 1.2, ...) dentro da regra-mãe.
- Todas as fontes de dados envolvidas: bancos internos, APIs externas, tabelas de referência, sistemas legados.
- Quando houver cálculo, as etapas dele (ex.: primeiro avaliar perfil de risco, depois aplicar tabela, depois ajustar por histórico).
- Quando a regra cruza contextos: múltiplos atores, múltiplos sistemas de validação, estados diferentes da aplicação.

## Exemplos de escrita

### ❌ Fraca
> O sistema deve validar o endereço de entrega antes de confirmar o pedido.

### ✅ Bem escrita
> O sistema deve validar o endereço de entrega antes de confirmar o pedido:
> 1.1 Verificar se o formato do CEP é válido.
> 1.2 Confirmar que a cidade informada corresponde ao estado do CEP.
> 1.3 Consultar a tabela de zonas de entrega para verificar se o endereço está em área atendida.

### ❌ Fraca
> Calcular o valor do seguro do cliente.

### ✅ Bem escrita
> Calcular o prêmio do seguro:
> 1.1 Avaliar o perfil de risco do condutor consultando as 3 APIs externas de histórico.
> 1.2 Aplicar a tabela de tarifas específica do estado do cliente.
> 1.3 Ajustar o valor conforme o histórico de sinistros em tempo real.
> 1.4 Aplicar as regras de desconto corporativo.

## Perguntas típicas para o questionário

- Quantas condições essa regra verifica? Consegue enumerá-las?
- Esses passos são sub-etapas de uma única decisão ou regras independentes? (Isso muda como devem ser escritos.)
- De quantas fontes de dados essa regra precisa? Quais são elas?
- Existe algum cálculo em etapas ou validação que cruza dados de fontes diferentes?
- Essa regra depende de dados em tempo real ou do estado atual do sistema?
