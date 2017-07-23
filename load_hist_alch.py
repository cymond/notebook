'''
* Pete
* 20170507
*
*
'''
from pandas.io import sql
from sqlalchemy import create_engine
import pandas as pd
from os import listdir
from os.path import isfile, join

hist_path = "admin/downloads/quandl_history/"
hist_files = [f for f in listdir(hist_path) if isfile(join(hist_path, f))]
hist_files_df = pd.DataFrame(hist_files, columns=['filename'])
#print(hist_files)
hist_files_df.sort_values(['filename'],inplace=True)
#print(hist_files_df)
engine = create_engine('mysql+pymysql://root:admin@0.0.0.0/pkdemo')


#Read from csv file and load data into a dataframe using
# DataFrame.to_sql

for row in hist_files_df.itertuples():
    if row.filename == 'EDOLLAR202006.csv':
        print(row.filename)
        df = pd.read_csv(hist_path + row.filename)
        df2 = df[['Date','Settle']]
        print(df2.tail(2))
        #print(df2.head(2))
        df2.to_sql(name=row.filename[:-4].lower(), con=engine, if_exists='replace',index=False)
