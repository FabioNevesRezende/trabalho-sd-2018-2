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

'''
def recebeRespostaCmd(s):
    while manterRecebeRespostaCmdVivo:
        try:
            data = s.recv(TAMANHO_MAXIMO_PACOTE)
            if not data: continue
            trataRetorno(data.decode())
        except:
            pass
'''    
def trataRetorno(msg):
    if re.match(r'Ok', msg) == None:
        printa_negativo(msg)
    else:
        printa_positivo(msg)
        
'''
def trataComando(socket, cmd, opcao=""):
    limpaConsole()
    msg = str(cmd + opcao).encode()
    socket.send(msg)
    time.sleep(0.1)
    esperaContinua()
def encerraCliente(socket):
    global manterRecebeRespostaCmdVivo
    global manterConversaUsuario

    printa_negativo('Encerrando aplicação =(')
    manterConversaUsuario = False

    if not manterConversaUsuario:
        time.sleep(5)
        manterRecebeRespostaCmdVivo = False
        socket.close()
'''

def conversaUsuario(stub):
    global manterConversaUsuario

    while manterConversaUsuario:
        limpaConsole()
        printaMenuPrincipal()
        inputUsuario = pegaInput()
        if len(inputUsuario) == 0: continue
        
        opcao = inputUsuario.split(' ')[0]
        c = int(inputUsuario.split(' ')[1])
        v = inputUsuario.split(' ')[2]

        printa_neutro('Comando a ser executado: ' + opcao + ' ' + str(c) + ' ' + v)
        if opcao[:6].lower() == 'create':
            #trataComando(s, comandos['create'], opcao[6:])
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
            #encerraCliente(s)
            printa_negativo('Encerrando aplicação =(')
            manterConversaUsuario = False
            manterRecebeRespostaCmdVivo = False
            return
        else:
            limpaConsole()
            printa_negativo('Opção Inválida')
            esperaContinua()
        if response:
            trataRetorno(response)
            

def main():
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_SOCKET, PORTA_SOCKET))
    s.setblocking(0)
    '''
    
    with grpc.insecure_channel(str(IP_SOCKET) + ':' + str(PORTA_SOCKET)) as channel:
        stub = interface_pb2_grpc.ManipulaMapaStub(channel)
        #response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
    #print("Greeter client received: " + response.message)

        fio1 = Thread(target=conversaUsuario, args=(stub, ))
        fio1.start()

    #fio2 = Thread(target=recebeRespostaCmd, args=(stub, ))
    #fio2.start()

if __name__ == '__main__':
    main()
