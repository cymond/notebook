
from dbutils.connect import *
import pandas as pd
from sqlalchemy import create_engine

#
engine = create_engine('mysql+pymysql://root:admin@0.0.0.0/pkdemo')
data_path = "data_control/"

# config file
config_file = data_path + "instrumentconfig.csv"
costs_file = data_path + "costs_analysis.csv"
marketdata_file =  "marketdata.csv"

df = pd.read_csv(marketdata_file)
print(df.tail(4))
df.to_sql("marketdata", con=engine, if_exists='replace', index=False)

'''
df = pd.read_csv(config_file)
print(df.tail(4))
df.to_sql("instrumentconfig", con=engine, if_exists='replace', index=False)

df = pd.read_csv(costs_file)
print(df.tail(4))
df.to_sql("costs_analysis", con=engine, if_exists='replace', index=False)

df = pd.read_csv(data_path + "CHFUSDfx.csv")
df.to_sql("CHFUSDfx", con=engine, if_exists='replace', index=False)
df = pd.read_csv(data_path + "AUDUSDfx.csv")
df.to_sql("AUDUSDfx", con=engine, if_exists='replace', index=False)
df = pd.read_csv(data_path + "EURUSDfx.csv")
df.to_sql("EURUSDfx", con=engine, if_exists='replace', index=False)
df = pd.read_csv(data_path + "GBPUSDfx.csv")
df.to_sql("GBPUSDfx", con=engine, if_exists='replace', index=False)
df = pd.read_csv(data_path + "KRWUSDfx.csv")
df.to_sql("KRWUSDfx", con=engine, if_exists='replace', index=False)
df = pd.read_csv(data_path + "JPYUSDfx.csv")
df.to_sql("JPYUSDfx", con=engine, if_exists='replace', index=False)
df = pd.read_csv(data_path + "HKDUSDfx.csv")
df.to_sql("HKDUSDfx", con=engine, if_exists='replace', index=False)

'''

