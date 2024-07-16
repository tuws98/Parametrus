import psycopg2
from dotenv import load_dotenv
import os
from contextlib import contextmanager
from sqlalchemy import create_engine

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

def consulta_estrutura():
    with instance_cursor() as cursor:
        query = '''
        SELECT *
        FROM ESTRUTURA
        '''
        cursor.execute(query,)
        request = cursor.fetchall()
        return request
    
def consulta_roteiro():
    with instance_cursor() as cursor:
        query = '''
        SELECT *
        FROM ROTEIRO
        '''
        cursor.execute(query,)
        request = cursor.fetchall()
        return request