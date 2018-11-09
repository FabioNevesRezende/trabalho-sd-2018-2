#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from comum import *
import random
import re
import numpy as np

import signal
import sys

manterRecebeRespostaCmdVivo = True
manterConversaUsuario       = True
servidores                  = None
threads                     = list()

# printa o menu principal em stdout
def printaMenuPrincipal():
    printa_positivo('Bem vindo. Digite uma das opções:')
    printa_neutro(' CREATE <chave> <valor> para criar um item no mapa')
    printa_neutro(' READ para receber todos os itens do mapa')
    printa_neutro(' READ <chave> para receber um item pela sua chave')
    printa_neutro(' UPDATE <chave> <valor> para alterar um item no mapa')
    printa_neutro(' DELELE <chave> para remover um item pela sua chave')
    printa_neutro(' SAIR, para sair')
    printa_colorido(' > ', 'green')

# pega o input do teclado
def pegaInput():
    inp = input()
    sys.stdin.flush() # limpa o buffer stdin
    return inp

# esta função serve apenas para pausar a execução
def esperaContinua():
    printa_neutro('Pressione ENTER para continuar')
    _nada = pegaInput()

# limpa o console
def limpaConsole():
    os.system('clear')

def trataRetorno(resposta_grpc):
    status = resposta_grpc.result().resposta
    if re.match(r'Ok', status) == None:
        printa_negativo(status)
    else:
        printa_positivo(status)
        
def trataComando(cmd, opcao=""):
    chave = ''
    valor = ''

    try:
        chave = int(cmd.split(' ')[1])
        valor = cmd.split(' ')[2]
    except IndexError:
        pass
    
    return chave, valor

def encerraCliente(signal=None, frame=None):
    global manterRecebeRespostaCmdVivo
    global manterConversaUsuario

    printa_negativo('Encerrando aplicação =(')
    manterConversaUsuario = False

    if not manterConversaUsuario:
        time.sleep(5)
        sys.exit()

def cria_stub():
    servidor = random.choice(servidores)
    endereco = '{}:{}{}'.format(IP_SOCKET, PREFIXO_PORTA, servidor)
    channel  = grpc.insecure_channel(endereco)
    return interface_pb2_grpc.ManipulaMapaStub(channel)

def conversaUsuario():
    while manterConversaUsuario:
        limpaConsole()
        printaMenuPrincipal()
        inputUsuario = pegaInput().strip()

        if len(inputUsuario) == 0: continue
        
        stub = cria_stub()
        opcao = inputUsuario.split(' ')[0]
        c, v  = trataComando(inputUsuario)

        if c < 0:
            printa_negativo('Chave inválida!')
            esperaContinua()
            continue
        
        if opcao[:6].lower() == 'create':
            future = stub.CriaItem.future(interface_pb2.msgItem(chave=c ,valor=v))
            future.add_done_callback(trataRetorno)
            esperaContinua()
        elif opcao[:4].lower() == 'read':
            future = stub.LeItem.future(interface_pb2.msgItem(chave=c))
            future.add_done_callback(trataRetorno)
            esperaContinua()
        elif opcao[:6].lower() == 'update':
            future = stub.AtualizaItem.future(interface_pb2.msgItem(chave=c, valor=v))
            future.add_done_callback(trataRetorno)
            esperaContinua()
        elif opcao[:6].lower() == 'delete':
            future = stub.DeletaItem.future(interface_pb2.msgItem(chave=c))
            future.add_done_callback(trataRetorno)
            esperaContinua()
        elif opcao[:4].lower() == 'sair':
            encerraCliente()
        else:
            limpaConsole()
            printa_negativo('Opção Inválida')
            esperaContinua()

def configura_cliente():
    fio1 = Thread(target=conversaUsuario)
    threads.append(fio1)

    fio1.start()

def main():
    global servidores

    try:
        servidores = np.fromfile(SERVIDORES, sep='\n', dtype=int)
        signal.signal(signal.SIGINT, encerraCliente)
        configura_cliente()
    except FileNotFoundError:
        printa_negativo("Arquivo de servidores inexistente!")
        return

if __name__ == '__main__':
    main()
