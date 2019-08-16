"""
Funciones para trabajar con los archivos de porcentaje
de Agua Util por cultivo.
Tareas que hay que realizar:
- Lectura de TXT con los datos diarios
- Calculo de medias decadales (1-10; 11-20; 21-Fin de Mes)
- Union de estos datos con superficies por departamento y por cuartel
"""
import os
import pandas as pd
import numpy as np
import datetime as dt
import calendar

import matplotlib
import matplotlib.pyplot as plt

def clas_decada(fechas):
    """
    Funcion para crear array que clasifica las fechas
    por decada diaria mensual.
    """
    #
    r_i = np.zeros(np.shape(fechas))
    r_d = []  #np.zeros(np.shape(fechas))
    years = np.unique([i.year for i in fechas])
    # print(len(years)*12*3)
    nindex = 1
    for yr in years:
        for mo in np.arange(1,13):
            i1 = np.logical_and(fechas >= dt.datetime(yr,mo,1),
                                fechas <= dt.datetime(yr,mo,10))
            i2 = np.logical_and(fechas >= dt.datetime(yr,mo,11),
                                fechas <= dt.datetime(yr,mo,20))
            u_day = calendar.monthrange(yr, mo)[1]
            i3 = np.logical_and(fechas >= dt.datetime(yr,mo,21),
                                fechas <= dt.datetime(yr,mo,u_day))
            r_i[i1] = nindex
            r_i[i2] = nindex + 1
            r_i[i3] = nindex + 2
            r_d.append(dt.datetime(yr,mo,1))
            r_d.append(dt.datetime(yr,mo,11))
            r_d.append(dt.datetime(yr,mo,21))
            nindex = nindex + 3

    return r_i, r_d

def get_file_data(archivo):
    """
    Separa del nombre del archivo y extrae nombre de Centroide (ctrd)
    y cultivo (clt)
    """
    diccionario = {}
    l0 = archivo.split('.')  # ultimo valor es 'txt'
    str1 = ''.join(l0[:-1])  # Elimina los puntos (e.g M1.1 queda M11)
    l1 = str1.split('-')  # el ultimo debiera ser el cultivo
    if 'S1' in l1:
        diccionario['ctrd'] = '-'.join(l1[:-2])
        diccionario['clt'] = '-'.join(l1[-2::])
    else:
        diccionario['ctrd'] = '-'.join(l1[:-1])
        diccionario['clt'] = l1[-1]

    return diccionario


def sum_wgt_table(Resumen, peso):
    """
    Funcion para sumar
    """
    arr_out = np.zeros(Resumen.shape[0])
    for ic, column in enumerate(Resumen):
        if column != 'Fecha':
            arr_out = arr_out + Resumen[column].values * peso[ic - 1]

    return arr_out


def proccessing_decadal(lfiles, dic):
    """
    """
    dateparse = lambda x: pd.datetime.strptime(x, '%d/%m/%Y')
    f = open(dic['lfile'], 'a')
    for arc in lfiles:
        f.write('Trabajando en el archivo: ' + arc + '\n')
        # print(arc)
        bfile = dic['pfiles'] + arc
        df = pd.read_csv(bfile, sep=';', decimal=',',
                         parse_dates=['Fecha'], date_parser=dateparse,
                         encoding='ISO-8859-1')
        # Renomobramos las columnas
        df.columns = ['Fecha', 'ALM', 'ETR', 'ETC', 'AU', 'ED', 'EA']
        i_col, f_col = clas_decada(df.Fecha.dt.to_pydatetime())
        df = df.assign(i_deca=i_col)
        deca1 = df.groupby('i_deca').mean()  # Media por decada dias
        deca2 = df.groupby('i_deca').count()  # Conteo de dias
        # Create decadal output
        col = ['i_deca', 'AU', 'c_AU']
        list_of_series = [deca1.index, deca1.AU, deca2.AU]
        deca = pd.DataFrame({'AU':deca1.AU, 'c_AU':deca2.AU})
        deca = deca.assign(f_deca=f_col[0:int(i_col[-1])])
        if deca['c_AU'].iloc[-1] < 10:
            # Si el ultimo no tiene la decada completa, NO se incluye!
            deca.drop(deca.tail(1).index, inplace=True)
        deca.apply(pd.to_numeric, errors='ignore')
        # Obtenemos datos de archivo (Centroide y Cultivo)
        f_d = get_file_data(arc)
        if f_d['clt'] != 'QUE':
            # print(f_d)
            d_file = dic['decafolder'] + 'decadales_' + f_d['ctrd'] +\
                     '_' + f_d['clt']
            deca.to_csv(d_file + '.txt', sep=';', decimal=',', float_format='%.3f',
                        encoding='ISO-8859-1')
            # ----- LOGFILE -------
            f.write('Archivo con datos decadales: ' + d_file + '.txt \n')
            f.write('--------------------------------------------------\n')
            # ---------------------
        df = None
    # --- End of LOOP ------------------------
    f.close()


def processing_departamento(dic):
    """
    """
    f = open(dic['lfile'], 'a')
    f.write('Trabajando en archivos de division politica \n')
    dp3 = pd.read_csv(dic['divpol'], sep=';', encoding='ISO-8859-1')
    f.write('Archivo con datos Division Politica: ' + dic['dpfile'] + '\n')
    f.write('--------------------------------------------------\n')
    # ################################################
    # Read decadal files
    # ################################################
    dfiles = [i for i in os.listdir(dic['decafolder'])
              if os.path.isfile(os.path.join(dic['decafolder'], i))]
    # Get all Single DPTO
    dpto = np.unique(dp3['PRDPT'].values)
    # ################################################
    # Calculos por DEPARTAMENTO
    # Parametros para leer bien los distintos archivos
    # ################################################
    dateparse1 = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')
    for item in dpto:
        f.write(u'Trabajando en el departamento: ' + item + '\n')
        df_s = dp3[dp3['PRDPT'] == item]
        centroides = np.unique(df_s['centroide'].values)
        FirstTime = True
        weights = []
        npts = []
        N_PT = 0.
        for ctr in centroides:
            f.write(u'Trabajando en el centroide: ' + ctr + '\n')
            # Archivos decadales e.g: decadales_F100-30_3_TL
            if dic['clt'] == 'TL':
                    ndecafile1 = 'decadales_' + ctr + '_' + dic['clt']
                    ndecafile2 = 'decadales_' + ctr + '_' + 'TS(' + dic['clt'] + ')'
                    f_ctr = [s for s in dfiles
                             if ndecafile1 in s or ndecafile2 in s]
            elif dic['clt'] == 'S2':
                ndecafile = 'decadales_' + ctr + '_' + 'TS(' + dic['clt'] + ')'
                f_ctr = [s for s in dfiles if ndecafile in s]
            else:
                ndecafile = 'decadales_' + ctr + '_' + dic['clt']
                f_ctr = [s for s in dfiles if ndecafile in s]
            if f_ctr:
                # Vamos sumando para obtener el total de puntos
                df_c = df_s[np.logical_and(df_s['PRDPT'] == item,
                                           df_s['centroide'] == ctr)]
                N_PT = N_PT + df_c.sum()['DEPTO'] # Total de puntos
                Cpt = df_c.sum()['DEPTO'] # Puntos del centroide en el depto
                npts.append(Cpt)
                df_deca = pd.read_csv(dic['decafolder'] + '/' + f_ctr[0],
                                      sep=';', decimal=',',
                                      parse_dates=['f_deca'],
                                      date_parser=dateparse1,
                                      encoding='ISO-8859-1')
                if FirstTime:
                    FirstTime = False
                    Resumen = pd.DataFrame(index=np.arange(0, len(df_deca)))
                    # Assume that all decadal files has the same len
                    Resumen = Resumen.assign(Fecha=df_deca['f_deca'])
                    fecha_f = df_deca['f_deca'].iloc[-1]
                ###########
                n_str = u'AU_' + ctr
                if ctr == u'CAÑUELAS':
                    n_str = 'AU_CANUELAS'
                kwargs = {n_str: df_deca.AU}
                Resumen = Resumen.assign(**kwargs)
            #################################################
            else:
                txt = u'No hay decadal para cultivo ' + dic['clt'] +\
                    ' en el centroide: ' + ctr + '\n'
                f.write(txt)

        if npts:
            weights = [valor/N_PT for valor in npts]
            # Tabla de Pesos
            columnas = Resumen.columns[1::]
            tabla_peso = pd.DataFrame(columns=columnas,
                                      index=['PESO', 'PTS_CTR', 'PTS_TOTAL'])
            tabla_peso.loc[['PESO'], :] = weights
            tabla_peso.loc[['PTS_CTR'], :] = npts
            tabla_peso.loc[['PTS_TOTAL'], :] = N_PT*np.ones(len(columnas))
            # Calculamos columna con la SUMA y sus respectivos pesos
            Resumen = Resumen.assign(AU_WGT=sum_wgt_table(Resumen, weights))
            Resumen.apply(pd.to_numeric, errors='ignore')
            # -------------------------------------------------------------
            fhoy = fecha_f.strftime('%d%m%Y')
            ofolder = dic['opath'] + 'out/' + dic['resol'] + '_' + fhoy + '_out/'
            os.makedirs(ofolder, exist_ok=True)
            nombre = ofolder + item + '_' + dic['clt'] + '.xlsx'
            writer = pd.ExcelWriter(nombre, engine = 'xlsxwriter')
            Resumen.to_excel(writer, float_format = '%0.1f', sheet_name = 'Agua Util')
            tabla_peso.to_excel(writer, sheet_name = 'PESOS')
            f.write(u'Archivo resumen por departamento en: ' + nombre + '\n')
            f.write('--------------------------------------------------\n')
        else:
            txt = u'No se cultiva ' + dic['clt'] +\
                ' departamento: ' + item + '\n'
            f.write(txt)
            f.write('--------------------------------------------------\n')
    f.close()


def processing_cuartel(dic):
    """
    """
    f = open(dic['lfile'], 'a')
    f.write('Trabajando en archivos de division politica \n')
    dp3 = pd.read_csv(dic['divpol'], sep=';', encoding='ISO-8859-1')
    f.write('Archivo con datos Division Politica: ' + dic['dpfile'] + '\n')
    f.write('--------------------------------------------------\n')
    # ################################################
    # Read decadal files
    # ################################################
    dfiles = [i for i in os.listdir(dic['decafolder'])
              if os.path.isfile(os.path.join(dic['decafolder'], i))]
    # Get all Single Distrito (o cuartel)
    cuartel = np.unique(np.unique(dp3['Distrito'].values))
    dateparse1 = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')
    for item in cuartel:
        df_s = dp3[dp3['Distrito'] == item]
        prov = df_s['PRDPT'].iloc[0]
        centroides = np.unique(df_s['centroide'].values)
        FirstTime = True
        weights = []
        npts = []
        N_PT = 0.
        for ctr in centroides:
            f.write('Trabajando en el centroide: ' + ctr + '\n')
            # Leemos el archivo decadal de centroide y cultivo
            if dic['clt'] == 'TL':
                    ndecafile1 = 'decadales_' + ctr + '_' + dic['clt']
                    ndecafile2 = 'decadales_' + ctr + '_' + 'TS(' + dic['clt'] + ')'
                    f_ctr = [s for s in dfiles
                             if ndecafile1 in s or ndecafile2 in s]
            elif dic['clt'] == 'S2':
                ndecafile = 'decadales_' + ctr + '_' + 'TS(' + dic['clt'] + ')'
                f_ctr = [s for s in dfiles if ndecafile in s]
            else:
                ndecafile = 'decadales_' + ctr + '_' + dic['clt']
                f_ctr = [s for s in dfiles if ndecafile in s]
            if f_ctr:
                df_c = df_s[np.logical_and(df_s['Distrito'] == item,
                                           df_s['centroide'] == ctr)]
                N_PT = N_PT + df_c.sum()['DEPTO']
                Cpt = df_c.sum()['DEPTO']  # Puntos del centroide en el depto
                npts.append(Cpt)            # Guardamos los puntos del centroide
                df_deca = pd.read_csv(dic['decafolder'] + '/' + f_ctr[0],
                                      sep=';', decimal=',',
                                      parse_dates=['f_deca'],
                                      date_parser=dateparse1)
                if FirstTime:
                    FirstTime = False
                    Resumen = pd.DataFrame(index=np.arange(0, len(df_deca)))
                    # Assume that all decadal files has the same len
                    Resumen = Resumen.assign(Fecha=df_deca['f_deca'])
                n_str = 'AU_' + ctr
                kwargs = {n_str: df_deca.AU}
                Resumen = Resumen.assign(**kwargs)

            else:
                txt = u'No hay decadal para cultivo ' + dic['clt'] +\
                    ' en el centroide: ' + ctr + '\n'
                f.write(txt)
            ###########
        # End LOOP for centroides
        # ################################################
        if npts:
            weights = [valor/N_PT for valor in npts]
            # Tabla de Pesos
            columnas = Resumen.columns[1::]
            tabla_peso = pd.DataFrame(columns=columnas,
                                      index=['PESO', 'PTS_CTR', 'PTS_TOTAL'])
            tabla_peso.loc[['PESO'], :] = weights
            tabla_peso.loc[['PTS_CTR'], :] = npts
            tabla_peso.loc[['PTS_TOTAL'], :] = N_PT*np.ones(len(columnas))
            # Calculamos columna con la SUMA y sus respectivos pesos
            Resumen = Resumen.assign(AU_WGT=sum_wgt_table(Resumen, weights))
            Resumen.apply(pd.to_numeric, errors='ignore')
            # -------------------------------------------------------------
            fhoy = dt.datetime.today().strftime('%d%m%Y')
            ofolder = dic['opath'] + 'out/cuartel_' + dic['resol'] + '_' + fhoy + '/'
            os.makedirs(ofolder, exist_ok=True)
            nombre = ofolder + item + '_' + prov + '_' + dic['clt'] + '.xlsx'
            writer = pd.ExcelWriter(nombre, engine = 'xlsxwriter')
            Resumen.to_excel(writer, sheet_name = 'Agua Util')
            tabla_peso.to_excel(writer, sheet_name = 'PESOS')
            f.write('Archivo resumen por cuartel en: ' + nombre + '\n')
            f.write('--------------------------------------------------\n')
        else:
            txt = u'No se cultiva ' + dic['clt'] +\
                ' cuartel: ' + item + '\n'
            f.write(txt)
            f.write('--------------------------------------------------\n')
    f.close()


def main():
    # ################################################
    # Initial values to work
    # ################################################
    # ----- Modificar los valores para corrida decadales ------
    resol = '50'  # o puede ser '50'
    # Cambiar fecha para cada vez que se corre, colocando dia inicial decada
    fdeca = dt.datetime(2019, 4, 21).strftime('%d%m%Y')
    path = 'e:/python/AguaUtil/Balances/Balance1970/'
    opath = 'e:/python/AguaUtil/'
    au_folder = 'AU'
    deca_folder = opath + 'Decadales/decadal1970/'
    # Sin el punto que viene por default
    # colocar el cultivo a trabajar:
    cultivo = 'A12'
    # [S1, S2, M11, M12, M21, M22, G11, G12, A11, A12, TL, TS(TC)]
    clt_file = 'A1.2'
    # [S1, TS(S2), M1.1, M1.2, M2.1, M2.2, G1.1, G1.2, A1.1, A1.2, TL, TS(TC)]
    # -----  hasta aca se modifican los valores del usuario ------
    # Se crea carpetas
    os.makedirs(opath, exist_ok=True)
    os.makedirs(deca_folder, exist_ok=True)
    # Datos para el LOGFILE
    fhoy = dt.datetime.today().strftime('%d%m%Y')
    lfile = opath + 'out/' + fhoy +'_' + cultivo + '_' + resol +\
            '_' + fdeca + '_logfile.txt'
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

    # Summary of variables in dictionary python
    d = {'opath':opath, 'decafolder':deca_folder, 'pfiles':path,
         'clt':cultivo, 'lfile':lfile, 'dpfile':dp_file,
         'divpol':fdivpol, 'resol':resol}

    # ################################################
    # Start processing daily data to decade data
    # ################################################
    proccessing_decadal(lfiles, d)
    # ################################################
    # Start proccessing Data of Provinces and percentages of centroid inside
    # ################################################
    processing_departamento(d)
    # ################################################
    # Calculos por Cuartel
    # Parametros para leer bien los distintos archivos
    # ################################################
    # processing_cuartel(d)
# ###########################
# FIN PROGRAMA
# ###########################

if __name__ == '__main__':
    import time
    ############
    start_time = time.time()
    main()
    print('Tiempo de demora del script:')
    print("--- %s seconds ---" % (time.time() - start_time))
