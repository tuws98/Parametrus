import psycopg2, duckdb
import pandas as pd
from dotenv import load_dotenv
import os
from contextlib import contextmanager
from sqlalchemy import create_engine, text
import streamlit as st
from dados import df_uny1


load_dotenv()
DATABASE = os.getenv('DATABASE')
HOST= os.getenv('HOST')
USERSERVER= os.getenv('USERSERVER')
PASSWORD= os.getenv('PASSWORD')
PORT= os.getenv('PORT')

ss = st.session_state 

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

def add_roteiro(roteiro):
    connection = psycopg2.connect(database= DATABASE, host = HOST, user= USERSERVER, password= PASSWORD, port= PORT)
    conn_string = f"postgresql://{USERSERVER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    connection.autocommit = True

    db = create_engine(conn_string) 
    conn = db.connect()
    cursor = connection.cursor()

    roteiro.to_sql('roteiro', con= conn, if_exists='append', index=False)
    query = ''' SELECT * FROM roteiro'''

    cursor.execute(query)
    connection.commit()
    connection.close()

def consulta_estrutura(produto):
    with instance_cursor() as cursor:
        query = f'''
        SELECT *
        FROM estrutura
        WHERE produto = '{produto}'
        '''
        cursor.execute(query,)
        request = cursor.fetchall()
        df1 = pd.DataFrame(request, columns= ['produto','item_pai','item_filho','quantidade', 'unidade', 'custo_unitario'])
        return df1
        
    
def consulta_roteiro(produto):
    with instance_cursor() as cursor:
        query = f'''
        SELECT *
        FROM roteiro
        WHERE produto = '{produto}'
        '''
        cursor.execute(query,)
        request = cursor.fetchall()
        df1 = pd.DataFrame(request, columns= ['produto','componente','posto_operativo','servico','tempo','custo_h'])
        return df1
    
def recur(produto):
    with instance_cursor() as cursor:
        query = f'''
        SELECT *
        FROM estrutura
        WHERE produto = '{produto}'
        '''
        cursor.execute(query,)
        request = cursor.fetchall()
        df1 = pd.DataFrame(request, columns= ['produto','item_pai','item_filho','quantidade','unidade','custo_unitario'])


    query_recursiva = duckdb.sql(f''' 
    WITH RECURSIVE paths(produto,startNode, endNode, quant, unidade,custo_unitario) AS (
    SELECT produto, item_pai AS startNode, item_filho AS endNode, quantidade * 1 AS quant, unidade, custo_unitario
    FROM df1
    WHERE startNode NOT IN (SELECT item_filho FROM df1)
    UNION ALL
    SELECT 
    df1.produto, paths.startNode AS startNode, item_filho AS endNode, quantidade * paths.quant AS quant,df1.unidade,df1.custo_unitario
    FROM paths
    JOIN df1 ON paths.endNode = item_pai
    )
    SELECT produto as Produto ,startNode AS Componente, endNode AS Insumo, quant AS Quantidade, unidade AS Unidade,custo_unitario AS Custo
    FROM paths
    WHERE endNode NOT IN (SELECT item_pai FROM df1)
    ORDER BY quant;
    ''').df()

    df2 = query_recursiva.groupby(['Produto','Insumo']).agg({'Quantidade':'sum', 'Unidade' : max,'Custo' : 'mean'})
    df2['Custo Total'] = (df2['Custo'] * df2['Quantidade'])
    df2.fillna(0,inplace=True)
    return df2


def del_estrutura(produto):
     with instance_cursor() as cursor:
        connection = psycopg2.connect(database= DATABASE, host = HOST, user= USERSERVER, password= PASSWORD, port= PORT)
        conn_string = f"postgresql://{USERSERVER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
        connection.autocommit = True

        engine = create_engine(conn_string) 
        with engine.connect() as conn:
            query = f'''
            DELETE
            FROM estrutura
            WHERE produto = '{produto}'
            '''
            conn.execute(text(query))
            conn.commit()

def del_roteiro(produto):
     with instance_cursor() as cursor:
        connection = psycopg2.connect(database= DATABASE, host = HOST, user= USERSERVER, password= PASSWORD, port= PORT)
        conn_string = f"postgresql://{USERSERVER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
        connection.autocommit = True

        engine = create_engine(conn_string) 
        with engine.connect() as conn:
            query = f'''
            DELETE
            FROM roteiro
            WHERE produto = '{produto}'
            '''
            conn.execute(text(query))
            conn.commit()

def produtos():
    with instance_cursor() as cursor:
        query = f'''
        SELECT DISTINCT produto
        FROM estrutura
        '''
        cursor.execute(query,)
        request = cursor.fetchall()
        df1 = pd.DataFrame(request, columns= ['produto'])
        lista_produtos = df1['produto']
        return lista_produtos
    
def consulta_postos():
    with instance_cursor() as cursor:
        query = f'''
        SELECT *
        FROM postos
        '''
        cursor.execute(query,)
        request = cursor.fetchall()
        df1 = pd.DataFrame(request, columns= ['Posto Operativo', 'Custo/h'])
        return df1

def add_postos(df):
    connection = psycopg2.connect(database= DATABASE, host = HOST, user= USERSERVER, password= PASSWORD, port= PORT)
    conn_string = f"postgresql://{USERSERVER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    connection.autocommit = True

    db = create_engine(conn_string) 
    conn = db.connect()
    cursor = connection.cursor()

    df.to_sql('postos', con= conn, if_exists='append', index=False)
    query = ''' SELECT * FROM postos'''

    cursor.execute(query)
    connection.commit()
    connection.close()

def del_postos():
     with instance_cursor() as cursor:
        connection = psycopg2.connect(database= DATABASE, host = HOST, user= USERSERVER, password= PASSWORD, port= PORT)
        conn_string = f"postgresql://{USERSERVER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
        connection.autocommit = True

        engine = create_engine(conn_string) 
        with engine.connect() as conn:
            query = f'''
            DELETE
            FROM postos
            '''
            conn.execute(text(query))
            conn.commit()