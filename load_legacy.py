from pandas.io import sql
from sqlalchemy import create_engine
import pandas as pd
from os import listdir
from os.path import isfile, join

legacy_path = "legacycsv/"
legacy_files = [f for f in listdir(legacy_path) if isfile(join(legacy_path, f))]
legacy_files_df = pd.DataFrame(legacy_files, columns=['filename'])
#print(hist_files)
legacy_files_df.sort_values(['filename'],inplace=True)
#print(hist_files_df)
engine = create_engine('mysql+pymysql://root:admin@0.0.0.0/pkdemo')


#Read from csv file and load data into a dataframe using
# DataFrame.to_sql

for row in legacy_files_df.itertuples():

    #print(row.filename)
    df = pd.read_csv(legacy_path + row.filename, dtype={'CARRY_CONTRACT': str, 'PRICE_CONTRACT': str})
    #print(df.tail(2))
    #print("-----------------------------------------------------")

    table_name = "z_"+row.filename[:-4].lower()
    df.reset_index()
    print("z_"+row.filename[:-4].lower())
    df.to_sql(name=table_name, con=engine, if_exists='replace',index=False)

