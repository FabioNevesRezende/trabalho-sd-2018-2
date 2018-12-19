# -*- coding: utf-8 -*-
from concurrent import futures
from comum import *
import datetime
import io
import shutil
import queue

from banco_de_dadosproxy import BancoDeDados as IBD

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

online = True # status do servidor online/offline

class GrpcInterface(interface_pb2_grpc.ManipulaMapaServicer):
    def __init__(self, confServidor):
        self.configs = Configs()

        self.posicoes = 3
        self.processes = []
        self.subirReplicas()

        self.filaComandos   = Fila() # fila F1 especificada nos requisitos
        self.filaExecucao   = Fila() # fila F2 especificada nos requisitos
        self.filaRoteamento = Fila()

        self.comecaThreadFilaComandos()
        self.comecaThreadFilaExecucao()
        self.comecaThreadFilaRoteamento()

        super()

    def subirReplicas(self):
        #recupera todos os endereços(ip:porta) de acordo com a quantidade de replicas
        paths = ["{}:{}{}".format(IP_SOCKET, self.configs.id, i) for i in range(self.posicoes)]
        #define a primeira replica
        pathInicial = paths[0]
        #criar a replica 1
        print 'cria replica: {}'.format(pathInicial)
        p = subprocess.Popen(['concoord', 'replica','-o', 'concoord.object.counter.Counter','-a', pathInicial.split(':')[0], '-p', pathInicial.split(':')[1]])
        self.processes.append(p)
        #TODO: As replicas não estão encontrando os objeto do banco
        # for path in paths: 
        #     if path != pathInicial:
        #         ip = path.split(':')[0]
        #         porta = path.split(':')[1]
        #         #criar as n replicas
        #         print 'cria replica: {}'.format(path)
        #         p = subprocess.Popen(['concoord', 'replica', '-o', 'banco_de_dados.BancoDeDados', '-b', pathInicial,'-a', ip, '-p', porta])
        #         self.processes.append(p)
        self.instanciaIterfaceBanco([pathInicial])
        

    def instanciaIterfaceBanco(self, paths):
        self.bd = IBD(','.join(paths))
        
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
    
    def DeletaItem(self, request, context):
        return self.trataRequisicao(comandos['delete'], request.chave, request.valor, context)

    def AtualizaItem(self, request, context):
        return self.trataRequisicao(comandos['update'], request.chave, request.valor, context)

    def LeItem(self, request, context):
        return self.trataRequisicao(comandos['read'], request.chave, request.valor, context)

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
                _comando, chave, _valor = req
                validacao = self.configs.valida_chave(chave)
                if validacao[0]:
                    self.filaExecucao.enfileira((req, fila))
                else:
                    printa_neutro("Chave {} não pertence a mim. Roteando para {}".format(chave, validacao[1]))
                    self.filaRoteamento.enfileira((req, fila, validacao[1]))

    def trataFilaExecucao(self):
        while online:
            while self.filaExecucao.tamanho() > 0:
                req, filaResposta     = self.filaExecucao.desenfileira()
                comando, chave, valor = req
                resposta = self.defineComandoAExecutar(comando, chave, valor)
                resposta = resposta.encode()
                filaResposta.put(interface_pb2.status(resposta=resposta))

    def trataFilaRoteamento(self):
        while online:
            while self.filaRoteamento.tamanho() > 0:
                req, filaResposta, servidor = self.filaRoteamento.desenfileira()
                comando, c, v = req
                resposta      = None

        # TODO: corrigir roteamento

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

        # Thread que pega os comandos e os loga
    
    def cria_stub(self, servidor):
        endereco = '{}:{}{}'.format(IP_SOCKET, PREFIXO_PORTA, servidor)
        channel  = grpc.insecure_channel(endereco)
        return interface_pb2_grpc.ManipulaMapaStub(channel)

    # Cria um novo item e o adiciona à lista
    def criaItem(self, chave, valor):
        return IBD.criaItem(chave, valor)

    # Atualiza um item, caso exista
    def atualizaItem(self, chave, valor):
        return IBD.atualizaItem(chave, valor)

    # Remove um item, caso exista
    def removeItem(self, chave):
        return IBD.removeItem(chave)
        
    # Lê um item e o retorna a conexão, caso exista
    def leItem(self, chave):
        return 
   
    def encerraServidor(self):
        global online
        printa_negativo('Encerrando aplicação =(')
        online = False

    def defineComandoAExecutar(self, comando, chave, valor):
        resposta = None
        if comando == comandos['create']:
            resposta = self.criaItem(chave, valor)
        if comando == comandos['update']:
            resposta = self.atualizaItem(chave,valor)
        if comando == comandos['delete']:
            resposta = self.removeItem(chave) 
        if comando == comandos['read']:
            resposta = self.leItem(chave)
        return resposta


# inicia o servidor TCP no endereço IP_SOCKET e na porta PORTA_SOCKET
def iniciaServidor(args):
    configs  = configura_servidor(args)
    endereco = '[::]:{}{}'.format(PREFIXO_PORTA, configs.id)

    printa_neutro('Escutando no endereço: {}\n'.format(endereco))

    executor = futures.ThreadPoolExecutor(max_workers=10, 
                                          thread_name_prefix='Main')
    server   = grpc.server(executor)

    interface_pb2_grpc.add_ManipulaMapaServicer_to_server(GrpcInterface(configs), server)
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
        printa_negativo('Erro ao rodar servidor: ')
        printa_negativo(str(e))
        # traceback.print_exc()
        input()
