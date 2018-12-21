# Importante!!!
Conforme conversado na última apresentação(**alunos Nicolas e Pedro no dia 19/12**), as alterações foram realizadas permitindo que o servidores subam corretamente em conjuntos com suas respectivas replicas.

Ao iniciar o cliente, por algum motivo não identificado os primeiros comandos demoram um pouco para serem respondidos, mas o cliente **funciona**.

# Instalação
Para rodar a aplicação, é necessário ter as bibliotecas python: termcolor, pytest, pyyaml e gRPC


```bash
sudo apt install python-pip
sudo python -m pip install importlib
sudo python -m pip install termcolor
sudo python -m pip install pytest
sudo python -m pip install pyyaml
sudo python -m pip install grpcio grpcio-tools
sudo python -m pip install numpy
sudo python -m pip install future
sudo python -m  pip install concoord
```

# Geração de stubs
```
python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. interface.proto
```

# Execução
Para iniciar os servidores:
```bash
sudo python inicia_servidores.py 2 2
```

Para corretude da aplicação, é necessário definir um M que serão os bits possíveis da chave, e o N: número de servidores, sendo M o primeiro parâmetro e N o segundo.
Se precisar de ajuda:

```bash
python inicia_servidores.py -h
```

## Testes
<!-- Para rodar os testes, em um terminal, digite: `pytest test_cliente.py -vv`: dessa forma, os testes serão executados em ordem de aparecimento no código. (_Importante para a primeira sequencia de tests_)
 -->
