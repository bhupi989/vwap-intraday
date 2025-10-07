# trading_bot/core/strategy.py

import pandas as pd
from trading_bot.config import settings

def calculate_position_size(capital, risk_percent, sl_points, lot_size):
    """
    Calculates the position size (number of lots) based on risk parameters.

    Args:
        capital (float): Total trading capital.
        risk_percent (float): The percentage of capital to risk per trade.
        sl_points (float): The stop-loss in points for one share/unit.
        lot_size (int): The number of shares/units in one lot.

    Returns:
        int: The number of lots to trade.
    """
    max_loss_per_trade = capital * (risk_percent / 100)
    risk_per_lot = sl_points * lot_size

    if risk_per_lot <= 0:
        return 0

    num_lots = int(max_loss_per_trade / risk_per_lot)
    return num_lots

def check_entry_signal(df_5min, df_15min_ema):
    """
    Checks for the SELL entry signal based on the strategy rules.

    Args:
        df_5min (pd.DataFrame): 5-minute OHLCV data with VWAP calculated.
        df_15min_ema (pd.Series): 15-minute 25-period EMA values.

    Returns:
        bool: True if a SELL signal is found, False otherwise.
    """
    if len(df_5min) < 2 or df_15min_ema.isna().all():
        return False

    # Get the latest data
    last_candle = df_5min.iloc[-1]
    prev_candle = df_5min.iloc[-2]

    # Align 15-min EMA to the 5-min timeframe
    # We forward-fill the EMA value to apply it to each 5-min candle
    aligned_ema = df_15min_ema.reindex(df_5min.index, method='ffill')

    # Check for valid data
    if pd.isna(aligned_ema.iloc[-1]) or pd.isna(last_candle['VWAP']):
        return False

    # Entry condition: Price breaks below both VWAP and 15-min EMA
    # after a period of consolidation.

    # 1. Define consolidation: Price was between VWAP and EMA previously.
    # This is a simplified check. A more robust check might look at a longer period.
    vwap = prev_candle['VWAP']
    ema = aligned_ema.iloc[-2]
    upper_band = max(vwap, ema)
    lower_band = min(vwap, ema)

    consolidating = (prev_candle['close'] > lower_band and prev_candle['close'] < upper_band)

    # 2. Define breakdown: Current price is below both VWAP and EMA.
    breakdown = (last_candle['close'] < last_candle['VWAP'] and last_candle['close'] < aligned_ema.iloc[-1])

    if consolidating and breakdown:
        print(f"SELL SIGNAL DETECTED at {last_candle.name}: Price {last_candle['close']}")
        return True

    return False

def check_exit_signal(df_15min):
    """
    Checks for the exit signal (reverse swing) on the 15-min chart.

    Args:
        df_15min (pd.DataFrame): 15-minute OHLC data.

    Returns:
        bool: True if an exit signal is found, False otherwise.
    """
    if len(df_15min) < 3:
        return False

    # A "reverse swing" in a downtrend is a higher high.
    # We check if the last completed candle's high is greater than the previous one's.
    last_high = df_15min.iloc[-2]['high']
    prev_high = df_15min.iloc[-3]['high']

    if last_high > prev_high:
        print(f"EXIT SIGNAL (Reverse Swing) DETECTED at {df_15min.iloc[-1].name}")
        return True

    return False

def get_atm_option(dhan, symbol, expiry_date):
    """
    Finds the At-the-Money (ATM) option for a given symbol.

    NOTE: This is a placeholder. The actual implementation requires fetching
    the current price of the underlying and then searching the option chain.

    Args:
        dhan: An initialized DhanHQ API instance.
        symbol (str): The underlying symbol (e.g., 'BANKNIFTY').
        expiry_date (str): The option's expiry date.

    Returns:
        str: The trading symbol for the ATM PUT option.
    """
    # 1. Get current market price of the underlying
    # spot_price = dhan.get_quote(symbol)['last_price']
    spot_price = 45000  # Simulated spot price

    # 2. Find the closest strike price
    # strike_prices = dhan.get_option_chain(symbol, expiry_date)['strikes']
    strike_prices = [44800, 44900, 45000, 45100, 45200] # Simulated
    atm_strike = min(strike_prices, key=lambda x:abs(x-spot_price))

    # 3. Construct the option symbol (this format will vary by broker)
    # This is a simplified example.
    atm_option_symbol = f"{symbol}_{expiry_date}_{atm_strike}_PE"

    print(f"Determined ATM PUT option: {atm_option_symbol}")
    return atm_option_symbol


if __name__ == '__main__':
    # Example Usage:
    # 1. Position Sizing
    capital = settings.TOTAL_CAPITAL
    risk_percent = settings.RISK_PER_TRADE_PERCENT
    sl_points = 50
    banknifty_lot_size = 15  # Example for Bank Nifty

    lots = calculate_position_size(capital, risk_percent, sl_points, banknifty_lot_size)
    print(f"Capital: {capital}, Risk: {risk_percent}%, SL: {sl_points}pts")
    print(f"Calculated position size: {lots} lots for Bank Nifty (Lot Size: {banknifty_lot_size})")

    # 2. Entry/Exit Signal Check (using sample data)
    # Create sample dataframes
    from trading_bot.utils.indicators import calculate_vwap, calculate_ema

    # Sample 5-min data
    data_5min = {
        'open':  [101, 102, 101, 100],
        'high':  [103, 103, 102, 101],
        'low':   [100, 101, 100, 99],
        'close': [102, 101.5, 101.2, 99],
        'volume':[1000, 1100, 1200, 1500]
    }
    idx_5min = pd.to_datetime(['2023-01-01 09:20', '2023-01-01 09:25', '2023-01-01 09:30', '2023-01-01 09:35'])
    df_5min = pd.DataFrame(data_5min, index=idx_5min)
    df_5min = calculate_vwap(df_5min)

    # Sample 15-min data for EMA
    data_15min = {'close': [102, 101]}
    idx_15min = pd.to_datetime(['2023-01-01 09:15', '2023-01-01 09:30'])
    df_15min = pd.DataFrame(data_15min, index=idx_15min)
    df_15min = calculate_ema(df_15min, length=25)

    # Set VWAP and EMA to create a signal
    df_5min['VWAP'] = [101.8, 101.7, 101.6, 101.5]
    df_15min[df_15min.columns[-1]] = [101.9, 101.8] # EMA column

    print("\nChecking for entry signal...")
    signal = check_entry_signal(df_5min, df_15min.iloc[:, -1])
    print(f"Entry signal found: {signal}")

    # Sample 15-min data for exit check
    exit_check_data = {
        'open': [100, 98, 97], 'high': [101, 99, 100],
        'low': [98, 97, 96], 'close': [99, 97, 98], 'volume': [1,1,1]
    }
    exit_df = pd.DataFrame(exit_check_data, index=pd.to_datetime(['09:45', '10:00', '10:15']))
    print("\nChecking for exit signal...")
    exit_signal = check_exit_signal(exit_df)
    print(f"Exit signal found: {exit_signal}")