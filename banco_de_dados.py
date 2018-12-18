# -*- coding: utf-8 -*-
from comum import ItemMapa

class BancoDeDados:
    def __init__(self):
        self.itensMapa = []

    def criaItem(self, chave, valor):
        if  self.temItem(chave) == None:
            self.itensMapa.append(ItemMapa(chave, valor))
            msg = 'Ok - Item criado.'
        else:
            msg = 'NOk - Chave existente.'
        
        print (msg)
        return msg

    # Atualiza um item, caso exista
    def atualizaItem(self, chave, valor):
        index = self.temItem(chave)
        if not index==None:
            self.itensMapa[index] = ItemMapa(chave,valor)
            msg = 'Ok - Item atualizado.'
        else:
            msg = 'NOk - Chave inexistente.'

        print (msg)
        return msg

    # Lê um item e o retorna a conexão, caso exista
    def leItem(self, chave):
        index = self.temItem(chave)
        if not index==None:
            msg = str('Ok - Item: ' + self.itensMapa[index].serializa())
        else:
            msg = 'NOk - Chave inexistente.'

        print(msg)
        return msg

    # Remove um item, caso exista
    def removeItem(self, chave):
        index = self.temItem(chave)
        if not index==None:
            del self.itensMapa[index]
            msg = 'Ok - Item removido.'
        else:
            msg = 'NOk - Chave inexistente.'
        
        print(msg)
        return msg

    def temItem(self, chave):
        '''
            @param: chave: Chave do item
            Verifica se o item existe no "banco"
        '''
        for elem in self.itensMapa:
            if elem.chave == chave:
                return self.itensMapa.index(elem)
        return 