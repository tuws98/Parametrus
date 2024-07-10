import streamlit as st
import pandas as pd

st.image('https://parametrus.com.br/wp-content/uploads/2021/07/logo-png-vertical.png',width = 100)
st.title('Estrutura')

produto = st.text_input('Produto:')

st.write('')

df = pd.DataFrame(
    [
       {"Código":"-","Componente": "-",
       "Quantidade": 0,
       "Custo": 0},
   ]
)

df_edit = st.data_editor(df,num_rows="dynamic",hide_index=True)

def save(df_edit):
    st.session_state.df1 = df_edit
    st.session_state.produto = produto

st.button('Salvar estrutura', on_click= save, args=(df_edit, ))

if 'df1' in st.session_state:
        st.info(f'Estrutura do produto {st.session_state.produto} foi salva')
        st.write(st.session_state.df1)
        cv = st.session_state.df1['Quantidade'] * st.session_state.df1['Custo']
        st.write('Custo Variável:  R${:0,.2f}'.format(cv.sum()))



