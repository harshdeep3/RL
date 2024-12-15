
import MetaTrader5 as mt5
from mt5.MT5_Link import MT5Class, buy_symbol, sell_symbol, result_check, close_buy_position, close_sell_position
import time

if __name__ == "__main__":

    # get the custom MT5 class
    mt5_obj = MT5Class()
    # log into mt5 using the account info provided
    # pass in the account number and password for different account
    mt5_obj.login_to_metatrader()
    # get account info
    mt5_obj.get_acc_info()
    symbol = "BTCUSD"

    # prepare the buy request structure
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, can not call order_check()")
        mt5.shutdown()
        quit()

    # if the symbol is unavailable in MarketWatch, add it
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5.symbol_select(symbol, True):
            print("symbol_select({}}) failed, exit", symbol)
            mt5.shutdown()
            quit()

    if symbol_info is not None:
        lot = 0.01
        point = symbol_info.point
        price = symbol_info.ask
        deviation = 20

        # take profit and stop loss calculations
        tp = price + 100000 * point
        sl = price - 100000 * point

        result = buy_symbol(symbol=symbol, price=price, lot=lot, sl=sl, tp=tp, deviation=deviation)

        # check the execution result
        result_check(result=result)

        time.sleep(2)

        # create a close request
        position_id = result.order
        price = mt5.symbol_info_tick(symbol).bid
        deviation = 20

        tp = price + 100000 * point
        sl = price - 100000 * point

        result = close_buy_position(symbol=symbol, price=price, lot=lot, deviation=deviation, position_id=position_id)

        # check the execution result
        result_check(result=result)

        mt5.shutdown()

    """
    symbol info contains:
    custom=False, chart_mode=0, select=True, visible=True, session_deals=0, session_buy_orders=0, session_sell_orders=0,
    volume=0, volumehigh=0, volumelow=0, time=1705969770, digits=3, spread=55, spread_float=True, ticks_bookdepth=10,
    trade_calc_mode=0, trade_mode=4, start_time=0, expiration_time=0, trade_stops_level=0, trade_freeze_level=0, trade_exemode=2,
    swap_mode=1, swap_rollover3days=3, margin_hedged_use_leg=False, expiration_mode=15, filling_mode=2, order_mode=127,
    order_gtc_mode=0, option_mode=0, option_right=0, bid=147.956, bidhigh=148.098, bidlow=147.917, ask=148.011, askhigh=148.17,
    asklow=147.948, last=0.0, lasthigh=0.0, lastlow=0.0, volume_real=0.0, volumehigh_real=0.0, volumelow_real=0.0,
    option_strike=0.0, point=0.001, trade_tick_value=0.5313750391889092, trade_tick_value_profit=0.5313750391889092,
    trade_tick_value_loss=0.531804572455714, trade_tick_size=0.001, trade_contract_size=100000.0, trade_accrued_interest=0.0,
    trade_face_value=0.0, trade_liquidity_rate=0.0, volume_min=0.01, volume_max=200.0, volume_step=0.01, volume_limit=0.0,
    swap_long=12.46, swap_short=-25.92, margin_initial=100000.0, margin_maintenance=0.0, session_volume=0.0, session_turnover=0.0,
    session_interest=0.0, session_buy_orders_volume=0.0, session_sell_orders_volume=0.0, session_open=147.919,
    session_close=148.117, session_aw=0.0, session_price_settlement=0.0, session_price_limit_min=0.0, session_price_limit_max=0.0,
    margin_hedged=0.0, price_change=-0.1087, price_volatility=0.0, price_theoretical=0.0, price_greeks_delta=0.0,
    price_greeks_theta=0.0, price_greeks_gamma=0.0, price_greeks_vega=0.0, price_greeks_rho=0.0, price_greeks_omega=0.0,
    price_sensitivity=0.0, basis='', category='', currency_base='USD', currency_profit='JPY', currency_margin='USD', bank='',
    description='US Dollar vs Japanese Yen', exchange='', formula='', isin='', name='USDJPY', page='',
    path='Forex\\Majors\\USDJPY'

    Possible required features:
    bid, bidhigh, bidlow, ask, askhigh, asklow, session_open, session_close, price_change

    additional feature can be created using calculating indicator values.
    """

if __name__ == "__main__":
    
    # get the custom MT5 class
    mt5_obj = MT5Class()
    # log into mt5 using the account info provided
    # pass in the account number and password for different account
    mt5_obj.login_to_metatrader()
    # get account info
    mt5_obj.get_acc_info()
    
    # get total number of orders 
    num_of_order = mt5_obj.get_all_orders()
    # get total number of order for a given symbol
    num_of_order = mt5_obj.get_orders_total_by_symbol("BTCUSD")
    
    symbol_info = mt5_obj.get_symbol_info("BTCUSD")
    """
    symbol info contains: 
    custom=False, chart_mode=0, select=True, visible=True, session_deals=0, session_buy_orders=0, session_sell_orders=0, 
    volume=0, volumehigh=0, volumelow=0, time=1705969770, digits=3, spread=55, spread_float=True, ticks_bookdepth=10, 
    trade_calc_mode=0, trade_mode=4, start_time=0, expiration_time=0, trade_stops_level=0, trade_freeze_level=0, trade_exemode=2,
    swap_mode=1, swap_rollover3days=3, margin_hedged_use_leg=False, expiration_mode=15, filling_mode=2, order_mode=127, 
    order_gtc_mode=0, option_mode=0, option_right=0, bid=147.956, bidhigh=148.098, bidlow=147.917, ask=148.011, askhigh=148.17,
    asklow=147.948, last=0.0, lasthigh=0.0, lastlow=0.0, volume_real=0.0, volumehigh_real=0.0, volumelow_real=0.0, 
    option_strike=0.0, point=0.001, trade_tick_value=0.5313750391889092, trade_tick_value_profit=0.5313750391889092,
    trade_tick_value_loss=0.531804572455714, trade_tick_size=0.001, trade_contract_size=100000.0, trade_accrued_interest=0.0,
    trade_face_value=0.0, trade_liquidity_rate=0.0, volume_min=0.01, volume_max=200.0, volume_step=0.01, volume_limit=0.0,
    swap_long=12.46, swap_short=-25.92, margin_initial=100000.0, margin_maintenance=0.0, session_volume=0.0, session_turnover=0.0,
    session_interest=0.0, session_buy_orders_volume=0.0, session_sell_orders_volume=0.0, session_open=147.919, 
    session_close=148.117, session_aw=0.0, session_price_settlement=0.0, session_price_limit_min=0.0, session_price_limit_max=0.0,
    margin_hedged=0.0, price_change=-0.1087, price_volatility=0.0, price_theoretical=0.0, price_greeks_delta=0.0,
    price_greeks_theta=0.0, price_greeks_gamma=0.0, price_greeks_vega=0.0, price_greeks_rho=0.0, price_greeks_omega=0.0,
    price_sensitivity=0.0, basis='', category='', currency_base='USD', currency_profit='JPY', currency_margin='USD', bank='',
    description='US Dollar vs Japanese Yen', exchange='', formula='', isin='', name='USDJPY', page='',
    path='Forex\\Majors\\USDJPY'
    
    Possible required features:
    bid, bidhigh, bidlow, ask, askhigh, asklow, session_open, session_close, price_change
    
    additional feature can be created using calculating indicator values. 
    """
    
    if symbol_info is not None:
        
        lot = 0.01
        point = symbol_info.point
        price = symbol_info.ask
        deviation = 20
        
        print(f"point {point} {type(point)}, price {price}")
        
        print(f"symbol info {symbol_info}")
        
        result = mt5_obj.buy_symbol(price=price, lot=lot, point=point, deviation=deviation)
        
        mt5_obj.result_check(result=result)
        
        print(f"2. order_send done, {result}", )
        print(f"opened position with POSITION_TICKET={result.order}")
        print(f"sleep 2 seconds before closing position #{result.order}")
        
        # # create a close request
        # position_id=result.order
        # price=mt5.symbol_info_tick(symbol).bid
        # deviation=20
        # request={
        #     "action": mt5.TRADE_ACTION_DEAL,
        #     "symbol": symbol,
        #     "volume": lot,
        #     "type": mt5.ORDER_TYPE_SELL,
        #     "position": position_id,
        #     "price": price,
        #     "deviation": deviation,
        #     "magic": 234000,
        #     "comment": "python script close",
        #     "type_time": mt5.ORDER_TIME_GTC,
        #     "type_filling": mt5.ORDER_FILLING_RETURN,
        # }
        # # send a trading request
        # result=mt5.order_send(request)
        # # check the execution result
        # print("3. close position #{}: sell {} {} lots at {} with deviation={} points".format(position_id,symbol,lot,price,deviation));
        # if result.retcode != mt5.TRADE_RETCODE_DONE:
        #     print("4. order_send failed, retcode={}".format(result.retcode))
        #     print("   result",result)
        # else:
        #     print("4. position #{} closed, {}".format(position_id,result))
        #     # request the result as a dictionary and display it element by element
        #     result_dict=result._asdict()
        #     for field in result_dict.keys():
        #         print("   {}={}".format(field,result_dict[field]))
        #         # if this is a trading request structure, display it element by element as well
        #         if field=="request":
        #             traderequest_dict=result_dict[field]._asdict()
        #             for tradereq_filed in traderequest_dict:
        #                 print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
        
        # # shut down connection to the MetaTrader 5 terminal
        # mt5.shutdown()
    