import streamlit as st
import pandas as pd

df_sku = pd.Series(['-'])

st.set_page_config(layout="wide")
st.image('https://parametrus.com.br/wp-content/uploads/2021/07/logo-png-vertical.png',width = 100)
st.title('Precificador')

if 'estrutura_final' in st.session_state:
    df_sku = st.session_state.estrutura_final.index
##else:
  ##  st.warning('Cadastre a estrutura do produto')

if 'roteiro_final' in st.session_state:
    df_sku = df_sku.append(st.session_state.roteiro_final.index)
##else:
   ## st.warning('Cadastre o roteiro do produto')

col1,col2 = st.columns(2)
sku = col1.selectbox('Produto',df_sku)
quantidade = col2.number_input('Quantidade', min_value = 1, value = 1, step = 1)
st.write("")

if 'estrutura_final' in st.session_state:

    left, right = st.columns(2)

    if 'estrutura_final' in st.session_state:
        with left:
            st.write('')
            custo_variavel = st.session_state.estrutura_final[st.session_state.estrutura_final.index == sku]['Custo Total'].sum()
            st.metric('Custo Variável','R$ {:,.2f}'.format(float(custo_variavel)))
            st.write('')
            markup = st.slider('_Markup:_ porcentagem sobre o custo',0,400,0,format="%d%%")/100
        
        with right:
            st.write('')
            if 'roteiro_final' in st.session_state:
                custo_operacional = st.session_state.roteiro_final[st.session_state.roteiro_final.index == sku]['Custo Calculado'].sum()
            else:
                custo_operacional = 0
            st.metric('Custo Operacional','R$ {:,.2f}'.format(float(custo_operacional)))
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

if 'estrutura_final' not in st.session_state:
    st.warning('Cadastre a estrutura de produto')

if 'roteiro_final' not in st.session_state:
    st.warning('Cadastre o roteiro de produto')







