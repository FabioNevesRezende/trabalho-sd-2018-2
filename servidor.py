#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from comum import *
import sqlite3
import datetime

itensMapa = [] # lista de elementos <bigInteger, string>
conexoes = [] # lista de conexões 
online = True # status do servidor online/offline
filaF1 = Fila() # fila F1 especificada nos requisitos
filaF2 = Fila() # fila F2 especificada nos requisitos
filaF3 = Fila() # fila F3 especificada nos requisitos

connDb = sqlite3.connect('servidor.db')

# Analisa configuração inicial 
def parsaConfigIni():

    printa_neutro('Vai ler arquivo de inicialização')

    cursor = connDb.cursor()
    cursor.execute('create table if not exists logs (comando text, horario text)')
    cursor.execute('create table if not exists itens (chave text, valor text)')

    # recupera o estado, se houver
    cursor.execute('select chave, valor from itens')
    for row in cursor:
        itensMapa.append(ItemMapa(int(row[0]), row[1]))

    printa_positivo('Terminada a leitura de arquivo de inicialização, estado atual da lista de itens: ')
    printaItens()
    connDb.close()

# printa todos os itens
def printaItens():
    for item in itensMapa:
        item.printa()

def temItem(chave):
    for elem in itensMapa:
        if elem.chave == chave:
            return True
    return False

# cria um novo item e o adiciona à lista
def criaItem(chave, valor):
    global connDb

    if not temItem(chave):
        itensMapa.append(ItemMapa(chave, valor))
        cursor = connDb.cursor()
        cursor.execute("insert into itens(chave, valor) values (?,?)", (chave,valor))
        msg = 'Novo item ' + valor + ' criado com sucesso com ID: ' + str(chave)
        printa_positivo(msg)
        connDb.commit()
        connDb.close()
        return msg

def loga(msg):
    global connDb
    
    cursor = connDb.cursor()
    cursor.execute("insert into logs(comando, horario) values (?,?)", (msg,str(datetime.datetime.now())))
    connDb.commit()
    connDb.close()
    printa_positivo(msg + ' logada com sucesso')
    

# Thread que pega os comandos recem chegados do cliente e despacha para as filas F2 e F3
def trataComandosFilaF1():
    while online:
        while filaF1.tamanho() > 0:
            cmd, addr = filaF1.desenfileira()
            filaF2.enfileira((cmd, addr))
            filaF3.enfileira((cmd, addr))
            
# Thread que pega os comandos e os loga
def trataComandosFilaF2():
    while online:
        while filaF2.tamanho() > 0:
            cmd, addr = filaF2.desenfileira()
            loga(cmd)
            
# Thread que pega os comandos e os executa
def trataComandosFilaF3():
    while online:
        while filaF3.tamanho() > 0:
            cmd, addr = filaF3.desenfileira()
            
            
# Função que escuta comandos dos clientes (executado na Thread principal)
def escutaComandos():
    global online

    while online:
        try:
            for conn, addr in conexoes: # para cada conexão
                data = conn.recv(TAMANHO_MAXIMO_PACOTE)
                if not data: continue
                recebido = str(data.decode())
                printa_positivo('Recebeu "' + recebido + '" de: ' + str(addr))

                # se os 4 primeiros caracteres do que foi recebido for um dos 4 comandos CRUD aceitos no vetor "comandos"...
                if recebido[:4] == comandos['create'] or recebido[:4] == comandos['read'] or recebido[:4] == comandos['update'] or recebido[:4] == comandos['delete']:
                    filaF1.enfileira((recebido, addr))
                    conn.send(('Recebi de você: ' + recebido).encode())
                else:
                    printa_negativo('Recebido comando inválido de ' + str(addr))

        except KeyboardInterrupt as interrput:
            printa_negativo('Encerrando aplicação =(')
            online = False

# inicia o servidor TCP no endereço IP_SOCKET e na porta PORTA_SOCKET
def iniciaServidor():
    printa_positivo('Vai iniciar servidor TCP em ' + str(IP_SOCKET) + ':' + str(PORTA_SOCKET))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # inicia servidor tcp
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # diz para reusar porta 
    s.bind((IP_SOCKET, PORTA_SOCKET)) # atrela socket à porta no SO
    s.listen(50)
    return s

# loop infinito que escuta por novas conexoes e as adiciona no vetor "conexoes"
def escutaConexoes(s):
    global online
    
    while online:
        conn, addr = s.accept()
        printa_neutro('Iniciada conexão com ' + str(addr))
        conexoes.append((conn, addr))

# Main e ponto de inicio da aplicação
def main():
    parsaConfigIni()
    s = iniciaServidor()
    
    fio1 = Thread(target=escutaConexoes, args=(s,))
    fio1.start()  # inicia thread que escuta por novas conexoes

    fio2 = Thread(target=trataComandosFilaF1, args=())
    fio2.start()  # inicia thread que trata elementos da fila F1
    
    fio3 = Thread(target=trataComandosFilaF2, args=())
    fio3.start()  # inicia thread que trata elementos da fila F2
    
    fio4 = Thread(target=trataComandosFilaF3, args=())
    fio4.start()  # inicia thread que trata elementos da fila F3

    escutaComandos() # na thread principal, escuta comandos vindos do(s) cliente(s) e os adiciona na Fila F1


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        printa_negativo('Erro ao rodar servidor: ')
        printa_negativo(str(e))
        traceback.print_exc()



















