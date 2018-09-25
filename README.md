## Informações Gerais
A aplicação roda em Python3, não foi testada em Python2.

Todos os requisitos do professor estão nos comentários do arquivo common.py segundo slides

# Instalação
Para rodar a aplicação, é necessário ter a biblioteca termcolor do python

```bash
sudo -H pip3 install --upgrade pip
sudo pip3 install termcolor
sudo pip3 install pytest
sudo pip3 install pyyaml
```

## Testes
Para rodar os testes, em um terminal, digite: `pytest test_cliente.py -vv`: dessa forma, os testes serão executados em ordem de aparecimento no código. (_Importante para a primeira sequencia de tests_)
