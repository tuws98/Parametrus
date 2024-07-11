import streamlit as st
import pandas as pd
from dados import df_uny1
import time
import numpy as np

st.image('https://parametrus.com.br/wp-content/uploads/2021/07/logo-png-vertical.png',width = 100)
st.title('Roteiros de Produção')

postos = df_uny1['Posto Operativo'].value_counts().index

df_uny1 = df_uny1.rename(columns = {'Custo' : 'Custo/h'})

produto = st.text_input('Insira o código do produto:')

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[ "Componente", "Posto Operativo", 
                                                "Tempo(h)"])

if produto:

    st.subheader("Preencha os dados:")
    with st.form(key="add form", clear_on_submit= True):
        col1,col2,col3 = st.columns(3)
        c = col1.text_input('Componente')
        p = col2.selectbox('Posto Operativo',postos)
        t = col3.number_input('Tempo(h)')

        df_novo = pd.DataFrame({"Componente":c,"Posto Operativo":p, "Tempo(h)":t}, index = [produto])

        if st.form_submit_button('Adicionar'):
            st.session_state.df = pd.concat([st.session_state.df, df_novo], axis=0)
            st.info("Linha adicionada")    

    st.subheader('Roteiro em progresso:')
    roteiro = st.data_editor(st.session_state.df)

    def save(produto,roteiro):
        st.session_state.produto1 = produto
        st.session_state.roteiro = roteiro

    col1,col2,col3,col4 = st.columns(4)
    salvar = col1.button('Salvar roteiro', on_click= save, args=(produto,roteiro))
    botao_roteiro = col2.button('Visualizar roteiro')

    if salvar:
            if 'roteiro' in st.session_state and botao_roteiro == False:
                alert = st.success(f'Roteiro do produto {st.session_state.produto1} foi salvo')
                time.sleep(1.5) 
                alert.empty()

    def show_roteiro():
        st.subheader('Roteiro salvo:')
        roteiro_final = pd.DataFrame(st.session_state.roteiro)
        roteiro_final = pd.merge(roteiro_final,df_uny1,how='inner',on='Posto Operativo').set_index(roteiro_final.index)
        roteiro_final['Custo Calculado'] = roteiro_final['Custo/h'] * roteiro_final['Tempo(h)']
        st.write(roteiro_final)

    if botao_roteiro:
        if 'roteiro' in st.session_state:
            show_roteiro()
        else:
            st.warning('Nenhum roteiro foi cadastrado')