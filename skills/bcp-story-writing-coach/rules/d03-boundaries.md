
# D3 · Boundaries

Esta dimensão mede as fronteiras que a story cruza: trocas de informação com algo fora do escopo da própria aplicação (suas telas e seu banco de dados). Cada fronteira distinta tem sua complexidade definida pela natureza da informação trocada — quem fica dono dela, por quanto tempo ela é válida e se ela é persistida ou efêmera.

## O que o avaliador procura

- Toda troca de informação com algo fora do escopo da aplicação: um dispositivo físico (impressora, scanner, sensor, leitor de cartão, leitor de código de barras, importação/exportação de arquivo) ou um serviço de negócio remoto de outra aplicação.
- A direção da troca principal: a story recebe dados do sistema externo ou envia dados para ele? A direção muda a natureza da fronteira — receber dado em tempo real não é o mesmo que enviar um catálogo que o outro lado armazena.
- Três propriedades da informação trocada:
  - **Ownership**: quem recebe passa a ser dono do dado ou continua dependendo da fonte?
  - **Validade**: o dado é válido indefinidamente depois de recebido, ou só no instante da troca?
  - **Durabilidade**: o dado é persistido e duradouro, ou temporário e efêmero?
- A natureza da troca com serviços remotos:
  - **Perene**: o consumidor armazena o dado e pode reutilizá-lo depois sem revalidar (ex.: importar o cadastro de um cliente que passamos a possuir).
  - **Volátil**: o dado só é válido no instante da troca e o consumidor não pode assumir ownership (ex.: token de autorização de pagamento em tempo real, cotação de preço ao vivo).
- Contagem uma vez por fronteira distinta, não por troca: chamar o mesmo serviço três vezes é uma fronteira; trocar vários tipos de dado com o mesmo sistema ainda é uma fronteira — mas um mesmo parceiro trocando dado perene e volátil conta duas naturezas distintas.
- Se a story não cruza fronteira nenhuma (só telas e banco próprio), ela é autocontida — isso também é declarado na avaliação.

## O que torna a escrita fraca

- Mencionar a integração sem dizer o que é trocado: "integrar com o serviço de pagamento" não diz se recebemos um token efêmero ou importamos um histórico permanente.
- Não deixar claro quem fica dono do dado depois da troca — é o que distingue uma importação perene de uma consulta volátil.
- Omitir a direção: "sincronizar com o parceiro" não diz se enviamos ou recebemos.
- Não mencionar dispositivos físicos: se a story lê código de barras de um scanner ou importa um arquivo, isso é uma fronteira e precisa estar escrito.
- Esconder múltiplas naturezas de troca com o mesmo parceiro: se o mesmo serviço devolve um perfil que armazenamos e um token de uso único, são duas naturezas e ambas devem aparecer no texto.

## O que deixar explícito

- Cada sistema externo, serviço remoto ou dispositivo físico envolvido, nomeado individualmente.
- Para cada fronteira: a direção da troca (recebemos ou enviamos) e o dado concreto trocado.
- Se o dado recebido será armazenado e reutilizado pela nossa aplicação (perene) ou se só vale no momento da chamada (volátil).
- Quando o mesmo parceiro tem trocas de naturezas diferentes, declarar cada uma separadamente.
- Operações com arquivos (importação/exportação) e dispositivos (impressão, leitura) como trocas de fronteira explícitas.

## Exemplos de escrita

### ❌ Fraca
> Integrar com a API de geolocalização para mostrar o endereço do cliente.

### ✅ Bem escrita
> Ao cadastrar um cliente, a aplicação chama o serviço externo de geolocalização, recebe as coordenadas do endereço e as armazena no nosso banco junto ao cadastro — o dado passa a ser nosso e não precisa ser consultado novamente.

### ❌ Fraca
> Processar o pagamento com a operadora.

### ✅ Bem escrita
> No fechamento do pedido, a aplicação envia os dados do pagamento à operadora e recebe um token de autorização válido apenas naquele instante — o token não é persistido e uma nova autorização precisa ser solicitada a cada tentativa.

### ❌ Fraca
> Enviar dados fiscais.

### ✅ Bem escrita
> A aplicação envia o XML da nota fiscal ao serviço da autoridade tributária e trata a resposta imediata de aceite ou rejeição — a resposta só é válida no momento do envio e não pode ser reutilizada.

## Perguntas típicas para o questionário

- A story troca informação com algo fora da aplicação (outro sistema, serviço remoto, dispositivo físico, arquivo)? Qual?
- Para cada integração: nós recebemos o dado ou enviamos? O que exatamente é trocado?
- Depois da troca, quem fica dono do dado? Nós armazenamos e reutilizamos, ou ele só vale naquele instante?
- O mesmo parceiro tem trocas de naturezas diferentes (algo que armazenamos e algo efêmero)?
- Há interação com dispositivo físico ou importação/exportação de arquivo?
