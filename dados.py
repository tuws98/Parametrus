import pandas as pd

df_uny1 = pd.read_csv('postos_unylaser.csv',sep=';',decimal = ',')

print(df_uny1)

postos = df_uny1['Posto Operativo'].value_counts().index

print(postos)