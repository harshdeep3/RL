from stockEnv import StockMarketEnv as StockEnv
from mt5 import MT5_Link as link
import logging


class Env(StockEnv):
    """
    Represents a custom environment extending the StockEnv class.

    This class is a specialized environment, tailored for use with MetaTrader 5 (MT5),
    to handle operations related to financial instruments trading. It establishes
    a connection to MT5, retrieves account information, and initializes the environment
    for the specified financial symbol. It depends on an external MT5Class for
    performing all MT5-related operations.

    Attributes:
        mt5_obj (MT5Class): An instance of the MT5Class responsible for handling
            connection, login, and account information retrieval for MT5.
        symbol (str): The financial instrument symbol that the environment operates on.
            Defaults to "BTCUSD".
    """

    def __init__(self, logging_level: int = logging.DEBUG):

        # mt5 connection
        mt5_obj = link.MT5Class(logging_level=logging_level)
        mt5_obj.login_to_metatrader()
        mt5_obj.get_acc_info()

        symbol = "BTCUSD"

        super(Env, self).__init__(mt5_obj, symbol, logging_level)

