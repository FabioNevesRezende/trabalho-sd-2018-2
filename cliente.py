#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from comum import *
import random

rodando   = True

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

def recebeRespostaCmd(s):
    global rodando

    while rodando:
        try:
            data = s.recv(TAMANHO_MAXIMO_PACOTE)
            if not data: continue
            printa_neutro(data.decode())
        except:
            pass

def trataComando(socket, cmd, opcao=""):
    limpaConsole()
    msg = str(cmd + opcao).encode()
    socket.send(msg)
    time.sleep(0.1)
    esperaContinua()

def conversaUsuario(s):
    global rodando

    while rodando:
        limpaConsole()
        printaMenuPrincipal()
        opcao = pegaInput()

        if len(opcao) == 0: continue
        if opcao[:6].lower() == 'create':
            trataComando(s, comandos['create'], opcao[6:])
        elif opcao[:4].lower() == 'read':
            trataComando(s, comandos['read'], opcao[4:])
        elif opcao[:6].lower() == 'update':
            trataComando(s, comandos['update'], opcao[6:])
        elif opcao[:6].lower() == 'delete':
            trataComando(s, comandos['delete'], opcao[6:])
        elif opcao[:4].lower() == 'sair':
            s.send(comandos['die'].encode())
            rodando = False
        else:
            limpaConsole()
            printa_negativo('Opção Inválida')
            esperaContinua()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_SOCKET, PORTA_SOCKET))
    s.setblocking(0)
    fio1 = Thread(target=conversaUsuario, args=(s, ))
    fio1.start()

    fio2 = Thread(target=recebeRespostaCmd, args=(s, ))
    fio2.start()

if __name__ == '__main__':
    main()
