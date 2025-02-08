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


def get_all_orders() -> int:
    """
    Gets the total number of orders from the MetaTrader 5 trading platform.

    This function interacts with the MetaTrader 5 (MT5) API to retrieve the total
    number of open orders. It provides a simple interface to check the status of
    orders and outputs relevant information to the console. If there are any
    open orders, the total count is printed. Otherwise, a message stating that
    there are no orders is displayed.

    Returns:
        int: The total number of orders present in MetaTrader 5.

    Raises:
        Exception: If the MetaTrader 5 API is not initialized or fails to
        execute the function correctly.
    """
    orders = mt5.orders_total()

    if orders > 0:
        print("Total order = ", orders)
    else:
        print("No orders")

    return orders


def get_orders_total_by_symbol(symbol: str = "USDJPY") -> int:
    """
    Retrieves the total number of orders for a given financial instrument symbol.

    This function uses the MetaTrader 5 API to get the orders associated with the
    specified symbol. It prints the list of orders if available, or a message
    indicating that there are no orders for the provided symbol.

    Args:
        symbol (str): The financial instrument symbol to retrieve orders for. Defaults to "USDJPY".

    Returns:
        int: The total number of orders for the given symbol.
    """
    orders = mt5.orders_get(symbol=symbol)

    if len(orders) > 0:
        print(f"USDJPY orders = {orders}")
    else:
        print(f"No orders for {symbol}")

    return orders


def get_symbol_info(symbol: str = "USDJPY") -> object:
    """
    Fetches detailed information for a specific financial instrument symbol.

    This function attempts to retrieve information about a specified financial
    instrument symbol using the MetaTrader 5 API. It first checks if the symbol exists,
    and if it does not, it outputs the appropriate message and returns None. It also
    verifies if the symbol is visible in the trading platform and will return None if
    it is not. If both conditions are satisfied, it returns the symbol's information.

    Args:
        symbol (str): The symbol of the financial instrument to fetch information
            for. Defaults to "USDJPY".

    Returns:
        object: Returns an object containing all information about the specified
            symbol if found and visible. Returns None if the symbol is not found
            or is not visible.
    """

    symbol_info = mt5.symbol_info(symbol)

    if symbol_info is None:
        print(f"{symbol} not found")
        return None
    if not symbol_info.visible:
        print(f"{symbol} is not visible")
        return None

    return symbol_info


def buy_symbol(symbol: str, price: float, lot: float, sl: float, tp: float, deviation: int) -> dict:
    """
    Executes a 'buy' order for a specified financial symbol with the given parameters.
    The trading request is sent to the broker for execution, specifying the desired
    price, lot size, stop loss, take profit, deviation, and other necessary parameters.

    Args:
        symbol (str): The financial symbol to buy (e.g., currency pair or stock name).
        price (float): The desired price at which to execute the trade.
        lot (float): The volume of the trade, specified in lots.
        sl (float): The stop loss level for the trade.
        tp (float): The take profit level for the trade.
        deviation (int): The acceptable deviation in points for executing the trade.

    Returns:
        dict: A dictionary containing the results of the order execution, including
        details about success status, error codes, and other related data.
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


def close_buy_position(symbol: str, price: float, lot: float, deviation: int, position_id: int) -> dict:
    """
    Closes a buy position for a specified trading symbol and returns the execution result.

    This function sends a trade request to close an open buy position in the trading platform by
    placing a market sell order for the provided symbol. The parameters include the necessary
    details such as symbol name, price at which the position is closed, order volume, allowed
    price deviation, and the identifier of the position to be closed. The function prepares the
    trade request, sends it to the platform, and logs the transaction details. The trade result
    is returned.

    Args:
        symbol (str): The trading symbol for which the buy position is to be closed.
        price (float): The price at which the buy position will be closed.
        lot (float): The trade volume (lot size) to close the buy position.
        deviation (int): The maximum allowed deviation from the specified price.
        position_id (int): The identifier of the buy position to be closed.

    Returns:
        dict: A dictionary containing the result of the trade execution.
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


def close_sell_position(symbol: str, price: float, lot: float, deviation: int, position_id: int) -> dict:
    """
    Closes a sell position by opening a buy order with the specified parameters. This function uses MetaTrader
    5 API for handling trading operations.

    Args:
        symbol (str): The financial instrument for the trading operation (e.g., 'EURUSD').
        price (float): The price at which the buy order will be executed.
        lot (float): The volume of the trade in lots to be closed.
        deviation (int): The maximum price deviation allowed in points.
        position_id (int): The identifier of the existing sell position to be closed.

    Returns:
        dict: The result of the trading operation sent via the MetaTrader 5 API.
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


def sell_symbol(symbol: str, price: float, lot: float, sl: float, tp: float, deviation: int) -> dict:
    """
    Sends a sell order for a specified symbol in the MetaTrader 5 platform. The function creates
    a trading request to sell a symbol with a specified price, lot size, stop loss (SL), take
    profit (TP), and price deviation. The trade execution result is returned.

    Args:
        symbol (str): The financial instrument to sell (e.g., "EURUSD").
        price (float): The price at which the symbol should be sold.
        lot (float): The lot size to trade.
        sl (float): Stop loss price for the trade.
        tp (float): Take profit price for the trade.
        deviation (int): Maximum allowed deviation in points for the trade.

    Returns:
        Any: The result of the trade execution returned by MetaTrader 5.

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


def result_check(result: object) -> None:
    """
    Inspects the result of an order execution, logs the details, and prints any
    errors or detailed breakdowns of the trade result. If the result indicates
    a failure to complete (retcode differs from TRADE_RETCODE_DONE), prints the
    error details along with the request data.

    Args:
        result (object): The result object of a trading operation. Expected to
            have `retcode` attribute and support `_asdict()` method for
            accessing details, including potential nested request data in its
            dictionary representation.
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
    """
    Handles MetaTrader 5 operations such as login and retrieving account information.

    This class provides functionalities to connect to MetaTrader 5 terminal,
    authenticate using account credentials, and retrieve the account details for
    authenticated users.

    Attributes:
        mt5_result: Stores the result of the MetaTrader 5 login operation.
        account_info (dict): Holds account information as a dictionary after
            successful retrieval.

    """
    def __init__(self):
        self.mt5_result = None
        self.account_info = None

    def login_to_metatrader(self) -> None:

        """Logs in to the MetaTrader 5 terminal with the provided credentials.

            Establishes a connection to the MetaTrader 5 terminal and attempts to log
            in using the account credentials supplied to the function.

            Raises:
                SystemExit: If the login attempt fails.
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

    def get_acc_info(self) -> None:

        """
            Retrieves and updates the account information using MetaTrader 5 (MT5).

            This method fetches the current account details from MT5. If the account
            information is unavailable, it logs an error message. Otherwise, it stores
            the account details in a dictionary for further usage.

            Raises:
                None
            """
        if mt5.account_info() is None:
            print("Account info is None!")
        else:
            self.account_info = mt5.account_info()._asdict()


def get_historic_data(fx_symbol: str, fx_timeframe: int, fx_count: int) -> pd.DataFrame | None:
    """
    Retrieves historical market data from MetaTrader 5 for a specified financial symbol, timeframe,
    and count. The function converts the retrieved data into a pandas DataFrame and formats the
    time column as datetime. If the retrieval process fails or no data is returned, the function
    outputs an error message and returns None.

    Args:
        fx_symbol (str): The financial instrument symbol to retrieve data for (e.g., "EURUSD").
        fx_timeframe (int): The timeframe for the data, specified as an integer constant according to
            MetaTrader 5's API (e.g., mt5.TIMEFRAME_H1).
        fx_count (int): The number of data points (candles) to retrieve.

    Returns:
        pd.DataFrame | None: A pandas DataFrame containing the historical market data where the time
        column is converted to datetime. Returns None if retrieval fails or no data is found.
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
