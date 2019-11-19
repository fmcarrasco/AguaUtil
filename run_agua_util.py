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
from AguaUtil import verifica_fecha
from AguaUtil import get_file_data
from AguaUtil import get_divpol_file
##############################

start_time = time.time()

fhoy = dt.datetime.today().strftime('%Y%m%d%H%M')

nml = f90nml.read('./namelist.agua_util')
# Cambiar fecha para cada vez que se corre, colocando dia inicial decada
deca = nml['config_au']['deca']
dt_deca = dt.datetime.strptime(deca, '%Y-%m-%d')
cult_si = nml['config_au']['todos_cult']
cult_esp = nml['config_au']['espec_cult']
path = nml['config_au']['carpeta_bal']
opath = nml['config_au']['carpeta_ppal']
deca_folder = nml['config_au']['carpeta_deca']
ret_folder = nml['config_au']['carpeta_ret']
out_folder = nml['config_au']['carpeta_out']
ret_f50 = nml['config_au']['archivo_ret'][0]
ret_f500 = nml['config_au']['archivo_ret'][1]
calcula_deca = nml['config_au']['calcula_deca']
calculo_por = nml['config_au']['calculo_por']
nm_debug = nml['config_au']['nm_debug']
if nm_debug == 'SI':
    debug = True
    print('Modo Debugging!!')
else:
    debug = False
# ----------------------------------------
# Verificacion si la fecha indicada se puede calcular
lfiles = [i for i in os.listdir(path)
          if os.path.isfile(os.path.join(path, i))]
file_balance = path + lfiles[0]
verificador = verifica_fecha(file_balance, dt_deca)
if verificador:
    print('Para la fecha indicada se puede calcular el valor decadico.')
else:
    print('ERROR: NO se puede calcular el valor decadico para la fecha indicada.')
    print('Puede ser debido a que:')
    print('a) La fecha NO se encuentra en los balances.')
    print('o')
    print('b) No estan los 10/11 valores necesarios para calcular medias decadicos.')
    exit()
# ---------------------------------------
# Seleccion de los cultivos a trabajar
infile = './' + nml['config_au']['file_ind']
ind_clt = pd.read_csv(infile, sep=';')
if cult_si == 'SI':
    cultivos1 = ind_clt['clt'].tolist()
    cultivos2 = ind_clt['clt_file'].tolist()
    print('Se va a trabajar sobre TODOS los cultivos')
    print(cultivos2)
elif cult_si == 'UNO':
    if cult_esp == 'P':
        cultivos1 = [cult_esp]
        cultivos2 = ['-' + cult_esp + '.']
    elif cult_esp == 'CN':
        cultivos1 = [cult_esp]
        cultivos2 = ['-' + cult_esp + '.']
    else:
        cultivos1 = ind_clt['clt'].loc[ind_clt['clt'] == cult_esp].tolist()
        cultivos2 = ind_clt['clt_file'].loc[ind_clt['clt'] == cult_esp].tolist()
    print('Se va a trabajar sobre el siguiente cultivo: ')
    print(cultivos1)
    print(cultivos2)
else:
    cultivos1 = ind_clt['clt'].loc[ind_clt[deca[5::]] == 1].tolist()
    cultivos2 = ind_clt['clt_file'].loc[ind_clt[deca[5::]] == 1].tolist()
    print('Se va a trabajar sobre los siguientes cultivos: ')
    print(cultivos2)
# ----------------------------------------

# ----------------------------------------
# Se generan las carpetas para guardar las salidas
os.makedirs(opath, exist_ok=True)
os.makedirs(deca_folder, exist_ok=True)
# Se generan carpetas si se trabaja por CUARTEL o DEPARTAMENTO
if calculo_por == 'cuartel':
    # Mensajes
    print('Los calculos se van a hacer por CUARTEL.')
    print('Resolucion: 50; Reticula: ' + ret_folder + ret_f50)
    #
    bla_bla = ['50']
    salida_50 =  out_folder + 'cuartel_50_' + dt_deca.strftime('%Y%m%d') +\
                '_' + fhoy + '/'
    salida_500 =  ''
    os.makedirs(salida_50, exist_ok=True)
else:
    # Mensajes
    print(' ----- Los calculos se van a hacer por DEPARTAMENTO. ----')
    print(' ----- Resolucion: 50; Reticula: ' + ret_folder + ret_f50 + ' ----')
    print(' ----- Resolucion: 500; Reticula: ' + ret_folder + ret_f500 + ' ----')
    #
    bla_bla = ['50', '500']
    #bla_bla = ['50']
    salida_50 =  out_folder + '50_' + dt_deca.strftime('%Y%m%d') +\
                '_' + fhoy + '/'
    salida_500 =  out_folder + '500_' + dt_deca.strftime('%Y%m%d') +\
                '_' + fhoy + '/'
    os.makedirs(salida_50, exist_ok=True)
    os.makedirs(salida_500, exist_ok=True)
# ----------------------------------------------
#fdivpol = get_divpol_file('50', ret_folder, ret_f50, ret_f500)
#exit()
# ----------------------------------------------
# Comenzamos a iterar por resolucion y cultivo asignado
for resol in bla_bla:
    for iclt, clt_file in enumerate(cultivos2):
        print('###### Trabajando en la resolucion: ' + resol + ' ########')
        print('###### Trabajando en el cultivo: ' + clt_file + ' ########')
        # Datos para el LOGFILE
        fdeca = dt_deca.strftime('%Y%m%d')
        lfile = opath + 'out/' + fhoy +'_' + cultivos1[iclt] + '_' + resol +\
                '_' + fdeca + '_logfile.txt'
        print('###### Archivo LOG en: ' + lfile + ' ########')
        f = open(lfile, 'w')
        f.write('--------------------------------------------------\n')
        f.write('Carpeta de archivos: ' + path + '\n')
        f.write('Carpeta de salida 50: ' + salida_50 + ' \n')
        f.write('Carpeta de salida 500:' + salida_500 + ' \n')
        f.write('Carpeta de decadales: ' + deca_folder + '\n')
        if resol == '50':
            f.write('Archivo con datos Division Politica: ' + ret_f50 + '\n')
        elif resol == '500':
            f.write('Archivo con datos Division Politica: ' + ret_f500 + '\n')
        f.write('--------------------------------------------------\n')
        f.close()
        # Save in array ONLY files
        lfiles = [i for i in os.listdir(path)
                  if os.path.isfile(os.path.join(path, i)) and\
                  clt_file in i]
        if debug:
            print('Aca estoy debuggeando')
            ftexto = open('./prueba_archivos.txt', 'w')
            ftexto.write('--------------------------------------------------\n')
            for arc in lfiles:
                f_d = get_file_data(arc)
                ftexto.write('Archivo: ' + arc + '\n')
                ftexto.write('Centroide: ' + f_d['ctrd'] + '\n')
                ftexto.write('Cultivo: ' + f_d['clt'] + '\n')
                ftexto.write('--------------------------------------------------\n')
            ftexto.close()
            break
        # Generate a summary of the Political File
        # Archivo Division Politica
        fdivpol = get_divpol_file(resol, ret_folder, ret_f50, ret_f500,
                                  calculo_por)
        print('###### Archivo resolucion: ' + fdivpol)
        # Summary of variables in dictionary python
        d = {'opath':opath, 'decafolder':deca_folder, 'pfiles':path,
             'clt':cultivos1[iclt], 'lfile':lfile,
             'divpol':fdivpol, 'resol':resol, 's50':salida_50,
             's500':salida_500, 'debug':debug}
        # ################################################
        # Start processing daily data to decade data
        # ################################################
        if calcula_deca == 'SI' and resol == '50':
            print('###### Procesando ' + str(len(lfiles)) + ' archivos decadales ######')
            proccessing_decadal(lfiles, d)
            print('###### Fin Calculo decadales ######')
        elif calcula_deca == 'SI' and resol == '500':
            print('Para resolucion ', resol, ' ya estan calculados los decadales')
        else:
            print('###### Para esta corrida, se selecciono SIN calculo de decadales')
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
