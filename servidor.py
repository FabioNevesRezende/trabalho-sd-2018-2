#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from comum import *
import datetime
import io

itensMapa = [] # lista de elementos <bigInteger, string>
conexoes = [] # lista de conexões 
online = True # status do servidor online/offline
filaF1 = Fila() # fila F1 especificada nos requisitos
filaF2 = Fila() # fila F2 especificada nos requisitos
filaF3 = Fila() # fila F3 especificada nos requisitos

try:
    logs = open('logs.log', 'r+') # r+ modo leitura e escrita ao mesmo tempo, se o arquivo não existir, ele NÃO o cria, por isso o try-catch
except FileNotFoundError:
    logs = open('logs.log', 'w') # r+ modo escrita já que é a primeira vez não tem nada a ser lido
    

def criaItensMapaLogs():
    try:
        for linha in logs.readlines():
            comando = linha.split(' ')[0]
            chave = int(linha.split(' ')[1])
            if comando == comandos['create']:
                itensMapa.append(ItemMapa(chave, linha.split(' ')[2]))
            if comando == comandos['update']:
                pass
            if comando == comandos['delete']:
                pass #
            # não precisa implementar o read nesta leitura inicial já que ele não altera o estado do mapa de itens
    except io.UnsupportedOperation: # se não conseguir ler as linhas significa que o arquivo está aberto em modo de escrita apenas "w"
        printa_neutro('Não há nenhum log a ser lido')
        

# Analisa configuração inicial 
def parsaConfigIni():

    printa_neutro('Vai ler arquivo de inicialização')

    # recupera o estado, se houver
    criaItensMapaLogs()

    printa_positivo('Terminada a leitura de arquivo de inicialização, estado atual da lista de itens: ')
    printaItens()

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

    if not temItem(chave):
        itensMapa.append(ItemMapa(chave, valor))
        msg = 'Novo item ' + valor + ' criado com sucesso com ID: ' + str(chave)
        printa_positivo(msg)
        return msg

def loga(msg):
    logs.write(msg)
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
            loga(cmd + '\n')
            
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
            logs.close()
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
        logs.close()
        printa_negativo('Erro ao rodar servidor: ')
        printa_negativo(str(e))
        traceback.print_exc()



















