import streamlit as st
from st_pages import show_pages_from_config, add_page_title
import pandas as pd
from dados import df_uny1
import time
import io
from dependencies import consulta_estrutura, add_estrutura, recur

state = st.session_state

# Configurar página

st.set_page_config(page_title="Estrutura")
st.image('https://parametrus.com.br/wp-content/uploads/2021/07/logo-png-vertical.png',width = 100)
st.title('Estrutura de Produto')
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

# Puxando insumos da tabela
insumos = df_uny1['it-codigo'].value_counts().index

# Criando DataFrame
if "df1" not in st.session_state:
    st.session_state.df1 = pd.DataFrame(columns=[ "Item-pai","Item-filho", "Quantidade"])


# Tela inicial para digitar produto e componente
def inicial():
    global produto, cadastro, estrutura_recursiva
    produto = st.text_input('Insira o código do produto:')
    state.produto1 = produto  

    # Função pra fazer o botão de cadastro ficar ativo
    if 'dummy' not in st.session_state:
        st.session_state.dummy = False
            
    def click_button():
        st.session_state.dummy = True

    # Botões 
    col1,col2,col3,col4 = st.columns(4)
    cadastro = col1.button('Cadastrar novo componente',on_click= click_button)
    estrutura_completa = col2.button('Estrutura completa')
    estrutura_recursiva = col3.button('Visualizar custos')

    if produto == "":
        st.warning('Defina produto')

    if estrutura_completa:
            if 'produto1' in st.session_state:
                st.subheader('Estrutura completa:')
                consulta_estrutura(state.produto1)
                st.session_state.dummy = False
            else:
                st.warning('Nenhuma estrutura foi cadastrada')

    if estrutura_recursiva:
        if 'produto1' in st.session_state:
            st.subheader('Custos por insumos:')
            recur(state.produto1)
            st.session_state.dummy = False
        else:
            st.warning('Nenhuma estrutura foi cadastrada')


# Criando formulário a ser preenchido
def main():
    global estrutura
    if st.session_state.dummy == True:
        st.subheader("Criar componente:")
        with st.form(key="form_2", clear_on_submit= True):

            col1,col2,col3 = st.columns(3)
            c = col1.text_input('Item-pai',key='item_pai')
            pai_existente = col2.selectbox('Procurar item existente',key= 'box_pai',index = None,options= insumos, placeholder='-')
            col1,col2,col3 = st.columns(3)
            mp = col1.text_input('Item-filho',key='item_filho')
            filho_existente = col2.selectbox('Procurar item existente',key= 'box_filho',index = None,options= insumos,placeholder='-')
            q_filho = col3.number_input('Quantidade')

            if c == '':
                c = pai_existente
            if mp == '':
                mp = filho_existente

            df_novo = pd.DataFrame({"Item-pai": c,"Item-filho": mp, "Quantidade":q_filho}, index = [produto])

    # Adicionando dados ao DataFrame
            add = st.form_submit_button('Adicionar')
            if add:
                st.session_state.df1 = pd.concat([st.session_state.df1, df_novo], axis=0)
                st.info("Linha adicionada")    

        st.subheader('Em progresso:')
        state.estrutura = st.data_editor(st.session_state.df1)

# Função que salva DataFrame na memória e insere no banco de dados
def save(produto,df):
    global estrutura_final
    state.produto1 = produto
    estrutura_final = pd.DataFrame(df)
    estrutura_final = estrutura_final.rename_axis('Produto').reset_index()
    estrutura_final.columns = ['produto','item_pai','item_filho','quantidade']
    state.estrutura_final = estrutura_final

    add_estrutura(state.estrutura_final)

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
   
# Função principal que inicializa a página

if __name__ == '__main__':
    inicial()
    if state.dummy and state.produto1:
        main()
    if 'estrutura' in state and state.dummy == True:
        salvar = st.button('Salvar', on_click= save, args=(produto, state.estrutura))
        if salvar:
            alert = st.success(f'Estrutura do produto {st.session_state.produto1} foi salva')
            time.sleep(1.5) 
            alert.empty()
        

# estrutura_final = pd.merge(estrutura_final,df_uny1,how='inner',left_on = 'Item-filho',right_on='it-codigo').set_index(estrutura_final.index)
# estrutura_final['Custo Total'] = (estrutura_final['Custo Unitário'] * estrutura_final['Quantidade'])
# estrutura_final = estrutura_final.drop('it-codigo',axis=1)