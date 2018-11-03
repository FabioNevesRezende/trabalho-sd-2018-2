## Informações Gerais
A aplicação roda em Python3, não foi testada em Python2.

Todos os requisitos do professor estão nos comentários do arquivo common.py segundo slides

# Instalação
Para rodar a aplicação, é necessário ter as bibliotecas python: termcolor, pytest, pyyaml e gRPC

```bash
sudo -H pip3 install --upgrade pip
sudo pip3 install termcolor
sudo pip3 install pytest
sudo pip3 install pyyaml
sudo pip3 install grpcio grpcio-tools
```

# Geração de stubs
```
python3 -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. interface.proto
```

# Execução
Para iniciar os servidores:
```bash
python3 inicia_servidores.py 4 4
```

Para corretude da aplicação, é necessário definir um M que serão os bits possíveis da chave, e o N: número de servidores, sendo M o primeiro parâmetro e N o segundo.
Se precisar de ajuda:

```bash
python3 inicia_servidores.py -h
```

## Testes
<!-- Para rodar os testes, em um terminal, digite: `pytest test_cliente.py -vv`: dessa forma, os testes serão executados em ordem de aparecimento no código. (_Importante para a primeira sequencia de tests_)
 -->
