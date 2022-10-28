# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 17:35:14 2022

@author: rafin
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import time
import datetime as dt


headers = {'User-Agent': 
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}



df_rh = pd.read_excel('BaseRH.xlsx')

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
    

    
'''agora precisa criar df com todas as transferencias para os jogadores do 
dic_historico como forma de controlar jogadores que estao no transfermarkt'''




transfs = pd.DataFrame()

for item in dic_historico:
    
    df = pd.DataFrame(dic_historico[item])
    
    df = df.assign(ID = item)
    
    transfs = transfs.append(df)
    
transfs = transfs.reset_index(drop=True)

transfs.data = pd.to_datetime(transfs.data,errors='coerce',dayfirst=True)













''' pensar melhor nos próximos passos com a base pronta'''

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



validas = transfs[transfs.data > hoje - margem]






transfs.to_csv('Historico.csv')


df_base.ID = df_base.ID.replace('-',0)
df_base.to_csv('Base.csv')




    

    
    
    
    
    
    
    
        
    
    
    

