#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from concurrent import futures
from comum import *
import datetime
import io
import shutil
import re 
import queue

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

        self.filaComandos   = Fila() # fila F1 especificada nos requisitos
        self.filaExecucao   = Fila() # fila F2 especificada nos requisitos
        self.filaRoteamento = Fila()
        self.filaLogs       = Fila()

        self.comecaThreadFilaComandos()
        self.comecaThreadFilaExecucao()
        self.comecaThreadFilaRoteamento()

        # fio4 = Thread(target=self.trataFilaComandos, args=())
        # fio4.daemon = True
        # fio4.start()  # inicia thread que trata elementos da fila F3

        
        # logs = Thread(target=self.criaSnapshoting, args=())
        # logs.daemon = True
        # logs.start() # Inicia threa que mantém snap e logs

        super()

    def comecaThreadFilaComandos(self):
        trataFilaComandos = Thread(target=self.trataFilaComandos, args=())
        trataFilaComandos.daemon = True
        trataFilaComandos.name   = 'ThreadFilaComandos'
        trataFilaComandos.start()  # inicia thread que trata elementos da fila F1

    def comecaThreadFilaExecucao(self):
        trataFilaExecucao = Thread(target=self.trataFilaExecucao, args=())
        trataFilaExecucao.daemon = True
        trataFilaExecucao.name   = 'ThreadFilaExecucao'
        trataFilaExecucao.start()  # inicia thread que trata elementos da fila F2

    
    def comecaThreadFilaRoteamento(self):
        trataFilaRoteamento = Thread(target=self.trataFilaRoteamento, args=())
        trataFilaRoteamento.daemon = True
        trataFilaRoteamento.name   = 'ThreadFilaRoteamento'
        trataFilaRoteamento.start()  # inicia thread que trata elementos da fila F3

    def CriaItem(self, request, context):
        return self.trataRequisicao(comandos['create'], request.chave, request.valor, context)

    def trataRequisicao(self, comando, chave, valor, _context):
        req          = (comando, chave, valor)
        filaResposta = queue.Queue()

        self.filaComandos.enfileira((req, filaResposta))

        resposta = filaResposta.get()

        del filaResposta

        return resposta

    def trataFilaComandos(self):
        while online:
            while self.filaComandos.tamanho() > 0: # req + 
                req, fila = self.filaComandos.desenfileira() # req + filaResposta
                self.filaLogs.enfileira(req)
                self.filaExecucao.enfileira((req, fila))

    def trataFilaExecucao(self):
        while online:
            while self.filaExecucao.tamanho() > 0:
                req, filaResposta     = self.filaExecucao.desenfileira()
                comando, chave, valor = req

                validacao = self.configs.valida_chave(chave)
                resposta  = None

                if validacao[0]:
                    if comando == comandos['create']:
                        resposta = self.criaItem(chave, valor)
                    if comando == comandos['update']:
                        resposta = self.atualizaItem(chave,valor)
                    if comando == comandos['delete']:
                        resposta = self.removeItem(chave) 
                    if comando == comandos['read']:
                        resposta = self.leItem(chave)

                    resposta = resposta.encode()

                    filaResposta.put(interface_pb2.status(resposta=resposta))
                else:
                    printa_neutro("Chave {} não pertence a mim. Roteando para {}".format(chave, validacao[1]))
                    self.filaRoteamento.enfileira((req, filaResposta, validacao[1]))


    def trataFilaRoteamento(self):
        while online:
            while self.filaRoteamento.tamanho() > 0:
                req, filaResposta, servidor = self.filaRoteamento.desenfileira()
                comando, c, v = req
                resposta      = None

                stub = self.cria_stub(servidor)

                if comando == comandos['create']:
                    resposta = stub.CriaItem(interface_pb2.msgItem(chave=c ,valor=v))
                if comando == comandos['update']:
                    resposta = stub.AtualizaItem(interface_pb2.msgItem(chave=c ,valor=v))
                if comando == comandos['delete']:
                    resposta = stub.DeletaItem(interface_pb2.msgItem(chave=c))
                if comando == comandos['read']:
                    resposta = stub.LeItem(interface_pb2.msgItem(chave=c))

                filaResposta.put(resposta)

    def cria_stub(self, servidor):
        endereco = '{}:{}{}'.format(IP_SOCKET, PREFIXO_PORTA, servidor)
        channel  = grpc.insecure_channel(endereco)
        return interface_pb2_grpc.ManipulaMapaStub(channel)

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
    def criaItem(self, chave, valor):
        if  self.temItem(chave) == None:
            self.itensMapa.append(ItemMapa(chave, valor))
            msg = 'Ok - Item criado.'
            printa_positivo(msg)
        else:
            msg = 'NOk - Chave existente.'
            printa_negativo(msg)

        return msg

    # Atualiza um item, caso exista
    def atualizaItem(self, chave, valor):
        index = self.temItem(chave)
        if not index==None:
            self.itensMapa[index] = ItemMapa(chave,valor)
            msg = 'Ok - Item atualizado.'
            printa_positivo(msg)
        else:
            msg = 'NOk - Chave inexistente.'
            printa_negativo(msg)

        return msg

    # Remove um item, caso exista
    def removeItem(self, chave):
        index = self.temItem(chave)
        if not index==None:
            del self.itensMapa[index]
            msg = 'Ok - Item removido.'
            printa_positivo(msg)
        else:
            msg = 'NOk - Chave inexistente.'
            printa_negativo(msg)
        
        return msg

    # Lê um item e o retorna a conexão, caso exista
    def leItem(self, chave):
        index = self.temItem(chave)
        if not index==None:
            msg = str('Ok - Item: ' + self.itensMapa[index].serializa())
            printa_positivo(msg)
        else:
            msg = 'NOk - Chave inexistente.'
            printa_negativo(msg)
        
        return msg
   
    def encerraServidor(self):
        global online
        printa_negativo('Encerrando aplicação =(')
        logs.close()
        online = False

# inicia o servidor TCP no endereço IP_SOCKET e na porta PORTA_SOCKET
def iniciaServidor(args):
    configs  = configura_servidor(args)
    endereco = '[::]:{}{}'.format(PREFIXO_PORTA, configs.id)

    printa_neutro('Escutando no endereço: {}\n'.format(endereco))

    executor = futures.ThreadPoolExecutor(max_workers=10, thread_name_prefix='Main')
    server   = grpc.server(executor)

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
