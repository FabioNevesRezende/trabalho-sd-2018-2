from concoord.clientproxy import ClientProxy
from comum import ItemMapa

class BancoDeDados:

    def __init__(self, bootstrap):
        self.proxy = ClientProxy(bootstrap, token='None')

    def __concoordinit__(self):
        return self.proxy.invoke_command('__concoordinit__')

    def criaItem(self, chave, valor):
        return self.proxy.invoke_command('criaItem', chave, valor)

    def atualizaItem(self, chave, valor):
        return self.proxy.invoke_command('atualizaItem', chave, valor)

    def leItem(self, chave):
        return self.proxy.invoke_command('leItem', chave)

    def removeItem(self, chave):
        return self.proxy.invoke_command('removeItem', chave)

    def temItem(self, chave):
        return self.proxy.invoke_command('temItem', chave)