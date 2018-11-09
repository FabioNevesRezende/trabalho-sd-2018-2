#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from concurrent import futures
from comum import *
import datetime
import io
import shutil
import re 

online = True # status do servidor online/offline

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

#abre arquivos temporarios de logs
try:
    logs = open('logs.log', 'r+') # r+ modo leitura e escrita ao mesmo tempo, se o arquivo não existir, ele NÃO o cria, por isso o try-catch
except FileNotFoundError:
    logs = open('logs.log', 'w') # r+ modo escrita já que é a primeira vez não tem nada a ser lido
    
class GrpcInterface(interface_pb2_grpc.ManipulaMapaServicer):
    def __init__(self):
        self.configs = Configs()

        self.itensMapa = [] # lista de elementos <bigInteger, string>

        self.filaF1    = Fila() # fila F1 especificada nos requisitos
        self.filaF2    = Fila() # fila F2 especificada nos requisitos
        self.filaF3    = Fila() # fila F3 especificada nos requisitos
        self.filaF4    = Fila() # fila F3 especificada nos requisitos

        self.ListaLogs = ManipulaArquivosLog(dirNome=DIR_LOG, index=0)
        self.ListaSnaps = ManipulaArquivosLog(dirNome=DIR_SNAP, index=1)
        self.parsaConfigIni()
        
        fio2 = Thread(target=self.trataComandosFilaF1, args=())
        fio2.daemon = True
        fio2.start()  # inicia thread que trata elementos da fila F1
        
        fio3 = Thread(target=self.trataComandosFilaF2, args=())
        fio3.daemon = True
        fio3.start()  # inicia thread que trata elementos da fila F2
        
        fio4 = Thread(target=self.trataComandosFilaF3, args=())
        fio4.daemon = True
        fio4.start()  # inicia thread que trata elementos da fila F3
        
        # logs = Thread(target=self.criaSnapshoting, args=())
        # logs.daemon = True
        # logs.start() # Inicia threa que mantém snap e logs

        super()

    def trata_retorno(self, resposta):
        return resposta.result().resposta

    def cria_stub(self, servidor):
        endereco = '{}:{}{}'.format(IP_SOCKET, PREFIXO_PORTA, servidor)
        channel  = grpc.insecure_channel(endereco)
        return interface_pb2_grpc.ManipulaMapaStub(channel)

    def CriaItem(self, request, context):
        chave = request.chave
        valor = request.valor

        validacao = self.configs.valida_chave(chave)

        if validacao[0]:
            msg = ['']
            self.criaItem(chave, valor, msg)
            return interface_pb2.status(resposta=msg[0].encode())

            # self.filaF1.enfileira((comandos['create'], chave, valor, context))
        else:
            stub = self.cria_stub(validacao[1])
            printa_neutro("Chave {} não pertence a mim. Roteando para {}".format(chave, validacao[1]))
            return stub.CriaItem(interface_pb2.msgItem(chave=chave ,valor=valor))
            # return future.add_done_callback(self.trata_retorno)
            # self.filaF4.enfileira((comandos['create'], chave, valor, context, stub))
        
    def LeItem(self, request, context):
        recebido = str(comandos['read'] + ' ' + str(request.chave) + ' ' + str(request.valor))
        # self.filaF1.enfileira(recebido)
        #return interface_pb2.status(resposta='Ok - Item criado.', itemResposta=(chave=request.chave, valor=request.valor))
        return interface_pb2.status(resposta=('Recebi de você: ' + recebido).encode())
        
    def AtualizaItem(self, request, context):
        recebido = str(comandos['update'] + ' ' + str(request.chave) + ' ' + str(request.valor))
        # self.filaF1.enfileira(recebido)
        #return interface_pb2.status(resposta='Ok - Item criado.', itemResposta=(chave=request.chave, valor=request.valor))
        return interface_pb2.status(resposta=('Recebi de você: ' + recebido).encode())
        
    def DeletaItem(self, request, context):
        recebido = str(comandos['delete'] + ' ' + str(request.chave))
        # self.filaF1.enfileira(recebido)
        #return interface_pb2.status(resposta='Ok - Item criado.', itemResposta=(chave=request.chave, valor=request.valor))
        return interface_pb2.status(resposta=('Recebi de você: ' + recebido).encode())
        
    '''
    Recria itens em memória a partir do snap
    '''
    def criaItensMapaLogs(self):
        ultimoSnap = self.ListaSnaps.listaArquivos.recuperaUltimo()
        
        if ultimoSnap != None:
            for linha in ultimoSnap.read().split('\', '):
                if(linha == '[]'):
                    break
                linha = re.sub(r'[^a-zA-Z\d\s,:]','',linha.strip())
                self.itensMapa.append(ItemMapa.desserializa(linha))
        else:
            printa_neutro('Não há nenhum log a ser lido')

    #Função para executar os métodos em memória
    def executaComandos(self, cmd, msg=[""]):
        comando = cmd.strip().split(' ')[0]
        chave   = ''

        try:
            chave = int(cmd.split(' ')[1])
        except IndexError:
            return self.leTodosItens(msg)

        if comando == comandos['create']:
            return self.criaItem(chave, cmd.strip().split(' ')[2], msg)
        if comando == comandos['update']:
            return self.atualizaItem(chave, cmd.strip().split(' ')[2], msg)
        if comando == comandos['delete']:
            return self.removeItem(chave, msg) 
        if comando == comandos['read']:
            return self.leItem(chave, msg)

    # Analisa configuração inicial 
    def parsaConfigIni(self):
        printa_neutro('Lerá arquivo de inicialização')
        # recupera o estado, se houver
        self.criaItensMapaLogs()
        printa_positivo('Terminada a leitura de arquivo de inicialização, estado atual da lista de itens: ')
        self.printaItens()

    # printa todos os itens
    def printaItens(self):
        for item in self.itensMapa:
            printa_neutro(item.serializa())

    '''
    @param: chave: Chave do item
    Verifica se o item existe no "banco"
    '''
    def temItem(self, chave):
        for elem in self.itensMapa:
            if elem.chave == chave:
                return self.itensMapa.index(elem)
        return 

    # Cria um novo item e o adiciona à lista
    def criaItem(self, chave, valor, msg=[""]):
        if  self.temItem(chave)==None:
            self.itensMapa.append(ItemMapa(chave, valor))
            msg[0] = 'Ok - Item criado.'
            printa_positivo(msg[0])
            return True
        else:
            msg[0] = 'NOk - Chave existente.'
            printa_negativo(msg[0])
            return False

    # Atualiza um item, caso exista
    def atualizaItem(self, chave, valor, msg=[""]):
        index = self.temItem(chave)
        if not index==None:
            self.itensMapa[index] = ItemMapa(chave,valor)
            msg[0] = 'Ok - Item atualizado.'
            printa_positivo(msg[0])
            return True
        else:
            msg[0] = 'NOk - Chave inexistente.'
            printa_negativo(msg[0])
            return False

    # Remove um item, caso exista
    def removeItem(self, chave, msg=[""]):
        index = self.temItem(chave)
        if not index==None:
            del self.itensMapa[index]
            msg[0] = 'Ok - Item removido.'
            printa_positivo(msg[0])
            self.printaItens()
            return True
        else:
            msg[0] = 'NOk - Chave inexistente.'
            printa_negativo(msg[0])
            return False

    # Lê um item e o retorna a conexão, caso exista
    def leItem(self,chave, msg=[""]):
        index = self.temItem(chave)
        if not index==None:
            msg[0] = str('Ok - Item: ' + self.itensMapa[index].serializa())
            printa_positivo(msg[0])
            return True
        else:
            msg[0] = 'NOk - Chave inexistente.'
            printa_negativo(msg[0])
            return False

    # Lê um item e o retorna a conexão, caso exista
    def leTodosItens(self, msg=[""]):
        if len(self.itensMapa) > 0:
            msg[0] = 'Ok - Itens: ' + str([p.serializa() for p in self.itensMapa])
            printa_positivo(msg[0])
            return True
        else:
            msg[0] = 'NOk - Banco vazio.'
            printa_negativo(msg[0])
            return False

    def loga(self, msg):
        logs.write(msg)
        logs.flush() # garante a escrita no arquivo sem ter que fechá-lo
        printa_positivo(msg + ' logada com sucesso')
        
    # Thread que pega os comandos recem chegados do cliente e despacha para as filas F2 e F3
    def trataComandosFilaF1(self):
        while online:
            while self.filaF1.tamanho() > 0:
                cmd = self.filaF1.desenfileira()
                self.filaF2.enfileira(cmd)
                self.filaF3.enfileira(cmd)
                
    # Thread que pega os comandos e os loga
    def trataComandosFilaF2(self):
        while online:
            while self.filaF2.tamanho() > 0:
                cmd = self.filaF2.desenfileira()
                if cmd[:4] != comandos['read']:
                    self.loga(cmd + '\n')
                
    # Thread que pega os comandos e os executa
    def trataComandosFilaF3(self):
        while online:
            msg = [""] #Cria uma lista com apenas um elemento que será a mensagem retonada da execução dos comandos
            while self.filaF3.tamanho() > 0:
                cmd = self.filaF3.desenfileira()            
                self.executaComandos(cmd, msg)
                # interface_pb2.status(resposta=msg[0].encode())
                # print('Lista atual:')
                # printaItens()
                
    def encerraServidor(self):
        global online
        printa_negativo('Encerrando aplicação =(')
        logs.close()
        online = False
    
    # Método que criar os arquivos de log e snapshoting
    def criaSnapshoting(self):
        while(True):
            time.sleep(SLEEP_TIME)
            snapName = self.ListaSnaps.dirNome + 'snap.{}.txt'.format(str(self.ListaSnaps.index))
            logName =  self.ListaLogs.dirNome + 'log.{}.log'.format(str(self.ListaLogs.index))
            log = open(logName, "w")#Abre arquivo de log para cria-lo
            log.close()
            shutil.copyfile('logs.log', logName)#copia o log principal para o novo log
            logs.truncate(0)#Limpa o arquivo principal de logs
            snap = open(snapName, "w")
            snap.write(str([p.serializa() for p in self.itensMapa]))
            snap.flush() # garante a escrita no arquivo sem ter que fechá-lo
            snap.close()
            self.ListaLogs.adicionaArquivo(log)
            self.ListaSnaps.adicionaArquivo(snap)
 
# inicia o servidor TCP no endereço IP_SOCKET e na porta PORTA_SOCKET
def iniciaServidor(args):
    configs  = configura_servidor(args)
    endereco = '[::]:{}{}'.format(PREFIXO_PORTA, configs.id)

    printa_neutro('Escutando no endereço: {}\n'.format(endereco))

    server  = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    interface_pb2_grpc.add_ManipulaMapaServicer_to_server(GrpcInterface(), server)
    server.add_insecure_port(endereco)
    server.start()

    try:
        while online:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

    server.stop(0)

# Main e ponto de inicio da aplicação
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("id", 
        help="Identificador do servidor", 
        type=int)
    parser.add_argument("anterior", 
        help="Identificador do servidor anterior", 
        type=int)
    parser.add_argument("posterior", 
        help="Identificador do servidor posterior", 
        type=int)

    args = parser.parse_args()

    iniciaServidor(args)
    
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logs.close()
        printa_negativo('Erro ao rodar servidor: ')
        printa_negativo(str(e))
        traceback.print_exc()
        input()
