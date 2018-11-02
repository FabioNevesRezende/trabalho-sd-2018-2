#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import yaml

CONFIGS = yaml.load(open('configs.yml', 'r'))

def salva_servidores(servidores):
    with open("servidores.txt", "+w") as file:
        file.write("\n".join(map(str, servidores)))

def calcula_faixas(m, n):
    dois_a_m = 2 ** m
    divisor  = dois_a_m // n
    primeiro = dois_a_m - 1
    faixas   = list(range(primeiro, -1, -divisor))
    return faixas

def inicia_servidor(atual, ant, post):
    comando = "{} -e '{} servidor.py {} {} {}' &".format(
        CONFIGS['BASH'], CONFIGS['PYTHON'], atual, ant, post) # DETACHED
    os.system(comando)

def inicia_servidores(m, n):
    servidores = calcula_faixas(m, n)
    salva_servidores(servidores)

    for srv in range(n):
        atual = servidores[srv]
        ant   = servidores[srv - 1]
        post  = servidores[srv + 1]
        inicia_servidor(atual, ant, post)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bits", 
        help="m-bits para chave (M)", 
        type=int)
    parser.add_argument("servers", 
        help="quantidade de servidores (N)", 
        type=int)

    args = parser.parse_args()
    inicia_servidores(m=args.bits, n=args.servers)

if __name__ == '__main__':
    main()
