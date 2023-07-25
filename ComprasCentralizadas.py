#!/usr/bin/python3
# Lista de empresas com CNAE de venda de SW
# https://compras.dados.gov.br/fornecedores/v1/fornecedores.csv?id_cnae=6203100

# Lista de empresas com CNAE de serviços de nuvem
# https://compras.dados.gov.br/fornecedores/v1/fornecedores.csvl?id_cnae=6311900

# Contratos de um CNPJ
# http://compras.dados.gov.br/comprasContratos/v1/contratos.html?fornecedor_cnpj_cpf_idgener=00.103.115/0001-01

import requests
import json
import pandas as pd
import os
import sys


base_url = 'https://compras.dados.gov.br'
fornecedor_base_page_url = '/fornecedores/v1/fornecedores.json?id_cnae='
contratos_base_page_url = '/comprasContratos/v1/contratos.json?fornecedor_cnpj_cpf_idgener='
fornecedores = []
contratos = []

# Verifica se existem mais paginas e apenda conteudo no json fornecedores
def AnexaProximasPaginas(links):
    print("Pagina Adicional Encontrada. Navegando.")
    global fornecedores
    fornecedor_next_page_url = links['next']['href']

    response = requests.get(base_url+fornecedor_next_page_url, timeout=30)
    if response.status_code == 200:
        resp_dict = response.json()
    else:
        print("Error from server: " + str(response.content))
        return

    temp = resp_dict['_embedded']['fornecedores']
    fornecedores = fornecedores + temp

    links = resp_dict['_links']
    if "next" in links:
        AnexaProximasPaginas(links)
    return


#Gera lista detalhada de contratos por CNPJ
def ConsultaContratos(fornecedor,cnae):
    cnpj = fornecedor['cnpj']
    if not os.path.exists("./"+cnae+'/'+cnpj+".csv"):
        cnpj_fmt =  '{}.{}.{}/{}-{}'.format(cnpj[:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:])  
        response = requests.get(base_url+contratos_base_page_url+cnpj_fmt, timeout=30)
        if response.status_code == 200:
            resp_dict = response.json()
        else:
            print("Error from server: " + str(response.content))
            return
        contratos = resp_dict['_embedded']['contratos']

        links = resp_dict['_links']
        if "next" in links:
            print("MAIS DE 500 CONTRATOS PARA O CNPJ INDICADO!!!")

        print("Total de Contratos para cnpj "+cnpj_fmt+": "+str(len(contratos)))
        df = pd.json_normalize(contratos)
        if len(contratos) > 0:
            if not os.path.exists(cnae):
                os.mkdir(cnae)
            df.to_csv(cnae+'/'+cnpj+'.csv', sep="|")
    return


def ListaFornecedores(cnae):
    global fornecedores
    response = requests.get(base_url+fornecedor_base_page_url+cnae, timeout=30)
    if response.status_code == 200:
        resp_dict = response.json()
    else:
        print("Error from server: " + str(response.content))
        return

    fornecedores = resp_dict['_embedded']['fornecedores']
    links = resp_dict['_links']

    if "next" in links:
        AnexaProximasPaginas(links)

    print("Quantidade de fornecedores para o CNAE:" + str(len(fornecedores)))

    for fornecedor in fornecedores:
        try:
            ConsultaContratos(fornecedor,cnae)
        except Exception as e:
            print("Erro na leitura do JSON")
    return


file_cnae = open('cnae.txt', 'r')
lines = file_cnae.readlines()

for line in lines:
    cnae = line.strip()
    print(cnae)
    print("Processando CNAE: "+cnae)
    ListaFornecedores(cnae)
    print("Fim CNAE:"+cnae)

print("Fim de processamento.")

