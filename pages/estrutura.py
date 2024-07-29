import streamlit as st
import pandas as pd
from dados import df_uny1
import time
import io
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
from dependencies import consulta_estrutura, add_estrutura, recur

ss = st.session_state

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
if "df1" not in ss:
    ss.df1 = pd.DataFrame(columns=[ "Item-pai","Item-filho", "Quantidade", "Unidade","Custo Unitário"])

df2 = pd.DataFrame(columns=[ "Item-pai","Item-filho", "Quantidade", "Unidade"])
df2 = df2.astype(dtype= { "Item-pai":'str',"Item-filho":'str', "Quantidade":'float64', "Unidade":'str'})

# Função que converte DataFrame em Excel
def convert_df(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '@'}) 
    worksheet.set_column('A:E', None, format1)  
    writer.close()
    processed_data = output.getvalue()
    return processed_data

df2_excel = convert_df(df2)

# Tela inicial para digitar produto 
def inicial():
    global produto, cadastro, estrutura_recursiva
    produto = st.text_input('Insira o código do produto:')
    ss.produto1 = produto  

    # Função pra fazer o botão de cadastro ficar ativo
    if 'dummy' not in ss:
        ss.dummy = False
            
    def click_button():
        ss.dummy = True

    # Botões 
    col1,col2,col3,col4 = st.columns(4)
    cadastro = col1.button('Cadastrar componente',on_click= click_button)
    estrutura_completa = col2.button('Estrutura completa')
    estrutura_recursiva = col3.button('Custo insumos')
    exportar_excel = col4.button('Exportar estrutura')

    if produto == "":
        st.warning('Defina produto')

    if estrutura_completa:
        if 'produto1' in ss:
            st.subheader('Estrutura completa:')
            df_estrutura = consulta_estrutura(ss.produto1)
            df_estrutura['custo_total'] = (df_estrutura['custo_unitario'] * df_estrutura['quantidade'])
            df_estrutura.set_index('produto',inplace = True)
            df_estrutura['custo_total'] = df_estrutura['custo_total'].apply(lambda x: "R$ {:.2f}".format(x))
            df_estrutura['custo_unitario'] = df_estrutura['custo_unitario'].apply(lambda x: "R$ {:.2f}".format(x))
            st.write(df_estrutura)
            ss.dummy = False

        else:
            st.warning('Nenhuma estrutura foi cadastrada')

    if estrutura_recursiva:
        if 'produto1' in st.session_state:
            st.subheader('Custos por insumos:')
            df_recursiva = recur(ss.produto1)
            df3 = df_recursiva.copy()
            df_recursiva['Custo Total'] = df_recursiva['Custo Total'].apply(lambda x: "R$ {:.2f}".format(x))
            df_recursiva['Custo'] = df_recursiva['Custo'].apply(lambda x: "R$ {:.2f}".format(x))
            df_recursiva.rename(columns = {'Custo' : 'Custo Unitário'},inplace = True)
            df_recursiva = df_recursiva.reset_index(level= 'Insumo')
            st.dataframe(df_recursiva)
            st.markdown('Soma Custo Total : R$ {:.2f}'.format(df3['Custo Total'].sum()))
            ss.dummy = False

        else:
            st.warning('Nenhuma estrutura foi cadastrada')


# Área de cadastros
def main():
    global estrutura
    if ss.dummy == True:

        st.subheader("Criar componente:")

        # Baixar arquivo modelo para preencher
        st.download_button('Download Excel modelo',data = df2_excel,file_name = 'modelo_estrutura.xlsx')

        # Formulário para preenchimento
        with st.form(key="form_2", clear_on_submit= True):

            col1,col2,col3 = st.columns(3)
            c = col1.text_input('Item-pai',key='item_pai')
            pai_existente = col2.selectbox('Procurar item existente',key= 'box_pai',index = None,options= insumos, placeholder='-')
            mp = col1.text_input('Item-filho',key='item_filho')
            filho_existente = col2.selectbox('Procurar item existente',key= 'box_filho',index = None,options= insumos,placeholder='-')
            q_filho = col1.number_input('Quantidade Item-filho')
            unid = col2.text_input('Unidade Item-filho')

            if c == '':
                c = pai_existente
            if mp == '':
                mp = filho_existente

            df_novo = pd.DataFrame({"Item-pai": c,"Item-filho": mp, "Unidade" : unid,"Quantidade":q_filho}, index = [produto])
            df_novo = pd.merge(df_novo,df_uny1,how='left',left_on = 'Item-filho',right_on='it-codigo').set_axis(df_novo.index)
            df_novo = df_novo.drop('it-codigo',axis=1)

            # Botão de upload do arquivo em Excel
            df_preenchido = pd.DataFrame([])
            uploaded_file = st.file_uploader('Upload',type = 'xlsx')
            if uploaded_file:
                xl_preenchido = pd.read_excel(uploaded_file)
                df_preenchido = pd.DataFrame(xl_preenchido)
                produto_index = pd.Series([produto] * len(df_preenchido))
                df_preenchido.index = produto_index
                df_preenchido['Quantidade'] = df_preenchido['Quantidade'].astype(str)
                df_preenchido['Quantidade'] = df_preenchido['Quantidade'].str.replace(',', '.').astype(float)
                df_preenchido = pd.merge(df_preenchido,df_uny1,how='left',left_on = 'Item-filho',right_on='it-codigo').set_axis(df_preenchido.index)
                df_preenchido = df_preenchido.drop('it-codigo',axis=1)

    # Adicionando dados ao DataFrame
            add = st.form_submit_button('Adicionar')
            if add:
                ss.df1 = pd.concat([ss.df1, df_novo, df_preenchido], axis=0)
                ss.df1.fillna(0,inplace= True)
                st.info("Linha adicionada")    


        st.subheader('Em progresso:')
        ss.estrutura = st.data_editor(ss.df1,use_container_width=True, num_rows="dynamic", key= 'df_edit')
        

# Função que salva DataFrame na memória e insere no banco de dados
def save(produto,df):
    global estrutura_final
    ss.produto1 = produto
    estrutura_final = pd.DataFrame(df)
    estrutura_final = estrutura_final.rename_axis('Produto').reset_index()
    estrutura_final.columns = ['produto','item_pai','item_filho','quantidade', 'unidade','custo_unitario']
    ss.estrutura_final = estrutura_final

    add_estrutura(ss.estrutura_final)
    ss.df1 = pd.DataFrame(columns=[ "Item-pai","Item-filho", "Quantidade", "Unidade","Custo Unitário"])

   
# Função principal que inicializa a página

if __name__ == '__main__':
    inicial()
    if ss.dummy and ss.produto1:
        main()
    if 'estrutura' in ss and ss.dummy == True:
        salvar = st.button('Salvar', on_click= save, args=(produto, ss.estrutura))
        if salvar:
            alert = st.success(f'Estrutura do produto {ss.produto1} foi salva')
            time.sleep(1.5) 
            alert.empty()
        

