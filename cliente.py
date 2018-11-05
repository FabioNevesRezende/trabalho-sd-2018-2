#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from comum import *
import random
import re

manterRecebeRespostaCmdVivo = True
manterConversaUsuario = True

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

def trataRetorno(status):
    status = status.resposta
    if re.match(r'Ok', status) == None:
        printa_negativo(status)
    else:
        printa_positivo(status)
        
def trataComando(cmd, opcao=""):
    chave   = ''
    valor   = ''

    try:
        chave = int(cmd.split(' ')[1])
        valor = cmd.split(' ')[2]
    except IndexError:
        pass
    
    return chave, valor

def encerraCliente():
    global manterRecebeRespostaCmdVivo
    global manterConversaUsuario

    printa_negativo('Encerrando aplicação =(')
    manterConversaUsuario = False

    if not manterConversaUsuario:
        time.sleep(5)

def conversaUsuario(stub):
    global manterConversaUsuario

    while manterConversaUsuario:
        limpaConsole()
        printaMenuPrincipal()
        inputUsuario = pegaInput().strip()

        if len(inputUsuario) == 0: continue
        
        opcao = inputUsuario.split(' ')[0]
        c, v  = trataComando(inputUsuario)
        
        if opcao[:6].lower() == 'create':
            response = stub.CriaItem(interface_pb2.msgItem(chave=c ,valor=v))
            time.sleep(0.1)
            esperaContinua()
        elif opcao[:4].lower() == 'read':
            response = stub.LeItem(interface_pb2.msgItem(chave=c))
            time.sleep(0.1)
            esperaContinua()
        elif opcao[:6].lower() == 'update':
            response = stub.AtualizaItem(interface_pb2.msgItem(chave=c, valor=v))
            time.sleep(0.1)
            esperaContinua()
        elif opcao[:6].lower() == 'delete':
            response = stub.DeletaItem(interface_pb2.msgItem(chave=c))
            time.sleep(0.1)
            esperaContinua()
        elif opcao[:4].lower() == 'sair':
            encerraCliente()
        else:
            limpaConsole()
            printa_negativo('Opção Inválida')
            esperaContinua()
        if response:
            trataRetorno(response)
            esperaContinua()

            del response

def main():
    # TODO: escolher servidor random
    # TODO: carregar servidores em memória (NUMPY)

    channel = grpc.insecure_channel('{}:{}{}'.format(IP_SOCKET, PREFIXO_PORTA, 3))
    stub    = interface_pb2_grpc.ManipulaMapaStub(channel)

    fio1 = Thread(target=conversaUsuario, args=(stub, ))
    fio1.start()

if __name__ == '__main__':
    main()
