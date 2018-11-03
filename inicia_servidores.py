#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import yaml
from itertools import cycle

CONFIGS = yaml.load(open('configs.yml', 'r'))

def salva_servidores(servidores):
    caminho = CONFIGS['SERVIDORES']
    with open(caminho, "+w") as file:
        file.write("\n".join(map(str, servidores)))

def salva_parametros(params):
    caminho = CONFIGS['DB_PARAMS']
    yaml.dump(params, open(caminho, "+w"), default_flow_style=False)

def tem_resto(a, b):
    return True if a % b > 0 else False

def calcula_faixas(m, n):
    dois_a_m = 2 ** m
    divisor  = dois_a_m // n
    primeiro = divisor if tem_resto(dois_a_m, n) else divisor - 1

    faixas = list(range(primeiro, dois_a_m, divisor))
    limite = dois_a_m - 1
    ultimo = faixas[n - 1]

    if ultimo < limite:
        faixas[n - 1] = limite

    return faixas

def inicia_servidor(atual, ant, post):
    geometry = ''

    if CONFIGS['BASH'].startswith('xfce'):
        geometry = '--geometry 60x10'

    comando_python = '{} servidor.py {} {} {}'.format(CONFIGS['PYTHON'], atual, 
        ant, post)

    comando = "{} -e '{}' {} &".format(CONFIGS['BASH'], comando_python, 
        geometry) # DETACHED

    os.system(comando)

def inicia_servidores(m, n):
    servidores = calcula_faixas(m, n)
    salva_servidores(servidores)

    for srv in range(n):
        atual = servidores[srv]
        ant   = servidores[srv - 1]

        try:
            post = servidores[srv + 1]
        except IndexError:
            post = servidores[0]

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

    salva_parametros(vars(args))
    inicia_servidores(m=args.bits, n=args.servers)

if __name__ == '__main__':
    main()
