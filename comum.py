'''
O objetivo deste projeto é desenvolver um sistema de bancos de
dados genérico/multiuso, a ser usado como bloco de construção
em outros projetos.
Com este objetivo, replicaremos abordagens bem conhecidas e
funcionais, aplicando diversas técnicas de desenvolvimento de
sistemas distribuídos.
O projeto será dividido em 3 entregas, definidas abaixo.

Para a primeira entrega vocês desenvolverão a “cara” do banco
de dados, permitindo que clientes se conectem e realizem
operações de acordo com a especificação da API. Desenvolverão
também um cliente em linha de comando para que se possa
manipular o banco de dados, bem como um cliente de testes,
que estressará o banco para verificar sua corretude e
funcionalidades.

CLIENTE
Leitura de comandos
1 thread em loop infinito apresentando menu de comandos e
lendo comandos do teclado
uma vez digitado um comando, o mesmo é validado
se válido, comando é enviado ao servidor
se inválido, mensagem de erro é apresentada
o comando “sair” termina a execução deste thread
Apresentação de respostas
1 thread em loop infinito recebendo mensagens do servidor
uma vez recebida uma mensagem, a mesma é apresentada
na tela
uma vez terminado o thread de leitura de comandos,
espera-se pelo menos 5 segundos por novas mensagens do
servidor e então se termina este thread

SERVIDOR
A base de dados
é um mapa de BigInteger (inteiro de precisão infinita) para
um vetor de bytes (ou algo que o valha)
mantido em memória apenas (por enquanto)
e manipulado por 4 operações (CRUD)
observando a semântica de cada operação.
Apesar do banco ser em memória, toda operação será logada em
disco.
Terá arquitetura em estágios, tendo
1 ou mais threads recebendo comandos e colocando em
uma fila F1
1 thread consumindo comandos de F1 e colocando cópias
do comando em uma fila F2 e em outra fila F3
1 thread consumindo comandos de F2 e gravando-os em
disco.
1 thread consumindo de F3 aplicando o comando no banco
de dados.

THREAD DE LOGS
grava comandos em um arquivo de log
mantendo o arquivo aberto durante a execução do programa
adicionando comandos sempre ao fim do arquivo
somente se o comando altera a base de dados (Reads são
descartados)

THREAD DE PROCESSAMENTO
executa os comandos
contra o mapa
emitindo mensages de sucesso (create/update/delete)
respondendo com informação solicitada (read)
emitindo erros quando adequado (create/update/delete/read)
na ordem em que os comandos foram enfileirados em F3

FILAS
são estruturas de dados com semântica bem definida.
listas não são filas
pilhas não são filas
arrays não são filas
embora possam ser usados para implementar filas

TOLERÂNCIA A FALHAS
Como o mapa é mantido em memória, no caso de falhas, todo o
banco apagado. Para recuperá-lo
Na reinicialização do processo
abra o arquivo de log
e processe-o na sequência em que foi escrito
reexecutando todas as operações gravadas
antes de aceitar novas requisições de clientes.

ACESSO CONCORRENTE
Diversos clientes podem ser iniciados em paralelo e contactando
o mesmo servidor.

Comunicação
Toda comunicação é feita via TCP.
E o canal de comuniação com o cliente é mantido aberto
enquanto o mesmo estiver executando.
Todas as portas usadas na comunicação são especificadas
via arquivos de configuração.

'''

from termcolor import colored
import sys
import time
import socket
from threading import *
import traceback
import os
import yaml

configs               = yaml.load(open('configs.yml', 'r'))
IP_SOCKET             = configs['IP_SOCKET']
PORTA_SOCKET          = configs['PORTA_SOCKET']
TAMANHO_MAXIMO_PACOTE = configs['TAMANHO_MAXIMO_PACOTE']

# printa uma mensagem colorida com a cor "cor"
def printa_colorido(strng, cor):
    sys.stdout.write(colored(str(strng), cor))

# printa uma mensagem de sucesso com a cor verde
def printa_positivo(mensagem):
    printa_colorido('[+] ', 'green')
    sys.stdout.write(str(mensagem) + '\n')

# printa uma mensagem de falha/erro com a cor vermelho
def printa_negativo(mensagem):
    printa_colorido('[-] ', 'red')
    sys.stdout.write(str(mensagem) + '\n')

# printa uma mensagem azul
def printa_neutro(mensagem):
    printa_colorido('[*] ', 'blue')
    sys.stdout.write(str(mensagem) + '\n')

comandos = { 'create' : 'CREA', 'read' : 'READ', 'update' : 'UPDT', 'delete' : 'DELT', 'die': 'DIE'}

# Define uma dupla {chave-valor}
class ItemMapa():
    def __init__(self, chave, valor):
        self.chave = chave
        self.valor = valor.encode()

    def __setattr__(self, name, value):
        # Verifica se a chave é um Inteiro
        if name == 'chave' and not isinstance(value, int): 
            raise TypeError('Chave do item deve ser um Inteiro')
        # Verifica se o valor é uma string
        if name == 'valor' and not isinstance(value, bytes):
            raise TypeError('Valor do item deve ser um array de bytes')
        super().__setattr__(name, value)

    # Serializa o item em uma string
    def serializa(self):
        return 'Chave: {0}, Valor: {1}'.format(self.chave, self.valor.decode())

    # Desserializa uma string em um ItemMapa
    @staticmethod
    def desserializa(objsrl):
        split = objsrl.split(',', 1)
        chave = split[0][6:]
        valor = split[1][6:]
        return ItemMapa(int(chave),valor)

# Esta classe Fila não é de nossa autoria
# pegamos pronto de https://www.pythoncentral.io/use-queue-beginners-guide/
class Fila:
    # Constructor cria a fila vazia
    def __init__(self):
        self.fila = list()

    # adiciona elemento na fila
    def enfileira(self,data):
        self.fila.insert(0, data)
        return True

    # remove um item da fila
    def desenfileira(self):
        if len(self.fila) > 0:
            return self.fila.pop()
        return None

  # Retorna o nro de elementos da fila
    def tamanho(self):
        return len(self.fila)

    # printa todos os elementos da fila
    def printaFila(self):
        for elem in self.fila:
            print(str(elem))
