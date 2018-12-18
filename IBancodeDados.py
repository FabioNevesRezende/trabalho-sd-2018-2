# -*- coding: utf-8 -*-
from comum import ItemMapa

class IBancodeDados:
    def __init__(self):
        self.itensMapa = []

    def criaItem(self, chave, valor):
        if  self.temItem(chave) == None:
            self.itensMapa.append(ItemMapa(chave, valor))
            msg = 'Ok - Item criado.'
            # printa_positivo(msg)
            print (msg)
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
            print (msg)
        else:
            msg = 'NOk - Chave inexistente.'
            print (msg)
        return msg

    # Lê um item e o retorna a conexão, caso exista
    def leItem(self, chave):
        index = self.temItem(chave)
        if not index==None:
            msg = str('Ok - Item: ' + self.itensMapa[index].serializa())
            print(msg)
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
            print(msg)
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

# def main():
#     tst = IBancodeDados()
#     tst.criaItem(1,'nicolas')
#     tst.leItem(1)


# if __name__ == "__main__":
#     main()