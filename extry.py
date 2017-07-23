from ex2 import *

app = HistApp("127.0.0.1", 4001, 999)

ibcontract = IBcontract()
ibcontract.secType = "FUT"
ibcontract.lastTradeDateOrContractMonth="201809"
ibcontract.symbol="GE"
ibcontract.exchange="GLOBEX"

resolved_ibcontract=app.resolve_ib_contract(ibcontract)

historic_data = app.get_IB_historical_data(resolved_ibcontract)

print(historic_data)

app.disconnect()