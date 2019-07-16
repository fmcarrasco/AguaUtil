def processing_cuartel(dic):
    """
    """
    f = open(dic['lfile'], 'a')
    dp3 = pd.read_csv(dic['divpol'], sep=';', encoding='ISO-8859-1')
    cuartel = np.unique(dp3.index.get_level_values('Distrito'))
    dfiles = [i for i in os.listdir(dic['decafolder'])
              if os.path.isfile(os.path.join(dic['decafolder'], i))]
    f.write('Trabajando datos para calculos por CUARTEL \n')
    idx = pd.IndexSlice
    dateparse1 = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')
    for item in cuartel:
        print(item)
        df_s = dp3.loc[idx[item, :,:], :]
        prov = df_s.index.get_level_values('PRDPT')[0]
        centroides = np.unique(df_s.index.get_level_values('centroide'))
        f.write('Trabajando en el departamento: ' + prov + '\n')
        f.write('Trabajando en el cuartel: ' + item + '\n')
        N_PT = 0.
        npts = []
        FirstTime = True
        for ctr in centroides:
            print(ctr)
            f.write('Trabajando en el centroide: ' + ctr + '\n')
            # Leemos el archivo decadal de centroide y cultivo
            f_ctr = [s for s in dfiles if ctr in s and dic['clt'] in s]
            if f_ctr:
                print(f_ctr[0])
                print('--------------------------')
                df_c = df_s.loc[idx[item,:,ctr], :]
                N_PT = N_PT + df_c.sum().values[0]
                Cpt = df_c.sum().values[0]  # Puntos del centroide en el depto
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
                print(txt)
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
            ofolder = dic['opath'] + '/out/' + dic['resol'] + '_' + fhoy + '/'
            os.makedirs(ofolder, exist_ok=True)
            nombre = ofolder + item + '_' + prov + '_' + dic['clt'] + '.xlsx'
            writer = pd.ExcelWriter(nombre, engine = 'xlsxwriter')
            Resumen.to_excel(writer, sheet_name = 'Agua Util')
            tabla_peso.to_excel(writer, sheet_name = 'PESOS')
            f.write('Archivo resumen por cuartel en: ' + nombre + '\n')
            f.write('--------------------------------------------------\n')
            print('--------------------------------------------------\n')
        else:
            txt = u'No se cultiva ' + dic['clt'] +\
                ' cuartel: ' + item + '\n'
            f.write(txt)
            f.write('--------------------------------------------------\n')
    f.close()
