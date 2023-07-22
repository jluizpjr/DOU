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

base_url = 'https://compras.dados.gov.br'
fornecedor_base_page_url = '/fornecedores/v1/fornecedores.json?id_cnae=6203100'
contratos_base_page_url = '/comprasContratos/v1/contratos.json?fornecedor_cnpj_cpf_idgener='
fornecedores = []
contratos = []

# Verifica se existem mais paginas e apenda conteudo no json fornecedores
def AnexaProximasPaginas(links):

    if "next" in links:
        global fornecedores
        fornecedor_next_page_url = links['next']['href']
        response = requests.get(base_url+fornecedor_next_page_url)
        resp_dict = response.json()
        temp = resp_dict['_embedded']['fornecedores']
        fornecedores = fornecedores + temp
        AnexaProximasPaginas(resp_dict['_links'])
    return 

#Gera lista detalhada de contratos por CNPJ
def ConsultaContratos(fornecedor):
    global contratos
    cnpj = fornecedor['cnpj']
    if os.path.exists("./"+cnpj+".csv"):
        cnpj_fmt =  '{}.{}.{}/{}-{}'.format(cnpj[:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:])  
        response = requests.get(base_url+contratos_base_page_url+cnpj_fmt)
        resp_dict = response.json()
        print("Contratos: "+str(len(resp_dict['_embedded']['contratos'])))
        temp = resp_dict['_embedded']['contratos']
        contratos = contratos + temp
        print("Total de Contratos: "+str(len(contratos)))
        #df = pd.read_json(contratos, orient='records')
        df = pd.json_normalize(contratos)
        df.to_csv(cnpj+'.csv')
        print(df)
    return


response = requests.get(base_url+fornecedor_base_page_url)
resp_dict = response.json()
fornecedores = resp_dict['_embedded']['fornecedores']
AnexaProximasPaginas(resp_dict['_links'])


for fornecedor in fornecedores:
    print(fornecedor['nome'])
    try:
        ConsultaContratos(fornecedor)
    except Exception as e:
        print("Erro na leitura do JSON")


