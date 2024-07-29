import streamlit as st
import plotly.express as px
import pandas as pd
from st_pages import _show_pages_from_config
from dependencies import consulta_estrutura, consulta_roteiro, produtos, recur


df_sku = pd.Series(['-'])

st.set_page_config(layout="wide",page_title="Precificador")
st.image('https://parametrus.com.br/wp-content/uploads/2021/07/logo-png-vertical.png',width = 100)
st.title('Precificador')
_show_pages_from_config()
ss = st.session_state

df_sku = produtos()

col1,col2 = st.columns(2)
sku = col1.selectbox('Produto',df_sku,placeholder= '-',key= 'sku',index = None)
st.write("")

estrutura = recur(ss.sku)
df_estrutura = pd.DataFrame(estrutura)
df_estrutura.reset_index(inplace= True)
df_estrutura.set_index('Produto',inplace= True)
roteiro = consulta_roteiro(ss.sku)
df_roteiro = pd.DataFrame(roteiro)
df_roteiro.set_index('produto',inplace= True)
df_roteiro['custo_total'] = df_roteiro['tempo'] * df_roteiro['custo_h']

custo_variavel = df_estrutura['Custo Total'].sum()
custo_operacional = df_roteiro['custo_total'].sum()


if ss.sku:

    col1,col2,col3 = st.columns(3)
    col1.metric('Custo Variável','R$ {:,.2f}'.format(float(custo_variavel)))
    col2.metric('Custo Operacional','R$ {:,.2f}'.format(float(custo_operacional)))
    col3.metric('Custo Total','R$ {:,.2f}'.format(float(custo_variavel + custo_operacional)))


    with col1:
        st.write('')
        preco_unitario = st.number_input('Preço Unitário (R$)')
    
    with col2:
        st.write('')
        quantidade = col2.number_input('Quantidade', min_value = 1, value = 1, step = 1)

    with col3:
        st.write('')
        aliquota = st.number_input('Alíquota de imposto (%)')/100
        imposto = preco_unitario * aliquota


    left,mid,right = st.columns(3)
    left.write('')
    desconto = left.slider('Desconto Concedido (%)',0,100,0)/100
    left.write('')

    preco_total = preco_unitario * quantidade
    margem_1 = preco_total - (custo_operacional + custo_variavel + imposto) * quantidade
    preco_unitario_2 = (preco_unitario - preco_unitario * desconto)
    preco_total_2 = (preco_total - preco_total * desconto)
    margem_2 = preco_total_2 - (custo_operacional + custo_variavel + imposto) * quantidade

    col1,col2,col3 = st.columns(3)

    with col1:
        st.write('')
        st.write('Valores **sem desconto**:')
        st.write('Preço Unitário : R$ {:0,.2f}'.format(preco_unitario))
        st.write('Valor Total : R$ {:0,.2f}'.format(preco_total))
        st.write('(-) Custos: R$ {:0,.2f}'.format((custo_variavel + custo_operacional) * quantidade))
        st.write('(-) Impostos: R$ {:0,.2f}'.format(imposto * quantidade))
        st.write('Margem de Lucro: R$ {:0,.2f}'.format(margem_1))

    with col2:
        st.write('')
        st.write('Valores **com desconto**:')
        st.write('Preço Unitário : R$ {:0,.2f}'.format(preco_unitario_2))
        st.write('Valor Total : R$ {:0,.2f}'.format(preco_total_2))
        st.write('(-) Custos: R$ {:0,.2f}'.format((custo_variavel + custo_operacional) * quantidade))
        st.write('(-) Impostos: R$ {:0,.2f}'.format(imposto * quantidade))
        st.write('Margem de Lucro: R$ {:0,.2f}'.format(margem_2))





