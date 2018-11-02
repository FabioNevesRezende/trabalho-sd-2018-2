Para testar o sistema, quando um servidor for carregado, imprima toda a sua tabela de roteamento e deixe explícito a faixa de chaves pertencentes ao servidor em questão. Mostre que as faixas são definidas como especificado.

Conecte-se a um servidor e execute  CRUD OK e CRUD NOK  em uma chave correspondendo a cada faixa de chaves, demonstrando o roteamento de requisições e que o funcionamento da entrega 1 é mantido na entrega 2.

Execute CRUD na chave 0.
Execute CRUD na chave 2^m - 1
Tente executar CRUD em uma chave negativa e verifique que falha.
Tente executar CRUD em uma chave maior que 2^m -1 e verifique que falha.

Após inserir uma chave/valor em cada faixa, reinicie os servidores e demostre que as chaves são recuperadas.

Demonstre que os snapshots são feitos com frequência pré-determinada e que snapshots antigos são removidos.

Demonstre que chaves inseridas durante a tomada do snapshot são adequadamente armazenadas no log.

Lásaro