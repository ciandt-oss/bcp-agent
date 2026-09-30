
# D9 · Notifications

Esta dimensão conta os eventos de negócio distintos que disparam mensagens a pessoas humanas — não os canais usados, nem a quantidade de destinatários. A complexidade cresce com o número de eventos de negócio diferentes que geram comunicação.

## O que o avaliador procura

- Eventos de negócio distintos que disparam uma mensagem a uma pessoa: "usuário registrado", "pedido aprovado", "senha redefinida" — cada um é um evento.
- Canais de entrega a humanos: e-mail, SMS, push notification, notificação in-app (toast/snackbar/banner), WhatsApp, mensagem em Slack/Teams — todos são canais do mesmo evento, não eventos separados.
- Múltiplos destinatários do mesmo evento não multiplicam a contagem: e-mail ao admin e ao usuário no registro continua sendo um evento.
- Múltiplos canais do mesmo evento não multiplicam a contagem: e-mail + SMS quando o pedido é aprovado continua sendo um evento.
- Conteúdo da mensagem (assunto, corpo, campos) não é evento separado.

O que NÃO é notificação:

- Webhooks e callbacks de API — são comunicação sistema-a-sistema, pertencem a D3 · Boundaries (integrações).
- Publicação em filas e eventos de domínio — mensageria técnica, não mensagem a pessoa.
- Logging e trilhas de auditoria — pertencem a D10 · Audits.
- Alertas de monitoramento — observabilidade, não notificação de negócio.

Menções sem canal nem evento identificável ("avisar o admin", "notificar o usuário") não são contáveis — são lacunas que o avaliador marca para esclarecimento.

## O que torna a escrita fraca

- Dizer "notificar o usuário" ou "avisar o admin" sem nomear o evento de negócio que dispara a mensagem nem o canal — sem os dois, a menção não é contável e vira pergunta pendente.
- Escrever "enviar e-mail e SMS" sem dizer a que evento isso se refere — canal sem evento não caracteriza notificação.
- Misturar webhook/callback de API com notificação a pessoa na mesma frase — o avaliador separa os dois, e a ambiguidade gera classificação errada entre D9 e D3.
- Misturar logging/auditoria ("registrar quem aprovou") com notificação ("avisar o solicitante") — o primeiro é D10, o segundo é D9.
- Descrever o mesmo evento várias vezes por canal ("e-mail quando aprovado" e "SMS quando aprovado") como se fossem dois requisitos distintos — é um evento com dois canais, e a escrita deve deixar isso claro.

## O que deixar explícito

- Cada evento de negócio que dispara mensagem: o que aconteceu (registro concluído, pedido aprovado, pedido enviado).
- O canal de cada mensagem: e-mail, SMS, push, in-app, WhatsApp, Slack/Teams.
- Quando o mesmo evento usar vários canais ou vários destinatários, escreva como um único disparo ("e-mail e SMS quando o pedido for aprovado", "e-mail ao admin e ao usuário no registro").
- Distinga na redação: mensagem a pessoa (notificação), chamada sistema-a-sistema (webhook → D3), registro de quem fez o quê (auditoria → D10).

## Exemplos de escrita

### ❌ Fraca
> "O sistema deve avisar o admin e mandar notificação pro usuário."

### ✅ Bem escrita
> "Quando um artigo for submetido, o sistema envia e-mail ao admin, ao pesquisador e ao revisor (um evento, três destinatários). Quando o artigo for aprovado, o sistema envia SMS e e-mail ao autor (segundo evento, dois canais)."

### ❌ Fraca
> "Enviar e-mail, SMS e push em várias situações do pedido."

### ✅ Bem escrita
> "Três eventos disparam notificações: registro do usuário (e-mail), aprovação do pedido (SMS) e envio do pedido (push notification)."

## Perguntas típicas para o questionário

- Quais eventos de negócio disparam mensagens a pessoas nesta story? Liste cada um.
- Para cada evento, qual é o canal (e-mail, SMS, push, in-app, WhatsApp)?
- Algum dos disparos descritos é na verdade um webhook ou callback para outro sistema? (Isso é integração, não notificação.)
- "Avisar/notificar" aparece sem canal ou sem evento definido? Qual é o evento e qual é o canal?
- Há registro de quem fez o quê misturado com as notificações? (Isso é auditoria, não notificação.)
