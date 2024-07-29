import streamlit as st
import pandas as pd
from dados import df_uny1
import time
import io
from dependencies import add_estrutura ,del_estrutura, consulta_estrutura, consulta_roteiro, del_roteiro

ss = st.session_state

# Configurar página

st.set_page_config(page_title="Editar registros")
st.image('https://parametrus.com.br/wp-content/uploads/2021/07/logo-png-vertical.png',width = 100)
st.title('Editar registros')
st.markdown("""
            <style>
                div[data-testid="column"] {
                    width: fit-content !important;
                    flex: unset;
                }
                div[data-testid="column"] * {
                    width: fit-content !important;
                }
            </style>
            """, unsafe_allow_html=True)


produto = st.text_input('Insira o código do produto:')


if produto:
    ss.produto_edit = produto 

if 'dummy_edit' not in ss:
    ss.dummy_edit = False
        
def click_button():
    ss.dummy_edit = True


if 'produto_edit' in ss:
    df = consulta_estrutura(ss.produto_edit)
    st.subheader('Estrutura:')
    df_edit = st.data_editor(df,use_container_width=True, num_rows="dynamic",key='editor')
    ss.df_edit = df_edit

    salvar = st.button('Salvar estrutura',key= 'salvar')
    if salvar:
        del_estrutura(ss.produto_edit)
        add_estrutura(ss.df_edit)
        alert = st.success('Alterações salvas')
        time.sleep(1.5) 
        alert.empty()


    df2 = consulta_roteiro(ss.produto_edit)
    st.subheader('Roteiro:')
    df_edit2 = st.data_editor(df2,use_container_width=True, num_rows="dynamic",key='editor2')
    ss.df_edit2 = df_edit2

    salvar2 = st.button('Salvar roteiro',key='salvar2')
    if salvar2:
        del_roteiro(ss.produto_edit)
        add_estrutura(ss.df_edit2)
        alert = st.success('Alterações salvas')
        time.sleep(1.5) 
        alert.empty()