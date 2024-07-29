import streamlit as st
import pandas as pd
from dados import df_uny2
import time
import io
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
from dependencies import consulta_roteiro, add_roteiro, consulta_estrutura

ss = st.session_state

# Configurar página

st.set_page_config(page_title="Roteiro")
st.image('https://parametrus.com.br/wp-content/uploads/2021/07/logo-png-vertical.png',width = 100)
st.title('Roteiros de Produção')
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

# Puxando postos operativos da tabela
postos = df_uny2['Posto Operativo'].value_counts().index

# Componentes cadastrados na estrutura do produto
if 'produto1' in ss:
    estrutura = consulta_estrutura(ss.produto1)
    comp_estrutura = pd.concat([estrutura['item_pai'], estrutura['item_filho']],axis=1)


# Criando DataFrame
if "df3" not in ss:
    ss.df3 = pd.DataFrame(columns=[ 'Componente', 'Posto Operativo', 'Serviço', 'Tempo (h)'])

df2 = pd.DataFrame(columns=['Componente', 'Posto Operativo', 'Tempo (h)' ,'Serviço'])
df2 = df2.astype(dtype= { "Componente":'str',"Posto Operativo":'str', "Serviço":'str', "Tempo (h)":'float64'})

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
    global produto, cadastro
    produto = st.text_input('Insira o código do produto:')
    ss.produto1 = produto  

    # Função pra fazer o botão de cadastro ficar ativo
    if 'dummy' not in ss:
        ss.dummy = False
            
    def click_button():
        ss.dummy = True

    # Botões 
    col1,col2,col3,col4 = st.columns(4)
    cadastro = col1.button('Cadastrar roteiro',on_click= click_button)
    roteiro_completo = col2.button('Roteiro completo')

    if produto == "":
        st.warning('Defina produto')

    if roteiro_completo:
        if 'produto1' in ss:
            st.subheader('Roteiro completo:')
            df_roteiro = consulta_roteiro(ss.produto1)
            df_roteiro = pd.DataFrame(df_roteiro,columns= ['Produto','Componente', 'Posto Operativo', 'Serviço', 'Tempo (h)', 'Custo/h'])
            df_roteiro['Custo Total'] = df_roteiro['Tempo (h)'] * df_roteiro['Custo/h']
            df4 = df_roteiro.copy()
            df_roteiro['Custo Total'] = df_roteiro['Custo Total'].apply(lambda x: "R$ {:.2f}".format(x))
            df_roteiro['Custo/h'] = df_roteiro['Custo/h'].apply(lambda x: "R$ {:.2f}".format(x))
            st.write(df_roteiro)
            st.write('Soma Custo Operacional: R$ {:.2f}'.format(df4['Custo Total'].sum()))
            ss.dummy = False

        else:
            st.warning('Nenhum roteiro foi cadastrado')


# Área de cadastros
def main():
    global roteiro
    if ss.dummy == True:

        st.subheader("Cadastrar roteiro:")

        # Baixar arquivo modelo para preencher
        st.download_button('Download Excel modelo',data = df2_excel,file_name = 'modelo_roteiro.xlsx')

        # Formulário para preenchimento
        with st.form(key="form_3", clear_on_submit= True):


            comp_existente = st.selectbox('Componente',key= 'box_exist',index = None,options= comp_estrutura, placeholder='-')
            col1,col2,col3 = st.columns(3)
            po = col1.selectbox('Posto Operativo',key='po', options = postos, index= None, placeholder= '-')
            serv = col2.selectbox('Serviço Externo',options= ['', 'Pintura', 'Solda'],key= 'serv')
            tempo = col1.number_input('Tempo (h)')

            df_novo = pd.DataFrame({"Componente": comp_existente,"Posto Operativo": po,"Serviço" : serv ,"Tempo (h)": tempo}, index = [produto])
            df_novo = pd.merge(df_novo,df_uny2,how='left',left_on = 'Posto Operativo',right_on='Posto Operativo').set_axis(df_novo.index)

            # Botão de upload do arquivo em Excel
            df_preenchido = pd.DataFrame([])
            uploaded_file = st.file_uploader('Upload',type = 'xlsx')
            if uploaded_file:
                xl_preenchido = pd.read_excel(uploaded_file)
                df_preenchido = pd.DataFrame(xl_preenchido)
                df_preenchido.index = [produto]
                df_preenchido = pd.merge(df_preenchido,df_uny2,how='left',left_on = 'Posto Operativo',right_on='Posto Operativo').set_axis(df_preenchido.index)

    # Adicionando dados ao DataFrame
            add = st.form_submit_button('Adicionar')
            if add:
                ss.df3 = pd.concat([ss.df3, df_novo, df_preenchido], axis=0)
                st.info("Linha adicionada")    


        st.subheader('Em progresso:')
        ss.roteiro = st.data_editor(ss.df3,use_container_width=True, num_rows="dynamic", key= 'df_edit')
        

# Função que salva DataFrame na memória e insere no banco de dados
def save(produto,df):
    global roteiro_final
    ss.produto1 = produto
    roteiro_final = pd.DataFrame(df)
    roteiro_final.reset_index(inplace= True)
    roteiro_final.columns = ['produto','componente','posto_operativo','servico','tempo','custo_h']
    ss.roteiro_final = roteiro_final

    add_roteiro(ss.roteiro_final)
    ss.df3 = pd.DataFrame(columns=['Componente', 'Posto Operativo', 'Serviço', 'Tempo (h)'])

   
# Função principal que inicializa a página

if __name__ == '__main__':
    inicial()
    if ss.dummy and ss.produto1:
        main()
    if 'roteiro' in ss and ss.dummy == True:
        salvar = st.button('Salvar', on_click= save, args=(produto, ss.roteiro))
        if salvar:
            alert = st.success(f'Roteiro do produto {ss.produto1} foi salvo')
            time.sleep(1.5) 
            alert.empty()
        