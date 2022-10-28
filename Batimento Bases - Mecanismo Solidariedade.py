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
        
    st.write(cont)
    cont += 1

df_base['Pagina'] = lista_pags
df_base['ID'] = lista_ids

df_base.ID = df_base.ID.replace('-','0')

st.write(df_base)
