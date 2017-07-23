# For daily update, pass just the market. Code checks <market>.carrydata.csv,
# for the current PRICE and CARRY and updates them in the two files,
# <market>_price.csv and <market>_carrydata.csv
# Check
#   **** both data streams must have equal indexes and must be loaded with equal indexes.
#   **** Report date of last update...

from dbutils.panama import *
import pandas as pd

update_data("EDOLLAR")