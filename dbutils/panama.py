from accessrights import q_access_key
import quandl
import pandas as pd
from wrapper_v2 import IBWrapper, IBclient
from swigibpy import Contract as IBcontract
import os
import numpy as np
source_path = "quandl_history/"
destination_path = "data/"

def pretty_print(title, dtFrame, nhead, ntail):
    print()
    if nhead > 0:
        print("Head --------------------------------------------------------------------------")
        print( title)
        print(dtFrame.head(nhead))

    if ntail > 0:
        print("Tail --------------------------------------------------------------------------")
        print(title)
        print(dtFrame.tail(ntail))
        print("-------------------------------------------------------------------------------")
    print()

def get_code_from_month(m):
    return {
        '01': 'F',
        '02': 'G',
        '03': 'H',
        '04': 'J',
        '05': 'K',
        '06': 'M',
        '07': 'N',
        '08': 'Q',
        '09': 'U',
        '10': 'V',
        '11': 'X',
        '12': 'Z'
    }[m]

def get_qndl_string(mkt_ser,maturity):
    '''
    :param mkt_ser: Series with elements {CARVER,QUANDL,IB,SECTYPE,CURRENCY,Q_EXCHANGE,IB_EXCHANGE,MULTIPLIER}
    :param maturity:  e.g. 201803
    :return: String to sent to Quandl API
    >>> data=mysqlFuturesData()
    >>> data._get_all_cost_data()
    '''
    year = str(maturity)[:4]
    month = str(maturity)[4:6]
    month_code = get_code_from_month(month)
    symbol = mkt_ser['QUANDL']
    exchange = mkt_ser['Q_EXCHANGE']
    api_call_head = '{}/{}{}{}'.format(exchange, symbol, month_code, year)
    return api_call_head

def get_ib_contract(mkt_ser,maturity):
    '''
    :param mkt_ser: Series with elements {CARVER,QUANDL,IB,SECTYPE,CURRENCY,Q_EXCHANGE,IB_EXCHANGE,MULTIPLIER}
    :param maturity:  e.g. 201803
    :return: Contract to send to IB API
    '''

    ib_multiplier = mkt_ser['MULTIPLIER']
    ib_security_type = mkt_ser['SECTYPE']
    ib_exchange = mkt_ser['IB_EXCHANGE']
    ibcontract = IBcontract()
    ibcontract.symbol = mkt_ser['IB']
    ibcontract.secType = ib_security_type # Security Type

    ibcontract.currency = mkt_ser['CURRENCY']  # Currency
    ibcontract.exchange = ib_exchange  # Exchange
    if ib_multiplier > 0:
        ibcontract.multiplier = str(ib_multiplier)
    if ib_security_type == 'FUT':
        ibcontract.expiry = maturity
        ibcontract.includeExpired = True
    return ibcontract

def ib_download(client, mkt_ser, maturity,**kwargs):
    start_date = kwargs.get('start_date')
    counter = 100
    ibcontract = get_ib_contract(mkt_ser, maturity)
    if ibcontract.secType == 'CASH':
        ibcontract.primaryExchange = ibcontract.exchange
        result = client.get_IB_historical_data(ibcontract, "2 D", "1 hour", counter, "MIDPOINT")
        result.rename(columns={0:'DATETIME',\
                              'close':'FX'}, inplace=True)
        result.index.names = ['DATETIME']
        result = result[['FX']]

    else:
        result = client.get_IB_historical_data(ibcontract, "1 M", "1 day", counter)
        result.rename(columns={'Date': 'DATETIME', \
                               'Trade Date': 'DATETIME', \
                               'Prev. Day Open Interest': 'Open Interest', \
                               'Total Volume': 'Volume', \
                               'close': 'PRICE', \
                               'Current Price': 'PRICE'}, inplace=True)
        result.index.names = ['DATETIME']
        result = result[['PRICE']]
    return result


def qndl_download(mkt_ser, maturity, **kwargs):
    from dateutil.relativedelta import relativedelta
    start_date = kwargs.get('start_date')
    auth_token = q_access_key()
    api_call_head = get_qndl_string(mkt_ser, maturity)
    result = quandl.get(api_call_head, returns="pandas", authtoken=auth_token, start_date=start_date)
    # result = quandl.get(api_call_head, returns="pandas", authtoken=auth_token)
    # re = quandl.get
    # rename to Dates to DATETIME
    # and to Settle
    #print(result)
    result.rename(columns={'Date': 'DATETIME', \
                           'Trade Date': 'DATETIME', \
                           'Prev. Day Open Interest': 'Open Interest', \
                           'Total Volume': 'Volume', \
                           'Settle': 'PRICE', \
                           'Current Price': 'PRICE'}, inplace=True)
    result.index.names = ['DATETIME']
    result.reset_index(inplace=True)
    result['DATETIME'] = result['DATETIME'].apply(lambda x: x + relativedelta(hours=23))
    result.set_index(['DATETIME'],inplace=True)
    frame = result[['PRICE']]
    return frame

def q_download(engine, symbol, maturity,**kwargs):

    start_date = kwargs.get('start_date')
    auth_token = q_access_key()
    marketdata_df = pd.read_sql_table(table_name="marketdata", con=engine,index_col='CARVER')
    #market_info = marketdata_df[marketdata_df['CARVER']== symbol]
    #carver_sym = symbol
    quandl_sym = marketdata_df.loc[symbol]['QUANDL']
    quandl_exchange = marketdata_df.loc[symbol]['Q_EXCHANGE']
    month = str(maturity)[4:6]
    year = str(maturity)[:4]
    code = get_code_from_month(month)
    api_call_head = '{}/{}{}{}'.format(quandl_exchange, quandl_sym, code, year)
    result = quandl.get(api_call_head, returns="pandas", authtoken=auth_token, start_date=start_date)
    #result = quandl.get(api_call_head, returns="pandas", authtoken=auth_token)
    #re = quandl.get
    # rename to Dates to DATETIME
    # and to Settle
    result.rename(columns={'Trade Date': 'Date', \
                           'Prev. Day Open Interest': 'Open Interest', \
                           'Total Volume': 'Volume', \
                           'Current Price': 'Settle'}, inplace=True)
    result.index.names = ['Date']
    frame  = result[['Settle']]
    return frame

def splice_price(base_df,new_df,date):
    import datetime

    # Panama splice the two dataframes together on 'date' and return the spliced df
    # First, determine delta between the 2 dfs on the splice date
    # There may be one price or several intra-day prices, BUT the splice is done on the last price of day
    next_day = date + datetime.timedelta(1)

    basedf_mask = (base_df.index >= date) & (base_df.index < next_day)
    basedf_date = base_df.index[basedf_mask][-1]
    newdf_mask = (new_df.index >= date) & (new_df.index < next_day)
    newdf_date = new_df.index[newdf_mask][-1]


    delta = new_df.loc[newdf_date][0] - base_df.loc[basedf_date][0]
    #print("delta: ", delta)
    # Add this delta to pan_df stream
    # and truncate both dfs at splice date...

    #print(base_df[:date][:-1].tail(5))
    base_df['PRICE'] = base_df['PRICE'] + delta
    #print(base_df[:date][:-1].tail(5))
    appended_df = new_df[newdf_date:].copy()
    price_df = base_df[:newdf_date][:-1]
    #print("price: ", len(price_df))
    price_df = price_df.append(appended_df).round({'PRICE':10})
    return price_df

def splice_carry(base_df, new_price, new_carry, price_mat, carry_mat, date):
    import datetime
    next_day = date + datetime.timedelta(1)

    basedf_mask = (base_df.index >= date) & (base_df.index < next_day)
    basedf_date = base_df.index[basedf_mask][-1]
    new_price_mask = (new_price.index >= date) & (new_price.index < next_day)
    new_price_date = new_price.index[new_price_mask][-1]

    new_carry_mask = (new_carry.index >= date) & (new_carry.index < next_day)
    new_carry_date = new_carry.index[new_carry_mask][-1]

    new_price = new_price[new_price_date:].copy()
    new_carry = new_carry[new_carry_date:].copy()

    append_df = pd.concat([new_price, new_carry], axis=1)
    append_df.columns = ["PRICE", 'CARRY']
    append_df["CARRY_CONTRACT"] = carry_mat
    append_df["PRICE_CONTRACT"] = price_mat
    carry_df = base_df[:new_price_date][:-1]
    #print(append_df.tail(5))
    #print(carry_df.tail(5))
    #print("price: ", len(carry_df))
    carry_df = carry_df.append(append_df)
    carry_df.index.names = ['DATETIME']
    carry_df = carry_df[pd.notnull(carry_df['PRICE'])]
    return carry_df

def getIBContract(engine, market, curr_contract):
    '''
        :param engine:
        :param market:
        :param contract:
        :return:
        IB should return latest intra-day data plus settlement price from yesterday if not available
        1. retrieve database raw data...
        2. Check if newer rows in quandl
        3. Update database with newer rows
        4. return the entire current raw data
        2. Update database table.
        '''
    price_string = 'Settle'
    to_save = False
    table = market.lower() + str(curr_contract)
    try:
        contract_df = pd.read_sql_table(table_name=table, \
                                        con=engine, index_col=['Date'], \
                                        parse_dates=['Date'])
    except Exception as e:
        print(table, "is not in the database!")
        contract_df = ib_download(engine, market, curr_contract)

def prev_weekday(adate):
    from datetime import date, timedelta
    adate -= timedelta(days=1)
    while adate.weekday() > 4: # Mon-Fri are 0-4
        adate -= timedelta(days=1)
    return adate

def check_data_ok(maturity, df, start_date, end_date, match):
    # Will raise an error if splice date that's supposed to be in df is missing (for match = True)
    # Called after a call to quandl or IB
    import datetime
    if not pd.isnull(start_date):
     #
        if start_date.hour == 23:
            start_date_alt = datetime.datetime(start_date.year, start_date.month, start_date.day, 0)
        if start_date.hour == 0:
            start_date_alt = datetime.datetime(start_date.year, start_date.month, start_date.day, 23)

    if not pd.isnull(end_date):
     #
        if end_date.hour == 23:
            end_date_alt = datetime.datetime(end_date.year, end_date.month, end_date.day, 0)
        if end_date.hour == 0:
            end_date_alt = datetime.datetime(end_date.year, end_date.month, end_date.day, 23)
    temp_df = df.copy()
    temp_df['HOURS'] = temp_df.index.map(lambda x: x.hour)
    closing_prices = temp_df[(temp_df['HOURS'] == 0) | (temp_df['HOURS'] == 23)]
    last_settlement_date = closing_prices[-1:].index[0]

    if match:
        # Check if splice dates that should be in temp_df are... propagate an error if missing
        if start_date != "NaT":
            if start_date.date() < last_settlement_date.date() and not \
                    (start_date in df.index or start_date_alt in df.index):
                assert False, maturity + ": Start splice date is missing in database data"
        if end_date != "NaT":
            if end_date.date() < last_settlement_date.date() and not \
                    (end_date in df.index or end_date_alt in df.index):
                assert False, maturity + ": End splice date is missing in database data"
    return True
    '''
    today_asdate = datetime.date.today()
    last_bday = prev_weekday(today_asdate)
    last_bday_r23 = datetime.datetime(last_bday.year, last_bday.month, last_bday.day, 23)
    if last_bday == last_settlement_date or last_bday_r23 == last_settlement_date:   # Downloads up to date
        return True # Data is up to date caller should return df upstream

    return False  # Data is not up to date... download data
    '''

def get_raw_data_initialize(engine, mkt_ser, maturity, start_date, end_date, match):
    '''

    :param engine: connection to mysql database
    :param mkt_ser: symbol with quandl and IB market descriptive info
    :param maturity:
    :param start_date: date maturity starts in panama stream
    :param end_date: date the next maturity starts in panama stream. The current maturity is only used to calculate delta
    :param match:
    :param initialize:
    :return:
    '''
    import datetime
    symbol = mkt_ser['CARVER']
    table = symbol.lower() + maturity
    print("Downloading symbol: ", symbol, "maturity: ", maturity)
    try:
        quandl_df = qndl_download(mkt_ser, maturity)
        new_df = quandl_df
        quandl_request = True
        #print(quandl_df.tail(4))
    except Exception as e:
        print(e, maturity, "Can not download data from quandl ")
    else:
        # Ensure match if required
        if check_data_ok(symbol, quandl_df, start_date, end_date, match):
            to_store_df = new_df.copy()
            to_store_df.reset_index(inplace=True)
            to_store_df.to_sql(name=table, con=engine, if_exists='replace', index=False)

            return quandl_df


def get_raw_data_update(engine, mkt_ser, maturity, start_date, end_date, match):

    # First check whether database data is up to date with daily updates... (i.e. from quandl)
    # Must consider Business Day (ignore Holidays during processing...)

    import datetime
    if not pd.isnull(start_date):
        #
        if start_date.hour == 23:
            start_date_alt = datetime.datetime(start_date.year, start_date.month, start_date.day, 0)
        if start_date.hour == 0:
            start_date_alt = datetime.datetime(start_date.year, start_date.month, start_date.day, 23)

    if not pd.isnull(end_date):
        #
        if end_date.hour == 23:
            end_date_alt = datetime.datetime(end_date.year, end_date.month, end_date.day, 0)
        if end_date.hour == 0:
            end_date_alt = datetime.datetime(end_date.year, end_date.month, end_date.day, 23)

    db_request = False
    quandl_request = False
    ib_request = False

    # Get PRICE mat
    symbol = mkt_ser['CARVER']
    table = symbol.lower() + maturity

    # Check for local database storage of raw data
    try:
        table_df = pd.read_sql_table(table_name=table, \
                                     con=engine, index_col=['DATETIME'], \
                                     parse_dates=['DATETIME'])


    except Exception as e:
        # If error, announce and get data from quandl or IB
        print(table, e, "Error when getting table from database!")
    else:
        # If table exists, check whether the startdate and enddate are available in the database
        # If so no downloads required from Quandl
        # Checks that the splice dates, start_date and end_date, if in the past, are available if any later dates are contained
        # in the database or downloaded data. If not the program should skip that market

        temp_df = table_df.copy()
        temp_df['HOURS'] = temp_df.index.map(lambda x: x.hour)
        closing_prices = temp_df[(temp_df['HOURS'] == 0) | (temp_df['HOURS'] == 23) ]
        last_settlement_date = closing_prices[-1:].index[0]
        db_request = True
        if last_settlement_date >= end_date:
            if match:
                if start_date != "NaT":
                    if start_date.date() < last_settlement_date.date() and not \
                            (start_date in table_df.index or start_date_alt in table_df.index):
                        assert False, maturity + ": Start splice date is missing in database data"
                if end_date != "NaT":
                    if end_date.date() < last_settlement_date.date() and not \
                            (end_date in table_df.index or end_date_alt in table_df.index):
                        assert False, maturity + ": End splice date is missing in database data"
                return table_df
            else:
                return table_df
    finally:

        try:
            quandl_df = qndl_download(mkt_ser, maturity)
            new_df = quandl_df
            quandl_request = True
            #print(quandl_df.tail(4))
        except Exception as e:
            print(e, maturity, "Can not download data from quandl ")
            assert False, maturity
        else:
            if db_request:
                new_df = table_df.append(quandl_df[last_settlement_date:][1:])
            else:
                new_df = quandl_df
            if check_data_ok(symbol, new_df, start_date, end_date, match):
                try:
                    to_store_df = new_df.copy()
                    to_store_df.reset_index(inplace=True)
                    to_store_df.to_sql(name=table, con=engine, if_exists='replace', index=False)
                except:
                    print("Can't access database", table)
                    assert False, "Check database..."
                return new_df

def get_active_price_and_carry(engine, mkt_ser):
    symbol = mkt_ser['CARVER']
    price_table = symbol.lower() + "_price"
    carrydata_table = symbol.lower() + "_carrydata"

    # Determine if the contracts to add are already in
    try:
        price_df = pd.read_sql_table(table_name=price_table, con=engine, \
                                     index_col=['DATETIME'], parse_dates=['DATETIME'], \
                                     columns=['PRICE'])
    except Exception as e:
        print("Cant access table: ", carrydata_table, ": skipping market: ",symbol)
        return(None,None)
    try:
        carry_df = pd.read_sql_table(table_name=carrydata_table, con=engine, \
                                     index_col=['DATETIME'], \
                                     columns=[ 'PRICE', 'CARRY' , 'CARRY_CONTRACT', 'PRICE_CONTRACT'], \
                                     parse_dates=['DATETIME'])
    except Exception as e:
        print("Can't access table: ", price_table, ": skipping market: ",symbol)
        return(None, None)
    #curr_price_contract = carry_df[-1:]['PRICE_CONTRACT'][0]
    return (price_df,carry_df)

def set_active_price_and_carry(engine, mkt_ser, price_df, carry_df):
    symbol = mkt_ser['CARVER']
    price_table = symbol.lower() + "_price"
    carrydata_table = symbol.lower() + "_carrydata"

    price_df.reset_index(inplace=True)
    try:
        price_df.to_sql(name=price_table, con=engine, if_exists='replace', index=False)
    except:
        print("Can't access database", price_table)
        assert False, "Check database..."

    carry_df.reset_index(inplace=True)
    try:
        carry_df.to_sql(name=carrydata_table, con=engine, if_exists='replace', index=False)
    except:
        print("Can't access database", carrydata_table)
        assert False, "Check database..."

def get_splice_data(engine, mkt_ser, row, initialize):
    import datetime

    carry_mat = str(row.CARRY_CONTRACT)
    price_mat = str(row.PRICE_CONTRACT)
    start_date = row.DATETIME
    end_date = row.END_DATETIME
    today = datetime.datetime.now()
    if not "end_date" in locals():
        end_date = today

    if initialize:
        price_df = get_raw_data_initialize(engine, mkt_ser,price_mat, start_date, end_date, True)
        carry_df = get_raw_data_initialize(engine, mkt_ser, carry_mat, start_date, end_date, False)
    else:

        price_df = get_raw_data_update(engine, mkt_ser, price_mat, start_date, end_date, True)
        carry_df = get_raw_data_update(engine, mkt_ser, carry_mat, start_date, end_date, False)


    return(price_df,carry_df)



def check_raw_data_downloads_v2(engine, mkt_ser, rolls, initialize):
    '''
    :param engine:
    :param mkt_ser:
    :param rolls:
    :return: list of CARRY & PRICE dataframes corresponding to each splice date
    # For past maturities, only check that start and end dates are available for PRICE and CARRY
    #   Attempt to download both from Quandl
    #   Assert error if still a PRICE splice date is missing.
    # For present and future maturities
    #   Get the latest data up to yesterday
    #   For PRICE matuirty get up to the minute data
    #   Assert error if a start data in the past is missing
    #   Ignore future splice dates
    '''

    import datetime
    symbol = mkt_ser['CARVER']
    rolls_copy = rolls.copy()
    rolls_copy['END_DATETIME'] = rolls_copy['DATETIME']
     # Make copy to upshift END_DATETIME
    rolls_copy.END_DATETIME = rolls_copy.END_DATETIME.shift(-1)
    list = []
    for row in rolls_copy.itertuples():
        # get_splice_mats(row)
        (price_df, carry_df) = get_splice_data(engine, mkt_ser, row, initialize)
        list.append([row, price_df, carry_df])
    return list



def initialize_series(engine, mkt_ser, rolls ):
    import datetime
    initialize = True
    list = check_raw_data_downloads_v2(engine, mkt_ser, rolls, initialize)
    # list has list of [schedule, price_df, carry_df] where schedule is (DATETIME, CARRY_CONTRACT & PRICE_CONTRACT)
    # First row is base
    today_asdate = datetime.date.today()
    today_asdatetime = datetime.datetime(today_asdate.year, today_asdate.month, today_asdate.day)
    count = 0
    coll = []

    for row in list:
        splice_date = row[0].DATETIME
        if splice_date < today_asdatetime:
            price_mat = row[0].PRICE_CONTRACT
            carry_mat = row[0].CARRY_CONTRACT
            #### **** AttributeError: 'NoneType' object has no attribute 'resample'
            #print("Price mat: ", price_mat)
            #print("Carry mat: ", carry_mat)
            price_df = row[1].resample("B").last()
            carry_df = row[2].resample("B").last()
            if count == 0:
                # initialize splice
                spliced_price = price_df
                spliced_carry = pd.concat([price_df, carry_df], axis=1)
                spliced_carry.columns = ["PRICE", 'CARRY']
                #spliced_carry = carry_df[pd.notnull(carry_df['PRICE'])]
                spliced_carry["CARRY_CONTRACT"] = carry_mat
                spliced_carry["PRICE_CONTRACT"] = price_mat
                spliced_carry.index.names = ['DATETIME']
                #print("Roll number: ", count + 1, " Splice date: ", splice_date)
                pretty_print("Roll number: " + str(count + 1) + " Splice date: " + str(splice_date) + " Price maturity: " + price_mat, spliced_price, 0, 5)
                pretty_print("Roll number: " + str(count + 1) + " Splice date: " + str(splice_date) + " Carry maturity: " + carry_mat, spliced_carry, 0, 5)
            else:
                spliced_price = splice_price(spliced_price, price_df, splice_date)
                spliced_carry = splice_carry(spliced_carry, price_df, carry_df, price_mat, carry_mat, splice_date)
                pretty_print("Roll number: " +  str(count + 1) +" Splice date: " + str(splice_date) + " Price maturity: " + price_mat, spliced_price, 0, 5)
                pretty_print("Roll number: " + str(count + 1) +" Splice date: " + str(splice_date) + " Carry maturity: " + carry_mat, spliced_carry, 0, 5)
            count += 1
    if count > 0:
        print("****************************************************************************")
        spliced_price.to_csv("panama_price_file.csv")
        spliced_carry.to_csv("panama_carry_file.csv")
        # Set the database table
        set_active_price_and_carry(engine, mkt_ser, spliced_price, spliced_carry)

        print("************************", count, " usable roll/s ******************************")
        pretty_print("Current price mat: " + price_mat, spliced_price, 0, 5)
        pretty_print("Current carry mat: " + carry_mat, spliced_carry, 0, 5)
        print("********************************************************************************")

        coll.append(spliced_price)
    return coll

def update_current_maturities(row, curr_price, curr_carry):

    # First get the current price and carry series, update them with current mat
    # and return the two as a tuple...
    import datetime

    price_mat = row[0].PRICE_CONTRACT
    carry_mat = row[0].CARRY_CONTRACT
    price_df = row[1].resample("B").last()
    carry_df = row[2].resample("B").last()
    temp_df = curr_price.copy()
    temp_df['HOURS'] = temp_df.index.map(lambda x: x.hour)
    closing_prices = temp_df[(temp_df['HOURS'] == 0) | (temp_df['HOURS'] == 23)]
    last_settlement_date = closing_prices[-1:].index[0]
    price_toadd = price_df[last_settlement_date:][1:]
    if len(price_toadd) > 0:
        end_date = price_toadd[-1:].index[0]
        end_date_r1d = end_date + datetime.timedelta(1)
        new_price_df = curr_price.append(price_df[last_settlement_date:][1:])

        carry_toadd = carry_df[last_settlement_date:end_date_r1d][1:]
        carry_toadd = pd.concat([price_toadd, carry_toadd], axis=1)
        carry_toadd.columns = ["PRICE", 'CARRY']
        # spliced_carry = carry_df[pd.notnull(carry_df['PRICE'])]
        carry_toadd["CARRY_CONTRACT"] = carry_mat
        carry_toadd["PRICE_CONTRACT"] = price_mat
        carry_toadd.index.names = ['DATETIME']
        new_carry_df = curr_carry.append(carry_toadd)
        return (new_price_df, new_carry_df)  ## return updated series..
    return(curr_price, curr_carry) ## no new updates - simply return inputs


def get_curr_rolls_and_mats(mkt_ser, rolls, curr_carry_df):

    import datetime

    curr_price_mat = curr_carry_df[-1:].iloc[0]['PRICE_CONTRACT']
    curr_carry_mat = curr_carry_df[-1:].iloc[0]['CARRY_CONTRACT']
    last_splice_datetime = curr_carry_df[curr_carry_df['PRICE_CONTRACT'] == curr_price_mat][0:1].index[0]
    last_splice_date = datetime.datetime(last_splice_datetime.year, last_splice_datetime.month,
                                         last_splice_datetime.day)

    found = False
    for row in rolls.itertuples():
        if row.DATETIME == last_splice_date:
            found = True
    if found:
        usable_rolls = rolls[(rolls['DATETIME'] > last_splice_date)]
    else:
        usable_rolls = rolls[(rolls['DATETIME'] != rolls['DATETIME'])] # empty dataframe, no rolling
    return(usable_rolls, curr_price_mat, curr_carry_mat)

def update_series(engine, mkt_ser, rolls ):
    '''
    :param engine:
    :param mkt_ser:
    :param rolls:
    :return: list of spliced PRICE and CARRY streams
    Assumes PRICE and CARRY streams are in the database engine. Use rolls to determine missing entries and perform
    updates and any required stitching
    '''
    # 1. Find current price and carry mats (curr_price_mat, curr_carry_mat) - current active roll
    # 2. from active roll, determine any due rolls..
    # 3. Update raw data
    # 4. Update current roll
    # 5. Update any other due rolls

    import datetime
    from collections import namedtuple
    # Check the current PRICE and CARRY... if none exist, skip the symbol
    (curr_price_df, curr_carry_df) = get_active_price_and_carry(engine,mkt_ser)
    if not isinstance(curr_price_df, pd.DataFrame) or not isinstance(curr_carry_df, pd.DataFrame):
        return

    # From CARRY stream determine the current PRICE and CARRY contracts and the usable_rolls
    (usable_rolls, curr_price_mat, curr_carry_mat) = get_curr_rolls_and_mats(mkt_ser, rolls, curr_carry_df)

    # **************************************************************************************
    # UPDATE Current maturities
    #  Get all raw data for PRICE and CARRY contracts and then update current maturities
    # **** This corresponds to raw data for DAILY UPDATES!!!!
    # ... download contracts from Quandl/IB
    q_price_df = get_raw_data_initialize(engine, mkt_ser, curr_price_mat, None, None, False)
    q_carry_df = get_raw_data_initialize(engine, mkt_ser, curr_carry_mat, None, None, False)
    myNamedTuple = namedtuple('myNamedTuple', 'PRICE_CONTRACT CARRY_CONTRACT')
    maturities = myNamedTuple(curr_price_mat, curr_carry_mat)
    arr = [maturities, q_price_df, q_carry_df]
    # Add the latest updates... new series 'spliced..' are now ready for any splicing
    pretty_print("Current price mat: " + curr_price_mat, curr_price_df, 0, 5)
    pretty_print("Current carry mat: " + curr_carry_mat, curr_carry_df, 0, 5)
    (spliced_price, spliced_carry) = update_current_maturities(arr, curr_price_df, curr_carry_df)
    # *****************************************************************************************



    # **************************************************************************************
    # PERFORM any due rolls
    # 1. Update any data not up to date in database. Return a list of all
    # 2.
    initialize = False
    list = check_raw_data_downloads_v2(engine, mkt_ser, usable_rolls, initialize)
    count = 0
    today_asdate = datetime.date.today()
    today_asdatetime = datetime.datetime(today_asdate.year, today_asdate.month, today_asdate.day)
    for row in list:
        splice_date = row[0].DATETIME


        price_mat = row[0].PRICE_CONTRACT
        carry_mat = row[0].CARRY_CONTRACT
        price_df = row[1].resample("B").last()
        carry_df = row[2].resample("B").last()
        #if count == 0 :
        #    (spliced_price, spliced_carry) = update_current_mat(row , curr_price_df, curr_carry_df)

        if splice_date < today_asdatetime:
            spliced_price = splice_price(spliced_price, price_df, splice_date)
            spliced_carry = splice_carry(spliced_carry, price_df, carry_df, price_mat, carry_mat, splice_date)
            pretty_print("Roll number: "+ str(count + 1) +" Splice date: " + str(splice_date) +" Price maturity: " + curr_price_mat, spliced_price, 0, 5)
            pretty_print("Roll number: "+ str(count + 1) +" Splice date: " + str(splice_date) +" Carry maturity: " + curr_carry_mat, spliced_carry, 0, 5)
            count += 1

    print("****************************************************************************")
    if count > 0:
        print("*************************",count," usable roll/s *************************")
        pretty_print("Current price mat: " + curr_price_mat, spliced_price, 0, 5)
        pretty_print("Current carry mat: " + curr_carry_mat, spliced_carry, 0, 5)
        print("****************************************************************************")
    else:
        print("************************ NO usable rolls! ********************************")
        print("Price mat:", curr_price_mat)
        pretty_print("Current price mat: " + curr_price_mat, spliced_price, 0, 5)
        pretty_print("Current carry mat: " + curr_carry_mat, spliced_carry, 0, 5)
        print("****************************************************************************")

    # Set the database table
    set_active_price_and_carry(engine, mkt_ser, spliced_price, spliced_carry)




























































































