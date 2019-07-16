import os
import pandas as pd
import numpy as np
import datetime as dt
import calendar

import matplotlib
import matplotlib.pyplot as plt


def get_file_data_old(archivo):
    """
    Separa del nombre del archivo y extrae nombre de Centroide (ctrd)
    y cultivo (clt)
    """
    diccionario = {}
    listado = archivo.split('-')
    diccionario['ctrd'] = listado[0]
    condicion = 'TS(S2)' in listado[1] or\
                'TS(TC)' in listado[1] or\
                'TL' in listado[1] or\
                'TS(TL)' in listado[1]
    if '.' in listado[1]:
        if 'P.txt' in listado[1]:
            diccionario['clt'] = listado[1].split('.')[0]
        elif condicion:
            diccionario['clt'] = listado[1].split('.')[0]
        else:
            diccionario['clt'] = listado[1].split('.')[0] + listado[1].split('.')[1]
    elif 'S1-V' in archivo:
        diccionario['clt'] = listado[1] + '-' + listado[2].split('.')[0]
    else:
        diccionario['clt'] = 'QUE'
    return diccionario

def get_file_data(archivo):
    """
    Separa del nombre del archivo y extrae nombre de Centroide (ctrd)
    y cultivo (clt)
    """
    diccionario = {}
    l0 = archivo.split('.')  # ultimo valor es 'txt'
    str1 = ''.join(l0[:-1])  # Elimina los puntos (e.g M1.1 queda M11)
    l1 = str1.split('-')  # el ultimo debiera ser el cultivo
    diccionario['ctrd'] = '-'.join(l1[:-1])
    diccionario['clt'] = l1[-1]

    return diccionario

opath = 'e:/python/AguaUtil/'
lpath = 'e:/python/AguaUtil/Balances/Balance1970/'
dfile = 'Grilla500.csv'
dp_file = opath + dfile
dp = pd.read_csv(dp_file, sep=';', encoding='ISO-8859-1')
pr_dp = dp['PROVINCIA'].values.squeeze() + '-' +\
        dp['DEPTO'].values.squeeze()
dp = dp.assign(PRDPT=pr_dp)
dp3 = dp.groupby(['PRDPT','Ctrde_ID']).count()
print(dp.head(10))
print(dp3)

lfiles = [i for i in os.listdir(lpath)
         if os.path.isfile(os.path.join(lpath, i)) and\
         'TS(TC)' in i]
f = open(opath + 'test_read_files.txt', 'w')
for nfile in lfiles:
    f.write(nfile + '\n')
    dic = get_file_data(nfile)
    f.write(dic['ctrd'] + '\n')
f.close()
