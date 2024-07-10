import streamlit as st
import pandas as pd

df = pd.read_csv('tabela_imap.csv',sep=';',decimal = ',')

df_sku = df['sku'].value_counts().index

st.set_page_config(layout="wide")
st.image('https://parametrus.com.br/wp-content/uploads/2021/07/logo-png-vertical.png',width = 100)
st.title('Precificador')

left, right = st.columns(2)

with left:
    sku = st.selectbox('SKU',df_sku)
    st.write('')
    custo_variavel = df[df['sku'] == sku]['custo_variavel'].sum()
    st.metric('Custo Variável','R$ {:,.2f}'.format(custo_variavel))
    st.write('')
    markup = st.slider('_Markup:_ porcentagem sobre o custo',0,400,0,format="%d%%")/100
  
with right:
    quantidade = st.number_input('Quantidade', min_value = 1, value = 1, step = 1)
    st.write('')
    custo_operacional = df[df['sku'] == sku]['custo_operacional'].sum()
    st.metric('Custo Operacional','R$ {:,.2f}'.format(custo_operacional))
    st.write('')
    desconto = st.slider('Desconto Concedido',0,100,0,format="%d%%")/100

preco_unitario = (custo_variavel + custo_operacional)*(1+markup)
preco_total = (custo_variavel + custo_operacional) * (1+markup) * quantidade
margem_1 = preco_total - (custo_operacional + custo_variavel) * quantidade
preco_unitario_2 = (preco_unitario - preco_unitario * desconto)
preco_total_2 = (preco_total - preco_total * desconto)
margem_2 = preco_total_2 - (custo_operacional + custo_variavel) * quantidade

with left:
    st.write('')
    st.write('Valores **sem desconto**:')
    st.write('Preço Unitário : R$ {:0,.2f}'.format(preco_unitario))
    st.write('Preço Total : R$ {:0,.2f}'.format(preco_total))
    st.write('Margem de Lucro: R$ {:0,.2f}'.format(margem_1))

with right:
    st.write('')
    st.write('Valores **com desconto**:')
    st.write('Preço Unitário : R$ {:0,.2f}'.format(preco_unitario_2))
    st.write('Preço Total : R$ {:0,.2f}'.format(preco_total_2))
    st.write('Margem de Lucro: R$ {:0,.2f}'.format(margem_2))

if 'df1' in st.session_state:
    st.write('Estrutura:')
    st.write(st.session_state.df1)

if 'df2' in st.session_state:
    st.write('Roteiro:')
    st.write(st.session_state.df2)








