from mt5 import MT5_Link as link
import MetaTrader5 as mt5
import datetime

from ta.trend import sma_indicator
from ta.trend import ema_indicator
from ta.momentum import RSIIndicator


def main() -> None:
    """
    Main execution function for setting up and analyzing financial market data. This
    function includes logging initialization, fetching historical data using MetaTrader 5
    (MT5), and calculating various financial indicators such as Simple Moving Average
    (SMA), Exponential Moving Average (EMA), and Relative Strength Index (RSI). The
    entire process aims to prepare financial data for further downstream analysis or
    implementation in ML/AI systems.

    Args:
        None

    Returns:
        None
    """

    # logging
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
    # logging.basicConfig(filename=f'controller_log/{now}_optuna_study_DQN.log',
    #                     level=LOGGING_LEVEL,
    #                     format='%(asctime)s :: %(levelname)s :: %(module)s :: %(processName)s'
    #                            ' :: %(funcName)s :: line #-%(lineno)d :: %(message)s')

    # file where the study results will be saved
    trial_name = f'saved_Files/{now}_optuna_study_PPO_4_envs.csv'
    mt5_obj = link.MT5Class()
    mt5_obj.login_to_metatrader()
    mt5_obj.get_acc_info()
    start = datetime.datetime(2010, 7, 1).strftime("%Y-%m-%d")
    end = datetime.datetime.now().strftime("%Y-%m-%d")

    timeframe = mt5.TIMEFRAME_D1
    symbol = 'USDJPY'
    count = 13500  # get 8500 data points

    # env = make_vec_env(Env, n_envs=4)
    data = link.get_historic_data(fx_symbol=symbol, fx_timeframe=timeframe, fx_count=count)
    
    sma_data = sma_indicator(data['close'],window=12, fillna=True)
    ema_data = ema_indicator(data['close'],window=12, fillna=True)
    rsi_data = RSIIndicator(data['close'],window=12, fillna=True).rsi()

    print("sma -> ", sma_data.head(), sma_data[4])
    print("ema -> ", ema_data.head(), ema_data[4])
    print("rsi -> ", rsi_data.head(),rsi_data[4])
    
    
if __name__ == '__main__':
    main()
