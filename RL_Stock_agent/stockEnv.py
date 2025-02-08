from typing import Tuple

import gymnasium as gym
from gymnasium import spaces
from collections import namedtuple
import logging
import pandas as pd

from mt5 import MT5_Link as link
import MetaTrader5 as mt5
import numpy as np
import pandas_datareader as web
import datetime

from ta.trend import sma_indicator
from ta.trend import ema_indicator
from ta.momentum import RSIIndicator


obs_namedtuple = namedtuple('obs_namedtuple',
                            ['balance', 'equity', 'free_margin', 'margin', 'profit', 'ask', 'bid',
                             'session_open', 'session_close', 'ema', 'sma', 'rsi'])

SMA_TIME = 20
EMA_TIME = 20
RSI_TIME = 14

LOGGING_LEVEL = logging.DEBUG


def get_yahoo_data(stock_name: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetches historical stock data from Yahoo Finance API for a specified stock and date range.

    This function retrieves stock prices and volume data for a given stock ticker
    within the specified start and end dates. The data is returned as a pandas
    DataFrame containing the stock's open, high, low, close, adjusted close prices,
    and volume. The index of the returned DataFrame is reset for easier access and
    manipulation.

    Args:
        stock_name (str): The ticker symbol of the stock to retrieve data for.
        start_date (str): The starting date for the data retrieval in 'YYYY-MM-DD'
            format.
        end_date (str): The ending date for the data retrieval in 'YYYY-MM-DD'
            format.

    Returns:
        pd.DataFrame: A DataFrame containing the stock's historical data, including
        columns such as 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', and
        a reset index.
    """
    df = web.data.get_data_yahoo(stock_name, start_date, end_date)
    # reset the index of the data to normal ints so df['Date'] can be used
    df.reset_index()
    return df


class StockMarketEnv(gym.Env):
    """
    Manages a simulated trading environment for a stock market.

    This class provides an OpenAI Gym-style interface for simulating stock market
    trading. It integrates historical market data, real-time account information,
    and technical indicators to create a realistic trading environment. Users can
    perform actions such as buying, selling, or holding stocks while receiving
    feedback in the form of rewards, observations, and termination flags.

    Attributes:
        logger (logging.Logger): Logger instance for capturing and reporting activity logs within the environment.
        mt5_obj (link.MT5Class): Reference to the MT5 API class instance for interacting with the Forex trading platform.
        symbol (str): The stock market symbol being traded in the environment.
        timeframe (int): The predefined time interval for retrieving historical price data (e.g., M5 - 5-minute intervals).
        action_space (gym.spaces.Discrete): The action space defining the valid range of trading actions.
        observation_space (gym.spaces.Box): The observation space defining the structure of observation states.
        state (np.ndarray): The current state representing market and account information for decision-making.
        current_index (int): Index pointer for historic data traversal, starting from the initial position.
        all_time_high (float): The all-time high closing price of the stock based on historical market data.
        symbol_info (object): Structure containing detailed information about the trading symbol, including pricing data,
            session timing, etc.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, mt5_obj: link.MT5Class, symbol: str):
        super(StockMarketEnv, self).__init__()
                
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(LOGGING_LEVEL)

        self.mt5_obj = mt5_obj
        self.symbol = symbol
        self.timeframe = mt5.TIMEFRAME_M5

        # getting historic data
        fx_count = 13000
        historic_data = link.get_historic_data(self.symbol, self.timeframe, fx_count)
        self.all_time_high = historic_data['close'].max()

        # prepare the buy request structure-
        self.symbol_info = mt5.symbol_info(symbol)
        if self.symbol_info is None:
            print(symbol, "not found, can not call order_check()")
            mt5.shutdown()
            quit()

        # Define action and observation spaces
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(low=0, high=1, shape=(10,), dtype=np.float64)

        self.state = self.get_obs()

        # Set starting index for data
        self.current_index = 1
        self.reset()

    def get_obs(self) -> np.ndarray:

        """
        Retrieves the current observation state of the trading environment.

        A comprehensive observation is created by consolidating real-time account
        data, symbol information, historical price data, and technical indicators.
        This state is then formatted to provide necessary data for decision-making
        related to trading actions.

        Returns:
            np.ndarray: An array representing the observation state, including
            account details, symbol data, and the most recent technical
            indicator values.
        """
        # Initialize symbol data
        # account information
        # total balance (before profit and loss
        balance = self.mt5_obj.account_info['balance']
        # current total value (include profit and loss)
        equity = self.mt5_obj.account_info['equity']
        # cash avaliable for use (buy or sell)
        free_margin = self.mt5_obj.account_info['margin_free']
        # value in GBP of symbol that is bought
        margin = self.mt5_obj.account_info['margin']
        # value in GBP of the profit current being made by the account
        profit = self.mt5_obj.account_info['profit']

        # symbol information
        # ask price ->
        ask = self.symbol_info.ask
        # bid price ->
        bid = self.symbol_info.bid
        # session open
        session_open = self.symbol_info.session_open
        # session close
        session_close = self.symbol_info.session_close

        # getting historic data
        fx_count = max([RSI_TIME, SMA_TIME, EMA_TIME])
        historic_data = link.get_historic_data(self.symbol, self.timeframe, fx_count)

        # get indicator data
        rsi = RSIIndicator(historic_data['close'], window=RSI_TIME, fillna=True).rsi().to_numpy()[-1]
        sma = sma_indicator(historic_data['close'], window=SMA_TIME, fillna=True).to_numpy()[-1]
        ema = ema_indicator(historic_data['close'], window=EMA_TIME, fillna=True).to_numpy()[-1]

        # Creating the state
        self.state = obs_namedtuple(balance=balance, equity=equity, free_margin=free_margin, margin=margin,
                                    profit=profit, ask=ask, bid=bid, session_open=session_open,
                                    session_close=session_close, ema=ema, sma=sma, rsi=rsi)

        # creating an env state
        obs = self.reformat_matrix(self.state)

        self.logger.debug(f"obs: {obs}")

        return obs

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, dict]:

        """
        Performs a single step of the environment, processes the given action, updates internal state based
        on financial metrics and market data, logs the step details, and returns observation, reward,
        termination status, and other information.

        Args:
            action (int): The action to be performed in the environment. Typically corresponds to a trading
                decision such as buy, sell, or hold.

        Returns:
            Tuple[np.ndarray, float, bool, bool, dict]: A tuple containing:
                - np.ndarray: The reformatted observation matrix representing the current state.
                - float: The calculated reward for the executed action.
                - bool: Whether the environment is terminated (done).
                - bool: Whether the environment is truncated. Always `False` in the current implementation.
                - dict: Additional information such as diagnostic data (empty in the current implementation).

        Raises:
            KeyError: If required keys are missing while accessing account or symbol data.
            ValueError: If there is a discrepancy in indicator calculation or historic data retrieval.
        """

        # Initialize symbol data
        # account information
        # total balance (before profit and loss
        balance = self.mt5_obj.account_info['balance']
        # current total value (include profit and loss)
        equity = self.mt5_obj.account_info['equity']
        # cash avaliable for use (buy or sell)
        free_margin = self.mt5_obj.account_info['margin_free']
        # value in GBP of symbol that is bought
        margin = self.mt5_obj.account_info['margin']
        # value in GBP of the profit current being made by the account
        profit = self.mt5_obj.account_info['profit']

        # symbol information
        # ask price ->
        ask = self.symbol_info.ask
        # bid price ->
        bid = self.symbol_info.bid
        # session open
        session_open = self.symbol_info.session_open
        # session close
        session_close = self.symbol_info.session_close

        # getting historic data
        fx_count = max([RSI_TIME, SMA_TIME, EMA_TIME])
        historic_data = link.get_historic_data(self.symbol, self.timeframe, fx_count)

        # get indicator data
        rsi = RSIIndicator(historic_data['close'], window=RSI_TIME, fillna=True).rsi().to_numpy()[-1]
        sma = sma_indicator(historic_data['close'], window=SMA_TIME, fillna=True).to_numpy()[-1]
        ema = ema_indicator(historic_data['close'], window=EMA_TIME, fillna=True).to_numpy()[-1]

        # Creating the state
        self.state = obs_namedtuple(balance=balance, equity=equity, free_margin=free_margin, margin=margin,
                                    profit=profit, ask=ask, bid=bid, session_open=session_open,
                                    session_close=session_close, ema=ema, sma=sma, rsi=rsi)

        self.trade(action)

        self.logger.debug(f"action: {action}, balance: {balance}, equity: {equity}, free_margin: {free_margin}, margin:" 
                          f" {margin}, profit: {profit}, ask: {ask}, bid: {bid}, session open: {session_open}, "
                          f"session_close: {session_close}, SMA: {sma}, EMA: {ema},  RSI: {rsi}")

        # Check if done
        done = equity < 20
        reward = self.get_reward()

        # Return observation, reward, done, and info
        return self.reformat_matrix(self.state), reward, done, False, {}

    def trade(self, action: int) -> None:

        """
        Executes a trade action based on the given input and updates the system state accordingly.

        This method processes a single trade action (either buying or selling stocks) and modifies the
        agent's cash holdings and owned stocks. It handles multiple trade requests, ensures valid
        stock transactions based on available cash, and updates the internal observable state.

        Args:
            action (int): The trade action where 0 represents a sell action, and 2 represents a buy action.

        """
        # TODO -> send a trade this function
        cash_in_hand = self.cash_in_hand

        allactions = []
        sell_index = []
        buy_index = []

        if action == 0:
            # sell stocks
            sell_index.append(1)
        elif action == 2:
            # buy stocks
            buy_index.append(1)

        if sell_index:
            cash_in_hand += self.state.close * self.state.owned
            owned = 0
            # make update obs_namedtyple function
            self.update_obs(cash_in_hand=cash_in_hand, owned=owned)
            
        elif buy_index:
            can_buy = True
            while can_buy:
                owned = self.state.owned
                for _ in buy_index:
                    # buy a single stock on loop
                    # if there are multiple stocks then the loop iterates over each stock and buys 1 stock
                    # (if it can) for the stocks available each iteration.
                    if self.state.cash_in_hand > self.state.close:
                        owned += 1  # buy one share
                        cash_in_hand -= self.state.close
                        
                        self.update_obs(owned=owned, cash_in_hand=cash_in_hand)
                    else:
                        # if the cash left is lower the stock price then stop buying
                        can_buy = False
        
        self.cash_in_hand = cash_in_hand
        
        self.logger.debug(f"action: {action}, cash in hand: {cash_in_hand}, state cash in hand: {self.state.cash_in_hand}, owned: {self.state.owned}")

    def get_reward(self) -> float:

        """
            Gets the current reward or profit of the account from the trading platform.

            This method retrieves the profit value in GBP for the current trading account.
            The profit is fetched from the account information provided by the MetaTrader 5
            (MT5) integration object. This value represents the total profit currently being made.

            Returns:
                float: The profit in GBP from the account.

            """
        self.logger.debug("get_reward function - > ")
        # value in GBP of the profit current being made by the account
        reward = self.mt5_obj.account_info['profit']

        return reward

    def reset(self, seed: int = None, **kwargs) -> np.ndarray:

        """
            Resets the environment state and initializes various data structures and metrics required for trading simulation.
            This function sets up the initial conditions, including account and symbol information, historic data, and
            financial indicators. It prepares input observations and internal state to begin a new session.

            Args:
                seed (int, optional): Seed for random number generator. Defaults to None.
                **kwargs: Additional arguments for customization.

            Returns:
                np.ndarray: Reformatted matrix representation of the initial observation.
            """
        # Initialize symbol data
        # account information
        # total balance (before profit and loss
        balance = self.mt5_obj.account_info['balance']
        # current total value (include profit and loss)
        equity = self.mt5_obj.account_info['equity']
        # cash avaliable for use (buy or sell)
        free_margin = self.mt5_obj.account_info['margin_free']
        # value in GBP of symbol that is bought
        margin = self.mt5_obj.account_info['margin']
        # value in GBP of the profit current being made by the account
        profit = self.mt5_obj.account_info['profit']

        # symbol information
        # ask price ->
        ask = self.symbol_info.ask
        # bid price ->
        bid = self.symbol_info.bid
        # session open
        session_open = self.symbol_info.session_open
        # session close
        session_close = self.symbol_info.session_close

        # getting historic data
        fx_count = max([RSI_TIME, SMA_TIME, EMA_TIME])
        historic_data = link.get_historic_data(self.symbol, self.timeframe, fx_count)

        # get indicator data
        rsi = RSIIndicator(historic_data['close'], window=RSI_TIME, fillna=True).rsi().to_numpy()[-1]
        sma = sma_indicator(historic_data['close'], window=SMA_TIME, fillna=True).to_numpy()[-1]
        ema = ema_indicator(historic_data['close'], window=EMA_TIME, fillna=True).to_numpy()[-1]

        # Creating the state
        self.state = obs_namedtuple(balance=balance, equity=equity, free_margin=free_margin, margin=margin,
                                    profit=profit, ask=ask, bid=bid, session_open=session_open,
                                    session_close=session_close, ema=ema, sma=sma, rsi=rsi)

        # creating an env state
        obs = self.reformat_matrix(self.state)

        self.logger.debug(f"obs: {obs}")

        return obs

        # Reset state, reward, and current index
        self.reward = 0
        self.current_index = 1

        info = {}

        stock_owned = 0
        
        stock_open = self.data['open'].iloc[self.current_index]
        stock_high = self.data['high'].iloc[self.current_index]
        stock_low = self.data['low'].iloc[self.current_index]
        stock_close = self.data['close'].iloc[self.current_index]
        stock_vol = self.data['tick_volume'].iloc[self.current_index]
        cash_in_hand = 200
        
        #todo add % change
        # self.state[-1] = self.data.iloc[self.current_index]["pct_change"]

        stock_rsi = self.rsi.iloc[self.current_index]

        # as this use previous data to get the current value, this can be nan
        # at the first few time steps, this is to remove them
        stock_sma = self.sma.iloc[self.current_index]

        stock_ema = self.ema.iloc[self.current_index]

        self.state = obs_namedtuple(owned=stock_owned, open=stock_open, low=stock_low, close=stock_close,
                                    high=stock_high, volume=stock_vol, sma=stock_sma, ema=stock_ema, rsi=stock_rsi,
                                    cash_in_hand=cash_in_hand)
        
        self.total_net = self.get_net()
        state_output = self.reformat_matrix(self.state)
        self.logger.debug(f"stocks owned: {stock_owned}, cash in hand: {cash_in_hand}, open: {stock_open}, low:"
                        f"{stock_low}, close: {stock_close}, high: {stock_high}, volume: {stock_vol}, RSI: {stock_rsi},"
                        f"SMA: {stock_sma}, EMA: {stock_ema}")
        return state_output, info

    def reformat_matrix(self, state: obs_namedtuple) -> np.ndarray:

        """
        Reformats and normalizes financial state data into a single matrix representation.

        This function processes the provided financial state data, normalizes its various fields within specified
        ranges, and combines them into a one-dimensional numpy array that can be used for further processing
        or analysis. Normalization scales the data between 0.0 and 1.0 based on the respective field's range,
        ensuring consistency in the dataset.

        Args:
            state (obs_namedtuple): A named tuple containing financial state data, which includes fields such as
                ask, balance, bid, equity, free_margin, margin, profit, session_open, session_close, rsi, sma,
                and ema. These fields represent various financial metrics.

        Returns:
            np.ndarray: A 1D numpy array representing the normalized state data for all fields, with a shape of (12,).
        """
        ask = state.ask
        balance = state.balance
        bid = state.bid
        equity = state.equity
        free_margin = state.free_margin
        margin = state.margin
        profit = state.profit
        session_open = state.session_open
        session_close = state.session_close
        rsi = state.rsi
        sma = state.sma
        ema = state.ema

        norm_balance = np.interp(balance, [0, 200],[0.0, 1.0]).reshape(1, 1)
        norm_equity = np.interp(equity, [0, balance], [0.0, 1.0]).reshape(1, 1)
        norm_free_margin = np.interp(free_margin, [0, margin],[0.0, 1.0]).reshape(1, 1)
        norm_margin = np.interp(balance, [0, 200],[0.0, 1.0]).reshape(1, 1)
        norm_profit = np.interp(profit, [0, balance], [0.0, 1.0]).reshape(1, 1)
        norm_ask = np.interp(ask, [0, self.all_time_high],[0.0, 1.0]).reshape(1, 1)
        norm_bid = np.interp(bid, [0, self.all_time_high], [0.0, 1.0]).reshape(1, 1)
        norm_session_open = np.interp(session_open, [0, self.all_time_high], [0.0, 1.0]).reshape(1, 1)
        norm_ssession_close = np.interp(session_close, [0, self.all_time_high], [0.0, 1.0]).reshape(1, 1)
        norm_rsi = np.interp(rsi, [0, 100], [0.0, 1.0]).reshape(1, 1)
        norm_sma = np.interp(sma, [0, self.all_time_high], [0.0, 1.0]).reshape(1, 1)
        norm_ema = np.interp(ema, [0, self.all_time_high], [0.0, 1.0]).reshape(1, 1)

        row_matrix = np.concatenate((norm_balance, norm_equity, norm_free_margin, norm_margin, norm_profit, norm_ask,
                                     norm_bid, norm_session_open, norm_ssession_close, norm_rsi, norm_sma,
                                     norm_ema)).reshape(12,)

        self.logger.debug(f"Value (normalised valuse -> Acount balance: {balance}({norm_balance}), equity: {equity} "
                          f"({norm_equity}), free_margin: {free_margin}({norm_free_margin}), margin: {margin} "
                          f"({norm_margin}), profit: {profit} ({norm_profit}), ask: {ask} ({norm_ask}), "
                          f"bid: {bid} ({norm_bid}), session_open: {session_open} ({norm_session_open}), "
                          f"session_close: {session_close} ({norm_ssession_close}), RSI: {rsi} ({norm_rsi}),"
                          f"SMA: {sma} ({norm_sma}), EMA: {ema} ({norm_ema})")
        
        return row_matrix

    def update_obs(self, owned=None, stock_open=None, low=None, close=None, high=None, volume=None,
                   rsi=None, sma=None, ema=None, cash_in_hand=None):
        
        if owned is None:
            owned = self.state.owned

        if stock_open is None:
            stock_open = self.state.open

        if low is None:
            low = self.state.low

        if close is None:
            close = self.state.close

        if high is None:
            high = self.state.high

        if volume is None:
            volume = self.state.volume

        if rsi is None:
            if not np.isnan(self.state.rsi):
                rsi = self.state.rsi

        if sma is None:
            if not np.isnan(self.state.sma):
                sma = self.state.sma

        if ema is None:
            if not np.isnan(self.state.ema):
                ema = self.state.ema

        if cash_in_hand is None:
            cash_in_hand = self.state.cash_in_hand

        self.logger.debug(f"stocks owned: {owned}, cash in hand: {cash_in_hand}, open: {stock_open}, low:"
                        f"{low}, close: {close}, high: {high}, volume: {volume}, RSI: {rsi},"
                        f"SMA: {sma}, EMA: {ema}")
        
        self.state = obs_namedtuple(owned=owned, open=stock_open, low=low, close=close, high=high,
                                    volume=volume, sma=sma, ema=ema, rsi=rsi, cash_in_hand=cash_in_hand)


if __name__ == '__main__':
    # MT5 account connection
    mt5_obj = link.MT5Class()
    mt5_obj.login_to_metatrader()
    mt5_obj.get_acc_info()

    start = datetime.datetime(2010, 7, 1).strftime("%Y-%m-%d")
    end = datetime.datetime.now().strftime("%Y-%m-%d")

    timeframe_h1 = mt5.TIMEFRAME_H1
    timeframe_h4 = mt5.TIMEFRAME_H4
    timeframe_d1 = mt5.TIMEFRAME_D1
    timeframe_w1 = mt5.TIMEFRAME_W1
    symbol = 'USDJPY'
    count = 8500  # get 8500 data points

    data_h1 = link.get_historic_data(fx_symbol=symbol, fx_timeframe=timeframe_h1, fx_count=count)
    # data_h4 = link.get_historic_data(fx_symbol=symbol, fx_timeframe=timeframe_h4, fx_count=count)
    # data_d1 = link.get_historic_data(fx_symbol=symbol, fx_timeframe=timeframe_d1, fx_count=count)
    # data_w1 = link.get_historic_data(fx_symbol=symbol, fx_timeframe=timeframe_w1, fx_count=count)

    # print("H\n", data_h1.head())
    # print("\nH4\n", data_h4.head())
    # print("\nD1\n", data_d1.head())
    # print("\nW1\n", data_w1.head())

    if data_h1 is None:
        print("Error: Data not recieved!")
    else:
        data_h1.set_index('time', inplace=True)
        print("\n", data_h1.head())
        print("\n", data_h1.tail())
        # env = StockMarketEnv(data_h1)

        # model = DQN('MlpPolicy', env, verbose=1)
        # model.learn(total_timesteps=1000)
