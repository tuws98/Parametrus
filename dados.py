import pandas as pd


df = pd.read_csv('tabela_imap.csv',sep=';',decimal=',')
print(df)
df.info()