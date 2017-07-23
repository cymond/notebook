import pytest
import pandas as pd

@pytest.fixture(scope='module')

def resource_marketdata_setup(request):
    '''
    :param request:
    :return: engine
    '''
    from sqlalchemy import create_engine
    from wrapper_v2 import IBWrapper, IBclient

    #engine = create_engine('mysql+pymysql://root:admin@0.0.0.0/pkdemo')
    callback = IBWrapper()
    client = IBclient(callback)
    market_series = pd.Series({"QUANDL":"ED","IB":"GE","SECTYPE":"FUT","CURRENCY":"USD",
                                "Q_EXCHANGE" :"CME","IB_EXCHANGE" :"GLOBEX","MULTIPLIER":0})
    engine = 1
    return (engine, client, market_series)

@pytest.fixture(scope='module')

def resource_roll_setup(request):
    from sqlalchemy import create_engine
    engine = create_engine('mysql+pymysql://root:admin@0.0.0.0/pkdemo')
    roll_schedule_df = pd.read_sql_table(table_name="roll_schedule", con=engine)
    roll_df = roll_schedule_df[roll_schedule_df['CARVER'] == 'EDOLLAR'][-8:-5]
    market_series = pd.Series({"CARVER":"EDOLLAR","QUANDL": "ED", "IB": "GE", "SECTYPE": "FUT", "CURRENCY": "USD",
                         "Q_EXCHANGE": "CME", "IB_EXCHANGE": "GLOBEX", "MULTIPLIER": 0})

    return(engine, market_series, roll_df)


def test_quandl_string(resource_marketdata_setup):
    '''
    :param resource_marketdata_setup:
    :return:
    '''
    from dbutils.panama import get_qndl_string
    maturity = '201803'
    (eng, clnt, mkt_ser) = resource_marketdata_setup
    api_call_string = get_qndl_string(mkt_ser,maturity)
    assert api_call_string == 'CME/EDH2018'


def test_ib_contract(resource_marketdata_setup):
    '''

    :param resource_marketdata_setup:
    :return:
    '''

    from dbutils.panama import get_ib_contract
    maturity = '201803'
    mkt_ser = pd.Series({"IB": "KRW", "SECTYPE": "CASH", "CURRENCY": "USD",
                         "IB_EXCHANGE": "IDEALPRO", "MULTIPLIER": 0})
    ibcontract = get_ib_contract(mkt_ser, maturity)
    print("Expiry: ", ibcontract.expiry)
    print("Symbol: ", ibcontract.symbol)
    assert ibcontract.symbol == 'KRW'


def test_qndl_download(resource_marketdata_setup):
    '''

    :param resource_marketdata_setup:
    :return:

    '''
    from dbutils.panama import qndl_download
    start_date = '20170605'
    maturity = '201803'
    (eng, clnt, mkt_ser) = resource_marketdata_setup
    result = qndl_download(mkt_ser, maturity, start_date=start_date)
    print("-----------------")
    print("Start date: ",start_date)
    print("Result head....")
    print(result.head(5))
    assert len(result) > 0

def test_ib_download_futures(resource_marketdata_setup):
    '''

    :param resource_market_setup:
    :return:
    '''
    from dbutils.panama import ib_download
    (eng, client, mkt_ser) = resource_marketdata_setup

    ## Get the hourly EuroDollar prices, last two days for the EuroDollar Dec2017 contract....

    start_date = '20160605'
    maturity = '201712'
    #mkt_ser = resource_marketdata_setup
    mkt_ser  = pd.Series({"QUANDL": "ED", "IB": "GE", "SECTYPE": "FUT", "CURRENCY": "USD",
                           "Q_EXCHANGE": "CME", "IB_EXCHANGE": "GLOBEX", "MULTIPLIER": 0})
    result = ib_download(client, mkt_ser, maturity, start_date=start_date)
    print("-----------------")
    print("Start date: ", start_date)
    print("IB Download EDOLLAR ........................................")
    print(result)
    assert len(result) > 0

    ## Get the hourly EUR forex rates for last 2 days....

    mkt_ser = pd.Series({"IB": "EUR", "SECTYPE": "CASH", "CURRENCY": "USD",
                         "IB_EXCHANGE": "IDEALPRO", "MULTIPLIER": 0})
    result = ib_download(client, mkt_ser, maturity, start_date=start_date)
    print("-----------------")
    print("Start date: ", start_date)
    print("IB Download EUR .......................................")
    print(result)
    assert len(result) > 0

def test_getUpdatedRawContract(resource_marketdata_setup):
    ## Test should return the latest hourly series for the contract
    ## First finds latest daily prices
    ## ...Updates daily prices till yesterday setting each to 11:00pm
    ## ...Updates today's hourly prices
    from dbutils.panama import ib_download,qndl_download#

    assert 1==1

def test_check_raw_data_downloads(resource_roll_setup):
    from dbutils.panama import check_raw_data_downloads
    (engine , mkt_ser, rolls) = resource_roll_setup

    df_list = check_raw_data_downloads(engine, mkt_ser, rolls)
    for arr in df_list:
        print(arr[0], "-------------------------------------------------------------------------------------------------")
        print(arr[1].head(2))
        print(arr[1].tail(5))
        print()
    assert 1==1

def test_check_raw_data_downloads_v2(resource_roll_setup):
    import datetime
    from dbutils.panama import check_raw_data_downloads_v2
    (engine , mkt_ser, rolls) = resource_roll_setup

    list = check_raw_data_downloads_v2(engine, mkt_ser, rolls, False)
    for row in list:
        date = row[0].DATETIME
        carry_mat = row[0].CARRY_CONTRACT
        price_mat = row[0].PRICE_CONTRACT
        date_r23 = date + datetime.timedelta(hours=23)
        date_low = date
        date_high = date + datetime.timedelta(1)
        print("=========================================================================================================")
        #print(date)
        #print(date_r23)


        bool = date in row[1].index # where datetime may be as 2016-11-15 00:00:00
        bool23 = date_r23 in row[1].index # where datetime may be as 2016-11-15 23:00:00
        date_mask = (row[1].index >= date_low) & (row[1].index < date_high)
        dates = row[1].index[date_mask]
        date_mask2 = (row[2].index >= date_low) & (row[2].index < date_high)
        dates2 = row[2].index[date_mask2]
        #print("dates: ", dates[-1])
        #print("dates2: ", dates2[-1])
        #print("date0 In Price df: ", bool, "date23 in Price df: ", bool23)
        #print("Price mat:", price_mat)
        print("**** first 1")
        print(row[1].ix[dates])
        print("**** first 2")
        print(row[1].loc[dates[-1]])
        bool = date in row[2].index
        bool23 = date_r23 in row[2].index
        #print("date0 In Carry df: ", bool, "date23 in Carry df: ", bool23)
        #print("Carry mat:", carry_mat)
        print("**** second 1")
        print(row[2].ix[dates2])
        print("**** second 2")
        print(row[2].loc[dates2[-1]])
        #print(row[2])
    '''
    for row in list:
        date_mask = (data.index > start) & (data.index < end)
        dates = data.index[date_mask]
        data.ix[dates]
'''

def test_initialize_series(resource_roll_setup):
    from dbutils.panama import initialize_series
    (engine, mkt_ser, rolls) = resource_roll_setup
    coll = initialize_series(engine, mkt_ser, rolls )
    print(coll[0].tail(5))
    #print(coll[1].head(5))