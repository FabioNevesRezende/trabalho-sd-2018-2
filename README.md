A aplicação roda em Python3, não foi testada em Python2
Todos os requisitos do professor estão nos comentários do arquivo common.py segundo slides
Para rodar a aplicação, é necessário ter a biblioteca termcolor do python

sudo -H pip3 install --upgrade pip
sudo pip3 install termcolor
sudo pip3 install pytest

## Rodar testes
Para rodar os testes, em um terminal, digite: `pytest test_cliente.py -vv`.
Dessa forma, os testes serão executados em ordem de aparecimento no código. (_Importante para a primeira sequencia de tests_)