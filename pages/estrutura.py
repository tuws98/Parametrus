import streamlit as st
import pandas as pd
from dados import df_uny1
import time
import numpy as np

st.image('https://parametrus.com.br/wp-content/uploads/2021/07/logo-png-vertical.png',width = 100)
st.title('Estrutura de Produto')

insumos = df_uny1['it-codigo'].value_counts().index

df_uny1 = df_uny1.rename(columns = {'Custo' : 'Custo Unitário'})

produto = st.text_input('Insira o código do produto:')

if "df1" not in st.session_state:
    st.session_state.df1 = pd.DataFrame(columns=[ "Componente", "Quantidade"])

if produto:

    st.subheader("Preencha os dados:")
    with st.form(key="add form", clear_on_submit= True):
        col1,col2 = st.columns(2)
        i = col1.selectbox('Componente',insumos)
        q = col2.number_input('Quantidade')

        df_novo = pd.DataFrame({"Componente":i,"Quantidade":q}, index = [produto])

        if st.form_submit_button('Adicionar'):
            st.session_state.df1 = pd.concat([st.session_state.df1, df_novo], axis=0)
            st.info("Linha adicionada")    

    st.subheader('Estrutura em progresso:')
    estrutura = st.data_editor(st.session_state.df1)

    def save(produto,estrutura):
        global estrutura_final
        st.session_state.produto1 = produto
        st.session_state.estrutura = estrutura
        estrutura_final = pd.DataFrame(st.session_state.estrutura)
        estrutura_final = pd.merge(estrutura_final,df_uny1,how='inner',left_on = 'Componente',right_on='it-codigo').set_index(estrutura_final.index)
        estrutura_final['Custo Total'] = (estrutura_final['Custo Unitário'] * estrutura_final['Quantidade'])
        estrutura_final = estrutura_final.drop('it-codigo',axis=1)

        st.session_state.estrutura_final = estrutura_final 

    col1,col2,col3,col4 = st.columns(4)
    salvar = col1.button('Salvar estrutura', on_click= save, args=(produto,estrutura))
    botao_estrutura = col2.button('Visualizar estrutura')

    if salvar:
            if 'estrutura' in st.session_state and botao_estrutura == False:
                alert = st.success(f'Estrutura do produto {st.session_state.produto1} foi salva')
                time.sleep(1.5) 
                alert.empty()

    def show_estrutura():
        st.subheader('Estrutura salva:')
        view_estrutura = st.session_state.estrutura_final.copy(deep=True)
        view_estrutura['Custo Total'] = view_estrutura['Custo Total'].apply(lambda x: "R$ {:.2f}".format(x))
        view_estrutura['Custo Unitário'] = view_estrutura['Custo Unitário'].apply(lambda x: "R$ {:.2f}".format(x))
        st.write(view_estrutura) 

    if botao_estrutura:
        if 'estrutura' in st.session_state:
            show_estrutura()
        else:
            st.warning('Nenhuma estrutura foi cadastrada')

