def createToRecovery():
    servidores = open('./servidores.txt', 'r')
    listaServidor = []
    for linha in servidores.readlines():
        listaServidor.append(int(linha))
    return listaServidor

def main():
    print(createToRecovery())

if __name__ == '__main__':
    main()
