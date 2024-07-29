import streamlit as st
import pandas as pd
from dados import df_uny1
import time
import io
from dependencies import add_estrutura ,del_estrutura, consulta_estrutura, consulta_postos, add_postos, del_postos
from dados import df_uny2

ss = st.session_state

# Configurar página

st.set_page_config(page_title="Importação de dados")
st.image('https://parametrus.com.br/wp-content/uploads/2021/07/logo-png-vertical.png',width = 100)
st.title('Importação de dados')
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



# add = st.button('add')
# df_uny2.rename(columns={'Posto Operativo':'posto_operativo','Custo/h':'custo_h'},inplace = True)
# if add:
#    add_postos(df_uny2)



df = consulta_postos()
st.subheader('Custo/h dos POs:')
df.sort_values(by='Posto Operativo',inplace= True,ignore_index= True)
df_postos = st.data_editor(df, num_rows="dynamic",key='editor',disabled= 'Posto Operativo')
df_postos.rename(columns={'Posto Operativo':'posto_operativo','Custo/h':'custo_h'},inplace = True)
ss.df_postos = df_postos

salvar = st.button('Atualizar custo/h dos POs',key= 'salvar')
if salvar:
    del_postos()
    add_postos(ss.df_postos)
    alert = st.success('Alterações salvas')
    time.sleep(1.5) 
    alert.empty()


st.subheader('Custo dos insumos:')
uploaded_file = st.file_uploader('Upload da planilha de custo dos insumos',type = 'xlsx')
if uploaded_file:
    xl_insumos = pd.read_excel(uploaded_file)
    df_insumos = pd.DataFrame(xl_insumos)
salvar2 = st.button('Atualizar custos médio insumos')
if salvar2:
    alert = st.success('Alterações salvas')
    time.sleep(1.5) 
    alert.empty()

