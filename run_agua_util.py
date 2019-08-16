import f90nml
import datetime as dt
import pandas as pd
import numpy as np
import os
import time
############

from AguaUtil import proccessing_decadal
from AguaUtil import processing_departamento
from AguaUtil import processing_cuartel
##############################
start_time = time.time()

nml = f90nml.read('./namelist.agua_util')
# Cambiar fecha para cada vez que se corre, colocando dia inicial decada
deca = nml['config_au']['deca']
path = nml['config_au']['carpeta_bal']
opath = nml['config_au']['carpeta_ppal']
deca_folder = nml['config_au']['carpeta_deca']
calculo_por = nml['config_au']['calculo_por']
# Sin el punto que viene por default
infile = './' + nml['config_au']['file_ind']
ind_clt = pd.read_csv(infile, sep=';')
cultivos1 = ind_clt['clt'].loc[ind_clt[deca[5::]]==1].tolist()
cultivos2 = ind_clt['clt_file'].loc[ind_clt[deca[5::]]==1].tolist()
# -----  hasta aca se modifican los valores del usuario ------
# Se crea carpetas
os.makedirs(opath, exist_ok=True)
os.makedirs(deca_folder, exist_ok=True)
# Comenzamos a trabajar en todas las resoluciones y cultivos de la fecha
if calculo_por == 'cuartel':
    bla_bla = ['50']
else:
    bla_bla = ['50', '500']
for resol in bla_bla:
    for iclt, clt_file in enumerate(cultivos2):
        print('###### Trabajando en la resolucion: ' + resol)
        print('###### Trabajando en el cultivo: ' + clt_file)
        # Datos para el LOGFILE
        fdeca = dt.datetime.strptime(deca, '%Y-%m-%d').strftime('%d%m%Y')
        fhoy = dt.datetime.today().strftime('%d%m%Y')
        lfile = opath + 'out/' + fhoy +'_' + cultivos1[iclt] + '_' + resol +\
                '_' + fdeca + '_logfile.txt'
        print('###### Archivo LOG en: ' + lfile)
        f = open(lfile, 'w')
        f.write('--------------------------------------------------\n')
        f.write('Carpeta de archivos: ' + path + '\n')
        f.write('Carpeta de salida: ' + opath + 'out/ \n')
        f.write('Carpeta de decadales: ' + deca_folder + '\n')
        f.write('--------------------------------------------------\n')
        f.close()
        # Save in array ONLY files
        lfiles = [i for i in os.listdir(path)
                  if os.path.isfile(os.path.join(path, i)) and\
                  clt_file in i]
        # Generate a summary of the Political File
        # Archivo Division Politica
        if resol == '50':
            dp_file = opath + 'Grilla50.csv'
            fdivpol = opath + 'resumen_divpol_50.csv'
            dp = pd.read_csv(dp_file, sep=';', encoding='ISO-8859-1')
            pr_dp = dp['PROVINCIA'].values.squeeze() + '-' +\
                dp['DEPTO'].values.squeeze()
            dp = dp.assign(PRDPT=pr_dp)
            dp1 = dp.groupby(['Distrito','PRDPT','centroide']).count()
            dp1.apply(pd.to_numeric, errors='ignore')
            dp1.to_csv(fdivpol, sep=';')
            print('###### Archivo resolucion: ' + fdivpol)
        elif resol == '500':
            dp_file = opath + 'Grilla500.csv'
            fdivpol = opath + 'resumen_divpol_500.csv'
            dp = pd.read_csv(dp_file, sep=';', encoding='ISO-8859-1')
            dp.columns = ['COD_PROV', 'COD_DEPTO', 'LINK', 'DEPTO', 'PROVINCIA',
                          'centroide']
            pr_dp = dp['PROVINCIA'].values.squeeze() + '-' +\
                    dp['DEPTO'].values.squeeze()
            dp = dp.assign(PRDPT=pr_dp)
            dp1 = dp.groupby(['PRDPT','centroide']).count()
            dp1.apply(pd.to_numeric, errors='ignore')
            dp1.to_csv(fdivpol, sep=';')
            print('###### Archivo resolucion: ' + fdivpol)

        # Summary of variables in dictionary python
        d = {'opath':opath, 'decafolder':deca_folder, 'pfiles':path,
             'clt':cultivos1[iclt], 'lfile':lfile, 'dpfile':dp_file,
             'divpol':fdivpol, 'resol':resol}
        # ################################################
        # Start processing daily data to decade data
        # ################################################
        print('###### Procesando ' + str(len(lfiles)) + ' archivos decadales')
        # proccessing_decadal(lfiles, d)
        # ################################################
        # Start proccessing Data of Provinces and percentages of centroid inside
        # ################################################
        if calculo_por == 'departamento':
            print('###### Procesando calculos por departamento')
            processing_departamento(d)
        elif calculo_por == 'cuartel':
            print('###### Procesando calculos por cuartel')
            processing_cuartel(d)
        print('---------------------------------------------------------------')
        # ################################################
print(u'###### Al fin termino!! ######')
print('Tiempo de demora del script:')
print("--- %s seconds ---" % (time.time() - start_time))
