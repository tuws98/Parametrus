import streamlit as st
from st_pages import show_pages_from_config, add_page_title
import pandas as pd
from dados import df_uny1
import time
import numpy as np
import io
from dependencies import criar_estrutura, consulta_estrutura, add_estrutura

state = st.session_state

# Configurar página
st.set_page_config(page_title="Estrutura")
st.image('https://parametrus.com.br/wp-content/uploads/2021/07/logo-png-vertical.png',width = 100)
st.title('Estrutura de Produto')


# Puxando insumos da tabela
insumos = df_uny1['it-codigo'].value_counts().index

# Renomear colunas
df_uny1 = df_uny1.rename(columns = {'Custo' : 'Custo Unitário'})


produto = st.text_input('Insira o código do produto:')

# Criando DataFrame
if "df1" not in st.session_state:
    st.session_state.df1 = pd.DataFrame(columns=[ "Componente","Matéria-Prima", "Quantidade"])

if produto:

# Criando formulário a ser preenchido
    st.subheader("Preencha os dados:")
    with st.form(key="add form", clear_on_submit= True):
        col1,col2,col3 = st.columns(3)
        c = col1.selectbox("Componente",insumos)
        mp = col2.selectbox('Matéria-Prima',insumos)
        q = col3.number_input('Quantidade')

        df_novo = pd.DataFrame({"Componente":c,"Matéria-Prima": mp, "Quantidade":q}, index = [produto])

# Adicionando dados ao DataFrame
        if st.form_submit_button('Adicionar'):
            st.session_state.df1 = pd.concat([st.session_state.df1, df_novo], axis=0)
            st.info("Linha adicionada")    

    st.subheader('Em progresso:')
    estrutura = st.data_editor(st.session_state.df1)


# Função que salva DataFrame na memória e realiza os cálculos
    def save(produto,estrutura):
        global estrutura_final
        st.session_state.produto1 = produto
        st.session_state.estrutura = estrutura
        estrutura_final = pd.DataFrame(st.session_state.estrutura)
        estrutura_final = pd.merge(estrutura_final,df_uny1,how='inner',left_on = 'Matéria-Prima',right_on='it-codigo').set_index(estrutura_final.index)
        estrutura_final['Custo Total'] = (estrutura_final['Custo Unitário'] * estrutura_final['Quantidade'])
        estrutura_final = estrutura_final.drop('it-codigo',axis=1)

        st.session_state.estrutura_final = estrutura_final

        state.est_prod = estrutura_final.index
        state.est_comp = estrutura_final['Componente']
        state.est_mp = estrutura_final['Matéria-Prima']
        state.est_quant = estrutura_final['Quantidade']

        add_estrutura(state.estrutura_final)

    col1,col2,col3,col4 = st.columns(4)
    salvar = col1.button('Salvar estrutura', on_click= save, args=(produto,estrutura))
    botao_estrutura = col2.button('Visualizar estrutura')

    if salvar:
            if 'estrutura' in st.session_state and botao_estrutura == False:
                alert = st.success(f'Estrutura do produto {st.session_state.produto1} foi salva')
                time.sleep(1.5) 
                alert.empty()

# Função que mostra estrutura e dá opção de baixar em excel
    def show_estrutura():
        st.write('')
        st.subheader('Estrutura salva:')
        view_estrutura = st.session_state.estrutura_final.copy(deep=True)
        view_estrutura['Custo Total'] = view_estrutura['Custo Total'].apply(lambda x: "R$ {:.2f}".format(x))
        view_estrutura['Custo Unitário'] = view_estrutura['Custo Unitário'].apply(lambda x: "R$ {:.2f}".format(x))
        view_estrutura = view_estrutura.rename_axis('Produto').reset_index()
        st.write(view_estrutura)

        buffer = io.BytesIO()
        if 'estrutura_final' in st.session_state:
            with pd.ExcelWriter(buffer, engine= 'xlsxwriter') as writer:
                st.session_state.estrutura_final.to_excel(writer, sheet_name = f'Estrutura {st.session_state.produto1}')

                writer.close()

                st.download_button(
                    label = "Exportar estrutura",
                    data = buffer.getvalue(),
                    file_name = f'Estrutura {st.session_state.produto1}.xlsx',
                    mime = "application/vnd.ms-excel"
                )

# Aviso caso botão de visualizar estrutura seja clicado antes da realização do cadastro 
    if botao_estrutura:
        if 'estrutura' in st.session_state:
            show_estrutura()
        else:
            st.warning('Nenhuma estrutura foi cadastrada')



