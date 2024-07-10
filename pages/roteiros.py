import streamlit as st
import pandas as pd

st.image('https://parametrus.com.br/wp-content/uploads/2021/07/logo-png-vertical.png',width = 100)
st.title('Roteiro')

produto = st.text_input('Produto:')

df = pd.DataFrame(
    [
       {"Código":"-","Componente": "-",
       "Posto Operativo": "-",
       "Tempo": "-"},
   ]
)

df_edit = st.data_editor(df,num_rows="dynamic",hide_index=True)

def save(df_edit):
    st.session_state.df2 = df_edit
    st.session_state.produto1 = produto

st.button('Salvar roteiro', on_click= save, args=(df_edit, ))

if 'df2' in st.session_state:
        st.info(f'Roteiro do produto {st.session_state.produto1} foi salvo')
        st.write(st.session_state.df2)