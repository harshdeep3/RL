import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import pytz

SERVER = "ICMarketsSC-Demo"

# acocount number
LOGIN = 52069703
# password
PASSWORD = "8z$y2UX5s6aPFb"

# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)


def get_all_orders() -> None:
    """
    This function get the number of current active orders
    Returns:
        _type_: _description_ - All orders in place
    """
    orders = mt5.orders_total()

    if orders > 0:
        print("Total order = ", orders)
    else:
        print("No orders")

    return orders


def get_orders_total_by_symbol(symbol: str = "USDJPY") -> int:
    """
    This function get the number of current active orders filter for a given symbol
    Args:
        symbol (str, optional): _description_. Defaults to "USDJPY". Symbol name

    Returns:
        int: _description_ - All order for a given symbol
    """
    orders = mt5.orders_get(symbol=symbol)

    if len(orders) > 0:
        print(f"USDJPY orders = {orders}")
    else:
        print(f"No orders for {symbol}")

    return orders


def get_symbol_info(symbol: str = "USDJPY"):
    """
    This function gets information for a given symbol
    Args:
        symbol (str, optional): _description_. Defaults to "USDJPY". - Symbol name

    Returns:
        _type_: _description_ - Information for a Given symbol
    """

    symbol_info = mt5.symbol_info(symbol)

    if symbol_info is None:
        print(f"{symbol} not found")
        return None
    if not symbol_info.visible:
        print(f"{symbol} is not visible")
        return None

    return symbol_info


def buy_symbol(symbol: str, price: float, lot: float, sl: float, tp: float, deviation: int):
    """
    The code block you provided is sending a trading request to buy a symbol at a
    specific price.

    Args:
        price (float): _description_ - price to buy at
        lot (float): _description_ - amount (lot) to buy
        point (float): _description_ -
        deviation (int): _description_ -

    Returns:
        _type_: _description_ - result of the buy request
    """

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # send a trading request
    result = mt5.order_send(request)

    # check the execution result
    print(f"1. order_send(): by {symbol} {lot} lots at {price} with deviation={deviation} points")

    return result


def close_buy_position(symbol: str, price: float, lot: float, deviation: int, position_id: int):
    """
    The code block you provided is sending a trading request to buy a symbol at a
    specific price.

    Args:
        price (float): _description_ - price to buy at
        lot (float): _description_ - amount (lot) to buy
        point (float): _description_ -
        deviation (int): _description_ -

    Returns:
        _type_: _description_ - result of the buy request
    """

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_SELL,
        "position": position_id,
        "price": price,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # send a trading request
    result = mt5.order_send(request)

    # check the execution result
    print(f"close position #{position_id}: sell {symbol} {lot} lots at {price} with deviation={deviation} points")

    return result


def close_sell_position(symbol: str, price: float, lot: float, deviation: int, position_id: int):
    """
    The code block you provided is sending a trading request to buy a symbol at a
    specific price.

    Args:
        price (float): _description_ - price to buy at
        lot (float): _description_ - amount (lot) to buy
        point (float): _description_ -
        deviation (int): _description_ -

    Returns:
        _type_: _description_ - result of the buy request
    """

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "position": position_id,
        "price": price,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # send a trading request
    result = mt5.order_send(request)

    # check the execution result
    print(f"close position #{position_id}: buy {symbol} {lot} lots at {price} with deviation={deviation} points")

    return result


def sell_symbol(symbol: str, price: float, lot: float, sl: float, tp: float, deviation: int):
    """
    Sending a buy signal at a given price.

    Args:
        price (float): _description_ - price to buy at
        lot (float): _description_ - amount (lot) to buy
        point (float): _description_ -
        deviation (int): _description_ -

    Returns:
        _type_: _description_ - result of the buy request
    """
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # send a trading request
    result = mt5.order_send(request)

    # check the execution result
    print(f"order_send(): by {symbol} {lot} lots at {price} with deviation={deviation} points")

    return result


def result_check(result):
    """
    Return the request result
    Args:
        result (_type_): _description_ - result for the request sent
    """
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"2. order_send failed, retcode={result.retcode}")
        # request the result as a dictionary and display it element by element
        result_dict = result._asdict()
        for field in result_dict.keys():
            print(f"  {field}={result_dict[field]}")
            # if this is a trading request structure, display it element by element as well
            if field == "request":
                traderequest_dict = result_dict[field]._asdict()
                for tradereq_filed in traderequest_dict:
                    print(f"  traderequest: {tradereq_filed}={traderequest_dict[tradereq_filed]}")


class MT5Class:

    def __init__(self):
        self.mt5_result = None
        self.account_info = None

    def login_to_metatrader(self):
        """
        Login into meta trader 5 account

        """
        # Connect to the MetaTrader 5 terminal
        mt5.initialize()

        # Log in to the terminal with your account credentials
        account_server = SERVER
        # this needs to be an integer
        login = LOGIN
        password = PASSWORD
        self.mt5_result = mt5.login(login, password, account_server)

        if not self.mt5_result:
            print("Login failed. Check your credentials.")
            quit()

    def get_acc_info(self):
        """
        Get account information
        """
        if mt5.account_info() is None:
            print("Account info is None!")
        else:
            account_info_dict = mt5.account_info()._asdict()
            self.account_info = pd.DataFrame(list(account_info_dict.items()), columns=['property', 'value'])
            print(self.account_info)


def get_historic_data(fx_symbol, fx_timeframe, fx_count):
    """
    
    Args:
        fx_symbol:
        fx_timeframe:
        fx_count:

    Returns:

    """
    rates = mt5.copy_rates_from_pos(fx_symbol, fx_timeframe, 0, fx_count)
    # dataframe
    historic_df = pd.DataFrame(rates)
    # changing the time to datetime
    if "time" in historic_df.keys():
        historic_df['time'] = pd.to_datetime(historic_df['time'], unit='s')
        return historic_df
    else:
        print("\n\nData not found! Check MT5 connection!")
        return None


if __name__ == "__main__":
    # todo update doc strings
    mt5_obj = MT5Class()
    mt5_obj.login_to_metatrader()
    mt5_obj.get_acc_info()

    # timeframe objects https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesfrom_py
    timeframe = mt5.TIMEFRAME_D1
    symbol = 'USDJPY'
    # set time zone to UTC
    timezone = pytz.timezone("Etc/UTC")
    # create 'datetime' objects in UTC time zone to avoid the implementation of a local time zone offset
    utc_from = datetime(2010, 1, 10, tzinfo=timezone)
    utc_to = datetime(2020, 1, 11, tzinfo=timezone)

    # goes back to 1971-08-11
    count = 13500

    # print account info
    # mt5_obj.get_acc_info()

    # get data
    df = get_historic_data(symbol, timeframe, count)
    df = df.set_index('time')

    print(df)
    # Disconnect from the terminal
    mt5.shutdown()
