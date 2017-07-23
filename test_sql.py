from playhouse.csv_loader  import *
import peewee as pw
from peewee import *

db = pw.MySQLDatabase(port=3306, host="0.0.0.0", user="root", passwd="admin", database="pkdemo")

table = load_csv(db,'quandl_history/WHEAT200009.csv')

[print(row.date, row.open, row.high, row.low,  row.settle, row.volume, row.open_interest) for row in table]
