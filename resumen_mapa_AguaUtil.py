import os
import pandas as pd
import numpy as np
import datetime as dt
import calendar


def get_xlsfile_data(n_file):
    """
    Extrae provincia, departamento, cultivo del nombre de archivo
    """
    diccionario = {}
    lst = n_file.split('.')[0]
    diccionario['Prov'] = lst.split('_')[0].split('-')[0]
    diccionario['Dpto'] = lst.split('_')[0].split('-')[1]
    diccionario['clt'] = lst.split('_')[1]
    return diccionario

# ---- Cambiar para la corrida
resol = '500'  # Resolucion
# Carpeta salida x Dpto y Cultivo
p_out = 'e:/python/AguaUtil/out/'
ipath = p_out + resol + '_' + '01072019_out/'
# --------------------- Start Code ---------------------------------------
if resol == '500':
    dp_file = 'e:/python/AguaUtil/Grilla500.csv'  # cambiar si resol = 500
elif resol == '50':
    dp_file = 'e:/python/AguaUtil/Grilla50.csv'  # cambiar si resol = 500
lfiles = [i for i in os.listdir(ipath)
         if os.path.isfile(os.path.join(ipath, i))]
dp = pd.read_csv(dp_file, sep=';', encoding='ISO-8859-1')
resumen = pd.DataFrame(columns=['Fecha', 'Prov', 'Depto', 'LINK',
                                'AU_WGT', 'Cultivo'])
for nfile in lfiles:
    dlt = get_xlsfile_data(nfile)
    df = pd.read_excel(ipath + nfile)
    ul = df[['Fecha', 'AU_WGT']].iloc[-1]
    fecha = ul.Fecha
    a = dp[np.logical_and(dp['PROVINCIA'] == dlt['Prov'],
                          dp['DEPTO'] == dlt['Dpto'])]
    link = a['LINK'].iloc[0]
    b = {'Fecha':fecha, 'Prov':dlt['Prov'], 'Depto':dlt['Dpto'], 'LINK':link,
         'AU_WGT':ul.AU_WGT, 'Cultivo':dlt['clt'] }
    resumen = resumen.append(b, ignore_index=True)
# Guardamos excel con resultado
nombre = p_out + resol + '_' + fecha.strftime('%Y%m%d') + '_resumen_AU.xlsx'
resumen.to_excel(nombre, sheet_name='Resumen Agua Util')
