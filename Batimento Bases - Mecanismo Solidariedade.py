# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 10:22:00 2022

@author: rafin
"""
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import time
import datetime as dt



base_antiga = pd.read_csv('Base.csv')

base_antiga = base_antiga.drop(['Unnamed: 0'],axis=1)
base_antiga.Nascimento = pd.to_datetime(base_antiga.Nascimento,errors='coerce',
                                        dayfirst=True)
base_antiga.Entrada = pd.to_datetime(base_antiga.Entrada,errors='coerce',
                                     dayfirst=True)
base_antiga.Saida = pd.to_datetime(base_antiga.Saida,errors='coerce',
                                   dayfirst=True)
base_antiga.ID = base_antiga.ID.astype('str')




hist_antigo = pd.read_csv('Historico.csv')

hist_antigo = hist_antigo.drop(['Unnamed: 0','Ultima2Anos','Aposentado'],axis=1)
hist_antigo.data = pd.to_datetime(hist_antigo.data,errors='coerce',dayfirst=True)
hist_antigo.ID = hist_antigo.ID.astype('str')



''' leitura de base do rh e criação de base com link de pesquisa
e página no transfermarkt.

Depois, ver quais jogadores desta base diferem da base_antiga'''



headers = {'User-Agent': 
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}




df_rh = pd.read_csv('BaseRH.csv',sep=";",decimal=',')

df_base = pd.DataFrame()
df_base['Nome'] = pd.unique(df_rh.NOME).tolist()

df_base['Nascimento'] = ''
df_base['Entrada'] = ''
df_base['Saida'] = ''
df_base['Tipo'] = ''

t = 0
while t < len(df_base):
    nome = df_base.Nome[t]
    df_base['Nascimento'][t] = df_rh[df_rh.NOME == nome]['NASCIMENTO'].tolist()[0]
    df_base['Entrada'][t] = df_rh[df_rh.NOME == nome]['ADMISSÃO'].tolist()[0]
    df_base['Saida'][t] = df_rh[df_rh.NOME == nome]['DEMISSÃO'].tolist()[0]
    df_base['Tipo'][t] = df_rh[df_rh.NOME == nome]['TIPO DEMISSÃO'].tolist()[0]
    t += 1



lista_links = []

for nome in df_base.Nome:
    link = nome.replace(' ','+')
    
    lista_links.append('https://www.transfermarkt.com.br/schnellsuche/ergebnis/schnellsuche?query='+link)
        
df_base['Link'] = lista_links  

df_base = df_base.reset_index(drop=True)


lista_pags = []
lista_ids = []
cont = 1
for link in df_base.Link:

    if link == 'https://www.transfermarkt.com.br/schnellsuche/ergebnis/schnellsuche?query=LUIZ+GUSTAVO+BENMUYAL+REIS':
        pag = '/luiz-gustavo/profil/spieler/597106'
        idjog = '597106'
        lista_pags.append(pag)
        lista_ids.append(idjog)
        
    elif link == 'https://www.transfermarkt.com.br/schnellsuche/ergebnis/schnellsuche?query=DIEGO+DA+SILVA':
        pag = '/diego-silva/profil/spieler/72521'
        idjog = '72521'
        lista_pags.append(pag)
        lista_ids.append(idjog)
        
    elif link == 'https://www.transfermarkt.com.br/schnellsuche/ergebnis/schnellsuche?query=MATHEUS+PEREIRA':
        pag = '/matheus-pereira/profil/spieler/739438'
        idjog = '739438'
        lista_pags.append(pag)
        lista_ids.append(idjog)
    
    else:

        url = link
        
        page = requests.get(url, headers=headers)
                
        soup = bs(page.content,'html.parser')
        
        
        resultados = soup.find_all('table',{'class':'items'})
        
        divs = soup.find_all('div',{'class':'table-header'})
        
        
        if len(divs) > 0 and divs[0].text[:29] == 'Resultados de pesquisa para j':
            
            tabela = resultados[0]
            
            pag = soup.find_all('tr')[1].find_all('a')[1].get('href')
            idjog = pag.split('/')[4]
            
            lista_ids.append(idjog)
            
            lista_pags.append(pag)
            time.sleep(1)
            
        else:
            
            time.sleep(1)
            lista_ids.append('-')
            lista_pags.append('-')
        
    print(cont)
    cont += 1

df_base['Pagina'] = lista_pags
df_base['ID'] = lista_ids

df_base.ID = df_base.ID.replace('-','0')


jogs_novos = pd.concat([df_base,base_antiga])

jogs_novos = jogs_novos.reset_index(drop=True)

jogs_novos = jogs_novos.drop_duplicates(keep=False)

jogs_novos = jogs_novos.drop_duplicates('Link')
jogs_novos = jogs_novos[jogs_novos.ID != '0']


''' exportando o jogs_novos com jogadores novos encontrados a partir da 
atualização da "Base RH.xlsx" quando comparado com a ultima base "Base.csv"
gerada'''

jogs_novos.to_csv('JogsNovos.csv',index=False)


''' gerar novo transfs que vai comparar com o hist_antigo para ver quais 
transferencias novas foram encontradas, incluindo jogadores novos e tambem
aqueles já na base'''




dic_historico = {}

cont = 1
for link in df_base.Pagina:
    
    if link != '-':
        url = 'https://www.transfermarkt.com.br'+link
        
        page = requests.get(url, headers=headers)
                
        soup = bs(page.content,'html.parser')
        
        transfs = soup.find_all('div',{'class':'tm-player-transfer-history-grid'})[1:-1]
        
        lista_data = []
        lista_cv = []
        lista_cc = []
        lista_vt = []
        
        for transf in transfs:
            if transf.find('div') is None:
                continue
            else:
                data = transf.find('div',{'class':'tm-player-transfer-history-grid__date'}).text.strip()
                cv = transf.find('div',{'class':'tm-player-transfer-history-grid__old-club'}).text.strip()
                cc = transf.find('div',{'class':'tm-player-transfer-history-grid__new-club'}).text.strip()
                vt = transf.find('div',{'class':'tm-player-transfer-history-grid__fee'}).text.strip()
                
                lista_data.append(data)
                lista_cv.append(cv)
                lista_cc.append(cc)
                lista_vt.append(vt)
            
        dic = {'data':lista_data,'cv':lista_cv,'cc':lista_cc,'vt':lista_vt}
        
        id_jog = link.split('/')[4]
        
        lista_ids.append(id_jog)
        
        dic_historico[id_jog] = dic
        
        print(cont)
        cont += 1
        
        time.sleep(1)
        
    else:
        print(cont)
        cont += 1
        
        time.sleep(1)



''' exportando as transferencias novas a serem analisadas, aquelas que nao 
estavam no hist_antigo ("Historico.csv")'''


transfs = pd.DataFrame()

for item in dic_historico:
    
    df = pd.DataFrame(dic_historico[item])
    
    df = df.assign(ID = item)
    
    transfs = transfs.append(df)
    
transfs = transfs.reset_index(drop=True)

transfs.data = pd.to_datetime(transfs.data,errors='coerce',dayfirst=True)



trans_novas = pd.concat([transfs,hist_antigo])

trans_novas = trans_novas.reset_index(drop=True)

trans_novas = trans_novas.drop_duplicates(keep=False)


trans_novas.to_csv('TransfNovas.csv',index=False)



''' identificando aposentados e ultima a mais de 2 anos para dps exportar'''


hoje = dt.datetime.now()
margem = dt.timedelta(days = 730)

lista_situacao = []

for jog in pd.unique(transfs.ID):
    aux_df = transfs[transfs.ID == jog]
    
    ultima = aux_df.nlargest(1,'data')['data'].tolist()[0]
    
    t = 0 
    while t < len(aux_df):
        if hoje > ultima + margem:
            lista_situacao.append('SIM')
        else:
            lista_situacao.append('NAO')
            
        t += 1
        

transfs['Ultima2Anos'] = lista_situacao


lista_aposent = []

for jog in pd.unique(transfs.ID):
    aux_df = transfs[transfs.ID == jog]
    
    ultima = aux_df.nlargest(1,'data')['cc'].tolist()[0]
    
    t = 0 
    while t < len(aux_df):
        if ultima == 'Fim de carreira':
            lista_aposent.append('SIM')
        else:
            lista_aposent.append('NAO')
            
        t += 1
        
transfs['Aposentado'] = lista_aposent



''' exportando a base e o historico para substituir na pasta e favorecer a 
proxima comparação'''


transfs.to_csv('Historico.csv',index=False)
df_base.to_csv('Base.csv',index=False)


