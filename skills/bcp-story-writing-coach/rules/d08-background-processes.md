
# D8 · Background Processes

Esta dimensão mede processos que rodam fora do fluxo principal do usuário — tarefas assíncronas, agendadas ou disparadas por eventos. O único fator que importa é COMO o processo é disparado; a complexidade interna dele (passos, validações, volume de dados) pertence a D1 · Business Rules.

## O que o avaliador procura

O avaliador identifica o gatilho do processo, numa hierarquia de complexidade crescente:

1. **Disparado por evento:** o processo é disparado por um evento do sistema (pedido aprovado, usuário registrado) ou externo (webhook, callback de gateway de pagamento) e continua DEPOIS que a resposta imediata ao usuário já foi entregue — o usuário não espera por ele.
2. **Agendado:** disparado exclusivamente por tempo (diário, semanal, mensal), sem disparo manual descrito.
3. **Agendado + disparo manual:** tem agenda E a story declara explicitamente que também pode ser disparado manualmente sob demanda ("roda toda noite, mas o operador pode disparar a qualquer momento").
4. **Totalmente externo/independente:** roda completamente fora da aplicação, sem depender de nenhum gatilho dela — a aplicação apenas reage ao resultado (ex.: um parceiro envia um arquivo diário via SFTP e o sistema o processa quando detectado).

O que NÃO é background process:

- Operações síncronas que respondem imediatamente e bloqueiam o usuário enquanto executam — fazem parte do fluxo principal.
- Uma fila mencionada sozinha, sem um worker assíncrono que a consuma descrito na story.
- Spikes, investigações ou menções genéricas a "batch", "fila" ou "processo" sem um processo assíncrono ou agendado efetivamente descrito.

Regras de borda:

- **Múltiplos processos:** conta o gatilho mais complexo — os gatilhos não se somam.
- **Evoluções:** se a story muda apenas a lógica interna de um processo existente (nova validação, novo passo, dados diferentes) e o gatilho continua o mesmo, a dimensão não se aplica à mudança — a alteração pertence a D1. Só se aplica quando o mecanismo de disparo muda (de evento para agendado, de agendado para também manual etc.), e aí vale o gatilho como fica depois da mudança.

## O que torna a escrita fraca

- Detalhar a complexidade interna do processo (quantidade de registros, validações, e-mails de falha, relatórios) sem dizer como ele é disparado — isso não muda esta dimensão e deixa o gatilho em falta.
- Escrever "processar em background" ou "enviar para a fila" sem descrever o que dispara o processamento nem quem consome a fila.
- Omitir o disparo manual quando ele existe: um job que "roda à noite e o operador também pode disparar" descrito só como "roda à noite" perde informação relevante.
- Não distinguir síncrono de assíncrono: "o sistema valida e responde" pode ser fluxo principal; só é background se a story deixar claro que continua depois da resposta.
- Em evoluções, descrever a mudança de lógica interna sem dizer se o gatilho mudou — sem essa informação, a dimensão não consegue se posicionar.

## O que deixar explícito

- O gatilho de cada processo: evento (qual evento, interno ou externo), agenda (qual frequência), agenda + manual, ou origem totalmente externa (quem envia, por qual canal).
- Que o processo não bloqueia o usuário: a resposta imediata já foi entregue quando ele executa.
- Se houver fila, o worker assíncrono que a consome.
- Se houver disparo manual além da agenda, declare os dois.
- Em evoluções, declare explicitamente se o mecanismo de disparo mudou ou se só a lógica interna mudou.

## Exemplos de escrita

### ❌ Fraca
> "Um job processa 10.000 registros por noite, aplica 5 validações, envia e-mail em caso de falha e gera relatório."

### ✅ Bem escrita
> "Um job agendado roda diariamente à meia-noite para processar os registros pendentes; o operador também pode dispará-lo manualmente a qualquer momento. As validações aplicadas a cada registro e o envio de e-mail em caso de falha são descritos nas regras de negócio."

### ❌ Fraca
> "Após o pagamento, o sistema processa a confirmação."

### ✅ Bem escrita
> "Quando o gateway de pagamento chama o webhook de confirmação, o sistema registra o recebimento e responde imediatamente; a conciliação do pagamento continua em segundo plano, sem bloquear a resposta."

## Perguntas típicas para o questionário

- O que dispara esse processo: um horário fixo, um evento do sistema, um evento externo (webhook/callback), ou ele vem de fora da aplicação (arquivo de parceiro)?
- O usuário espera o processo terminar para receber a resposta, ou a resposta sai antes e o processo continua depois?
- Além da agenda, é possível disparar o processo manualmente? Isso precisa estar escrito na story?
- Há uma fila envolvida? Quem consome essa fila e quando?
- Se for uma evolução: o gatilho mudou, ou só a lógica interna do processo?
