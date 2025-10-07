# trading_bot/utils/indicators.py

import pandas as pd
import pandas_ta as ta

def calculate_vwap(df):
    """
    Calculates the Volume Weighted Average Price (VWAP).

    Args:
        df (pd.DataFrame): DataFrame with columns ['high', 'low', 'close', 'volume'].

    Returns:
        pd.DataFrame: DataFrame with an added 'VWAP' column.
    """
    df.ta.vwap(append=True)
    # pandas-ta names the column 'VWAP_D'. We'll rename it for consistency.
    if 'VWAP_D' in df.columns:
        df.rename(columns={'VWAP_D': 'VWAP'}, inplace=True)
    return df

def calculate_ema(df, length=25):
    """
    Calculates the Exponential Moving Average (EMA).

    Args:
        df (pd.DataFrame): DataFrame with a 'close' column.
        length (int): The time period for the EMA.

    Returns:
        pd.DataFrame: DataFrame with an added 'EMA' column.
    """
    df.ta.ema(length=length, append=True)
    return df

def get_historical_data(dhan, symbol, exchange, instrument_type, from_date, to_date, interval='5minute'):
    """
    Fetches historical data for a given symbol.

    NOTE: This is a placeholder. The actual implementation will depend on the
    specific function provided by the dhanhq library to fetch historical data.
    You might need to adjust the parameters and function calls accordingly.

    Args:
        dhan: An initialized DhanHQ API instance.
        symbol (str): The stock or index symbol.
        exchange (str): The exchange (e.g., 'NSE').
        instrument_type (str): The instrument type (e.g., 'EQUITY', 'FUTURE').
        from_date (str): The start date in 'YYYY-MM-DD' format.
        to_date (str): The end date in 'YYYY-MM-DD' format.
        interval (str): The data interval (e.g., '5minute', '15minute').

    Returns:
        pd.DataFrame: A DataFrame with historical OHLCV data.
    """
    print(f"Fetching {interval} historical data for {symbol} from {from_date} to {to_date}...")

    # This is a simulated response. In a real scenario, you would call a function like:
    # data = dhan.historical_daily_data(
    #     symbol=symbol,
    #     exchange=exchange,
    #     instrument_type=instrument_type,
    #     from_date=from_date,
    #     to_date=to_date
    # )
    # And for intraday:
    # data = dhan.intraday_daily_minute_charts(...)

    # Creating a sample DataFrame for demonstration purposes.
    # The actual data will have columns like 'open', 'high', 'low', 'close', 'volume'.
    data = {
        'date': pd.to_datetime(['2023-01-01 09:15:00', '2023-01-01 09:20:00', '2023-01-01 09:25:00', '2023-01-01 09:30:00']),
        'open': [100, 102, 101, 103],
        'high': [103, 104, 103, 105],
        'low': [99, 101, 100, 102],
        'close': [102, 103, 102, 104],
        'volume': [1000, 1200, 1100, 1300]
    }
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    return df

if __name__ == '__main__':
    # Example usage:
    # Create a sample DataFrame
    sample_data = {
        'date': pd.to_datetime(pd.date_range(start='2023-01-01', periods=50, freq='5min')),
        'open': [i for i in range(100, 150)],
        'high': [i + 2 for i in range(100, 150)],
        'low': [i - 2 for i in range(100, 150)],
        'close': [i + 1 for i in range(100, 150)],
        'volume': [1000 * (i % 5 + 1) for i in range(50)]
    }
    df_5min = pd.DataFrame(sample_data)
    df_5min.set_index('date', inplace=True)

    # Calculate VWAP on 5-min data
    df_5min_with_vwap = calculate_vwap(df_5min.copy())
    print("5-min DataFrame with VWAP:")
    print(df_5min_with_vwap.head())

    # Resample to 15-min for EMA calculation
    df_15min = df_5min['close'].resample('15min').ohlc()
    df_15min['volume'] = df_5min['volume'].resample('15min').sum()

    # Calculate 25-period EMA on 15-min data
    df_15min_with_ema = calculate_ema(df_15min.copy(), length=25)
    print("\n15-min DataFrame with 25 EMA:")
    print(df_15min_with_ema.head())