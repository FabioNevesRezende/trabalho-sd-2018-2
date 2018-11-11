from threading import *
from termcolor import colored
import grpc
import interface_pb2
import interface_pb2_grpc
import sys
import time
import socket
import traceback
import os
import yaml
import argparse

configs               = yaml.load(open('configs.yml', 'r'))
IP_SOCKET             = configs['IP_SOCKET']
PORTA_SOCKET          = configs['PORTA_SOCKET']
TAMANHO_MAXIMO_PACOTE = configs['TAMANHO_MAXIMO_PACOTE']
DIR_LOG               = configs['DIR_LOG']
DIR_SNAP              = configs['DIR_SNAP']
SLEEP_TIME            = configs['SLEEP_TIME']
PREFIXO_PORTA         = configs['PREFIXO_PORTA']
SERVIDORES            = configs['SERVIDORES']
DB_PARAMS             = configs['DB_PARAMS']

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
        split = objsrl.split(', ', 1)
        chave = split[0][6:]
        valor = split[1][6:].strip()
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

    def recuperaUltimo(self):
        if self.tamanho() > 0:
            return self.fila[0]

# Manipula os arquivos como um fila
class ManipulaArquivosLog():
    def __init__(self, dirNome,index=0, separador='.'):
        self.dirNome = dirNome
        self.listaArquivos = Fila()
        self.index = index
        self.criaDirSeNaoExiste(self.dirNome)
        self.recuperaArquivos()

    def criaDirSeNaoExiste(self, dirNome):
        print('Nome diretorio - {}'.format(dirNome))
        if not os.path.exists(dirNome):
            os.makedirs(dirNome)

    # Instancia os arquivo na lista de arquivos e verifica o incremental para criação dos logs
    def recuperaArquivos(self, separador='.'):
        arquivos = os.listdir(self.dirNome)
        arquivos.sort()
        if len(arquivos) > 0:
            self.index = int(arquivos[-1].split(separador)[1]) + 1
            for name in arquivos:
                self.listaArquivos.enfileira((open(self.dirNome + name, 'r+')))

    #Remove o arquivo mais antigo da lista e da memoria
    def removeArquivo(self):
        caminhoRemovido = str(self.listaArquivos.desenfileira().name)
        os.remove(caminhoRemovido)
    
    #Adiciona um arquivo em memoria e em arquivo
    def adicionaArquivo(self, arquivo):
        if self.listaArquivos.tamanho() >= 3:
            self.removeArquivo()
        self.listaArquivos.enfileira(arquivo)
        self.index += 1
        
class Configs(object):
    class __Configs:
        def __init__(self, args=None):
            self.id        = args.id
            self.anterior  = args.anterior
            self.posterior = args.posterior 
            self.valida_posicao()
            self.tabela()
        
        def __str__(self):
            rep = {'id': self.id }
            return str(rep)
        
        def valida_posicao(self):
            self.sou_primeiro = True if self.anterior >= self.id else False
            self.sou_ultimo   = True if self.posterior <= self.id else False

        def valida_chave(self, chave):
            if chave in self.range:
                return (True,)
            elif chave > self.id:
                return (False, self.posterior)
            else:
                return (False, self.anterior)
                
        def tabela(self):
            faixa = list()
            if self.sou_primeiro:
                faixa.append(0)
            else:
                faixa.append(self.anterior + 1)
            faixa.append(self.id)

            self.range = range(faixa[0], faixa[1] + 1)
            
            printa_neutro("Responsável pela faixa: {}".format(faixa))
            printa_neutro("Nó anterior: {}. Nó posterior: {}".format(self.anterior, self.posterior))

    instance = None
    def __new__(cls, args=None): # __new__ always a classmethod
        if not Configs.instance:
            Configs.instance = Configs.__Configs(args)
        return Configs.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)

def configura_servidor(args):
    return Configs(args)