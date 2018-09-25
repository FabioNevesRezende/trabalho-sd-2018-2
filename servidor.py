#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from comum import *
import datetime
import io

itensMapa = [] # lista de elementos <bigInteger, string>
conexoes  = [] # lista de conexões 
online    = True # status do servidor online/offline
filaF1    = Fila() # fila F1 especificada nos requisitos
filaF2    = Fila() # fila F2 especificada nos requisitos
filaF3    = Fila() # fila F3 especificada nos requisitos

try:
    logs = open('logs.log', 'r+') # r+ modo leitura e escrita ao mesmo tempo, se o arquivo não existir, ele NÃO o cria, por isso o try-catch
except FileNotFoundError:
    logs = open('logs.log', 'w') # r+ modo escrita já que é a primeira vez não tem nada a ser lido
    
'''
Recria itens em memória
'''
def criaItensMapaLogs():
    try:
        for linha in logs.readlines():
            executaComandos(linha)
    except io.UnsupportedOperation: # se não conseguir ler as linhas significa que o arquivo está aberto em modo de escrita apenas "w"
        printa_neutro('Não há nenhum log a ser lido')

#Função para executar os métodos em memória
def executaComandos(cmd, msg=[""]):
    comando = cmd.strip().split(' ')[0]
    chave   = ''

    try:
        chave = int(cmd.split(' ')[1])
    except IndexError:
        return leTodosItens(msg)

    if comando == comandos['create']:
        return criaItem(chave, cmd.strip().split(' ')[2], msg)
    if comando == comandos['update']:
        return atualizaItem(chave, cmd.strip().split(' ')[2], msg)
    if comando == comandos['delete']:
        return removeItem(chave, msg) 
    if comando == comandos['read']:
        return leItem(chave, msg)

# Analisa configuração inicial 
def parsaConfigIni():
    printa_neutro('Lerá arquivo de inicialização')
    # recupera o estado, se houver
    criaItensMapaLogs()
    printa_positivo('Terminada a leitura de arquivo de inicialização, estado atual da lista de itens: ')
    printaItens()

# printa todos os itens
def printaItens():
    for item in itensMapa:
        printa_neutro(item.serializa())

'''
@param: chave: Chave do item
Verifica se o item existe no "banco"
'''
def temItem(chave):
    for elem in itensMapa:
        if elem.chave == chave:
            return itensMapa.index(elem)
    return 

# Cria um novo item e o adiciona à lista
def criaItem(chave, valor, msg=[""]):
    if  temItem(chave)==None:
        itensMapa.append(ItemMapa(chave, valor))
        msg[0] = 'Ok - Item criado.'
        printa_positivo(msg[0])
        return True
    else:
        msg[0] = 'NOk - Chave existente.'
        printa_negativo(msg[0])
        return False

# Atualiza um item, caso exista
def atualizaItem(chave, valor, msg=[""]):
    index = temItem(chave)
    if not index==None:
        itensMapa[index] = ItemMapa(chave,valor)
        msg[0] = 'Ok - Item atualizado.'
        printa_positivo(msg[0])
        return True
    else:
        msg[0] = 'NOk - Chave inexistente.'
        printa_negativo(msg[0])
        return False

# Remove um item, caso exista
def removeItem(chave, msg=[""]):
    index = temItem(chave)
    if not index==None:
        del itensMapa[index]
        msg[0] = 'Ok - Item removido.'
        printa_positivo(msg[0])
        printaItens()
        return True
    else:
        msg[0] = 'NOk - Chave inexistente.'
        printa_negativo(msg[0])
        return False

# Lê um item e o retorna a conexão, caso exista
def leItem(chave, msg=[""]):
    index = temItem(chave)
    if not index==None:
        msg[0] = str('Ok - Item: ' + itensMapa[index].serializa())
        printa_positivo(msg[0])
        return True
    else:
        msg[0] = 'NOk - Chave inexistente.'
        printa_negativo(msg[0])
        return False

# Lê um item e o retorna a conexão, caso exista
def leTodosItens(msg=[""]):
    if len(itensMapa) > 0:
        msg[0] = 'Ok - Itens: ' + str([p.serializa() for p in itensMapa])
        printa_positivo(msg[0])
        return True
    else:
        msg[0] = 'NOk - Banco vazio.'
        printa_negativo(msg[0])
        return False

def loga(msg):
    logs.write(msg)
    logs.flush() # garante a escrita no arquivo sem ter que fechá-lo
    printa_positivo(msg + ' logada com sucesso')
    
# Thread que pega os comandos recem chegados do cliente e despacha para as filas F2 e F3
def trataComandosFilaF1():
    while online:
        while filaF1.tamanho() > 0:
            cmd, conn, _addr = filaF1.desenfileira()
            filaF2.enfileira(cmd)
            filaF3.enfileira((cmd, conn))
            
# Thread que pega os comandos e os loga
def trataComandosFilaF2():
    while online:
        while filaF2.tamanho() > 0:
            cmd = filaF2.desenfileira()
            if cmd[:4] != comandos['read']:
                loga(cmd + '\n')
            
# Thread que pega os comandos e os executa
def trataComandosFilaF3():
    while online:
        msg = [""] #Cria uma lista com apenas um elemento que será a mensagem retonada da execução dos comandos
        while filaF3.tamanho() > 0:
            cmd, conn = filaF3.desenfileira()            
            executaComandos(cmd, msg)
            conn.send(msg[0].encode())
            print('Lista atual:')
            printaItens()
            
def encerraServidor():
    global online
    printa_negativo('Encerrando aplicação =(')
    logs.close()
    online = False

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
                    filaF1.enfileira((recebido, conn, addr))
                    conn.send(('Recebi de você: ' + recebido).encode())
                elif recebido[:4] == comandos['die']:
                    time.sleep(5)
                    raise KeyboardInterrupt
                else:
                    printa_negativo('Recebido comando inválido de ' + str(addr))
        except (KeyboardInterrupt, ConnectionResetError):
            encerraServidor()

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
    fio1.daemon = True
    fio1.start()  # inicia thread que escuta por novas conexoes

    fio2 = Thread(target=trataComandosFilaF1, args=())
    fio2.daemon = True
    fio2.start()  # inicia thread que trata elementos da fila F1
    
    fio3 = Thread(target=trataComandosFilaF2, args=())
    fio3.daemon = True
    fio3.start()  # inicia thread que trata elementos da fila F2
    
    fio4 = Thread(target=trataComandosFilaF3, args=())
    fio4.daemon = True
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
