import psycopg2, duckdb
import pandas as pd
from dotenv import load_dotenv
import os
from contextlib import contextmanager
from sqlalchemy import create_engine
import streamlit as st
from dados import df_uny1


load_dotenv()
DATABASE = os.getenv('DATABASE')
HOST= os.getenv('HOST')
USERSERVER= os.getenv('USERSERVER')
PASSWORD= os.getenv('PASSWORD')
PORT= os.getenv('PORT')

@contextmanager
def instance_cursor():
    connection = psycopg2.connect(database= DATABASE, host = HOST, user= USERSERVER, password= PASSWORD, port= PORT)
    cursor = connection.cursor()
    try:
        yield cursor
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print('Conexão com Postgres fechada')


def add_estrutura(estrutura_final):
    connection = psycopg2.connect(database= DATABASE, host = HOST, user= USERSERVER, password= PASSWORD, port= PORT)
    conn_string = f"postgresql://{USERSERVER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    connection.autocommit = True

    db = create_engine(conn_string) 
    conn = db.connect()
    cursor = connection.cursor()

    estrutura_final.to_sql('estrutura', con= conn, if_exists='append', index=False)
    query = ''' SELECT * FROM estrutura'''

    cursor.execute(query)
    connection.commit()
    connection.close()

def add_roteiro(nome,user,senha):
    connection = psycopg2.connect(database= DATABASE, host = HOST, user= USERSERVER, password= PASSWORD, port= PORT)
    cursor = connection.cursor()

    query = f'''
        INSERT INTO ROTEIRO VALUES
        {"Produto","Componente","Posto Operativo", "Tempo"}
        '''
    cursor.execute(query)
    connection.commit()
    if (connection):
            cursor.close()
            connection.close()
            print('Conexão com Postgres fechada')

def consulta_estrutura(produto):
    with instance_cursor() as cursor:
        query = f'''
        SELECT *
        FROM estrutura
        WHERE produto = '{produto}'
        '''
        cursor.execute(query,)
        request = cursor.fetchall()
        df1 = pd.DataFrame(request, columns= ['produto','item_pai','item_filho','quantidade'])
        st.write(df1)
    
def consulta_roteiro(produto):
    with instance_cursor() as cursor:
        query = f'''
        SELECT *
        FROM roteiro
        WHERE produto = '{produto}'
        '''
        cursor.execute(query,)
        request = cursor.fetchall()
        df1 = pd.DataFrame(request, columns= [])
        st.write(df1)
    
def recur(produto):
    with instance_cursor() as cursor:
        query = f'''
        SELECT *
        FROM estrutura
        WHERE produto = '{produto}'
        '''
        cursor.execute(query,)
        request = cursor.fetchall()
        df1 = pd.DataFrame(request, columns= ['produto','item_pai','item_filho','quantidade'])


    query_recursiva = duckdb.sql(f''' 
    WITH RECURSIVE paths(produto,startNode, endNode, quant) AS (
    SELECT produto, item_pai AS startNode, item_filho AS endNode, quantidade * 1 AS quant
    FROM df1
    WHERE startNode NOT IN (SELECT item_filho FROM df1)
    UNION ALL
    SELECT 
    df1.produto, paths.startNode AS startNode, item_filho AS endNode, quantidade * paths.quant AS quant
    FROM paths
    JOIN df1 ON paths.endNode = item_pai
    )
    SELECT produto as Produto ,startNode AS Componente, endNode AS Insumo, quant AS Quantidade
    FROM paths
    WHERE endNode NOT IN (SELECT item_pai FROM df1)
    ORDER BY quant;
    ''').df()

    df2 = query_recursiva.groupby(['Produto','Insumo'])['Quantidade'].sum().reset_index(name = 'Quantidade')
    df2 = pd.merge(df2,df_uny1,how='left',left_on = 'Insumo',right_on='it-codigo')
    df2 = df2.drop('it-codigo',axis=1)
    df2['Custo Total'] = (df2['Custo Unitário'] * df2['Quantidade'])
    df2.fillna(0,inplace=True)
    df2['Custo Total'] = df2['Custo Total'].apply(lambda x: "R$ {:.2f}".format(x))
    df2['Custo Unitário'] = df2['Custo Unitário'].apply(lambda x: "R$ {:.2f}".format(x))
    st.write(df2)
    