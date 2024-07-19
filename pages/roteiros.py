import streamlit as st
from st_pages import show_pages_from_config, add_page_title
import pandas as pd
from dados import df_uny2
import time
import numpy as np
import io
from dependencies import consulta_roteiro

st.set_page_config(page_title="Roteiros de Produção")
st.image('https://parametrus.com.br/wp-content/uploads/2021/07/logo-png-vertical.png',width = 100)
st.title('Roteiros de Produção')


postos = df_uny2['Posto Operativo'].value_counts().index

df_uny2 = df_uny2.rename(columns = {'Custo' : 'Custo/h'})

produto = st.text_input('Insira o código do produto:')

if "df2" not in st.session_state:
    st.session_state.df2 = pd.DataFrame(columns=[ "Componente", "Posto Operativo", 
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
            st.session_state.df2 = pd.concat([st.session_state.df2, df_novo], axis=0)
            st.info("Linha adicionada")    

    st.subheader('Em progresso:')
    roteiro = st.data_editor(st.session_state.df2)

    def save(produto,roteiro):
        global roteiro_final

        st.session_state.produto1 = produto
        st.session_state.roteiro = roteiro
        roteiro_final = pd.DataFrame(st.session_state.roteiro)
        roteiro_final = pd.merge(roteiro_final,df_uny2,how='inner',on='Posto Operativo').set_index(roteiro_final.index)
        roteiro_final['Custo Calculado'] = (roteiro_final['Custo/h'] * roteiro_final['Tempo(h)'])

        st.session_state.roteiro_final = roteiro_final 

    col1,col2,col3,col4 = st.columns(4)
    salvar = col1.button('Salvar roteiro', on_click= save, args=(produto,roteiro))
    botao_roteiro = col2.button('Visualizar roteiro')

    if salvar:
            if 'roteiro' in st.session_state and botao_roteiro == False:
                alert = st.success(f'Roteiro do produto {st.session_state.produto1} foi salvo')
                time.sleep(1.5) 
                alert.empty()

    def show_roteiro():
        st.write('')
        st.subheader('Roteiro salvo:')
        view_roteiro = st.session_state.roteiro_final.copy(deep=True)
        view_roteiro['Custo Calculado'] = (view_roteiro['Custo/h'] * view_roteiro['Tempo(h)']).apply(lambda x: "R$ {:.2f}".format(x))
        view_roteiro['Custo/h'] = view_roteiro['Custo/h'].apply(lambda x: "R$ {:.2f}".format(x))
        view_roteiro = view_roteiro.rename_axis('Produto').reset_index()
        st.write(view_roteiro)

        buffer = io.BytesIO()
        if 'roteiro_final' in st.session_state:
            with pd.ExcelWriter(buffer, engine= 'xlsxwriter') as writer:
                st.session_state.roteiro_final.to_excel(writer, sheet_name= f'Roteiro {st.session_state.produto1}')

                writer.close()

                st.download_button(
                    label = "Exportar roteiro",
                    data = buffer.getvalue(),
                    file_name = f'Roteiro {st.session_state.produto1}.xlsx',
                    mime = "application/vnd.ms-excel"
                )

    if botao_roteiro:
        if 'roteiro' in st.session_state:
            show_roteiro()
        else:
            st.warning('Nenhum roteiro foi cadastrado')