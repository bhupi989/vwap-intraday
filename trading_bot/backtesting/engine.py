# trading_bot/backtesting/engine.py

import pandas as pd
from trading_bot.config import settings
from trading_bot.utils.indicators import get_historical_data, calculate_vwap, calculate_ema
from trading_bot.core.strategy import check_entry_signal, check_exit_signal, calculate_position_size

class Backtester:
    def __init__(self, symbol, start_date, end_date, capital, risk_percent, sl_points, lot_size=1):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.capital = capital
        self.risk_percent = risk_percent
        self.sl_points = sl_points
        self.lot_size = lot_size

        self.trades = []
        self.in_trade = False
        self.current_trade = {}

    def _prepare_data(self):
        """
        Fetches and prepares historical data for backtesting.
        """
        # Fetch 5-minute data
        df_5min = get_historical_data(None, self.symbol, 'NSE', 'EQUITY', self.start_date, self.end_date, interval='5minute')
        if df_5min.empty:
            print("No 5-minute data available for the given period.")
            return None, None

        # Calculate VWAP on 5-min data
        self.df_5min = calculate_vwap(df_5min)

        # Resample 5-min data to 15-min
        ohlc_15min = self.df_5min['close'].resample('15min').ohlc()
        volume_15min = self.df_5min['volume'].resample('15min').sum()
        df_15min = ohlc_15min.join(volume_15min)

        # Calculate 25 EMA on 15-min data
        self.df_15min = calculate_ema(df_15min, length=25)

        # Align 15-min EMA to 5-min index for signal checking
        ema_col_name = self.df_15min.columns[-2] # EMA is the second to last column
        self.aligned_ema = self.df_15min[ema_col_name].reindex(self.df_5min.index, method='ffill')

    def run(self):
        """
        Runs the backtest over the prepared data.
        """
        self._prepare_data()

        if self.df_5min is None:
            return

        print(f"\n--- Running Backtest for {self.symbol} ---")
        print(f"Period: {self.start_date} to {self.end_date}\n")

        for i in range(1, len(self.df_5min)):
            # We need at least one previous candle to check for signals
            current_5min_slice = self.df_5min.iloc[:i+1]
            current_15min_slice = self.df_15min[self.df_15min.index <= current_5min_slice.index[-1]]

            if self.in_trade:
                self._manage_trade(current_5min_slice, current_15min_slice)
            else:
                self._check_for_entry(current_5min_slice)

        self._print_results()

    def _check_for_entry(self, current_data_slice):
        """
        Checks for an entry signal at the current timestamp.
        """
        # Pass the 15-min EMA series to the entry signal check
        ema_series = self.aligned_ema.loc[:current_data_slice.index[-1]]

        if check_entry_signal(current_data_slice, ema_series):
            self._execute_trade(current_data_slice.iloc[-1])

    def _execute_trade(self, entry_candle):
        """
        Simulates executing a trade.
        """
        self.in_trade = True
        entry_price = entry_candle['close']
        entry_time = entry_candle.name

        position_size = calculate_position_size(self.capital, self.risk_percent, self.sl_points, self.lot_size)
        if position_size == 0:
            print("Position size is zero. Skipping trade.")
            self.in_trade = False
            return

        self.current_trade = {
            'symbol': self.symbol,
            'entry_time': entry_time,
            'entry_price': entry_price,
            'position_size': position_size,
            'sl_price': entry_price + self.sl_points, # For a SELL trade, SL is higher
            'breakeven_price': entry_price - self.sl_points, # 1:1 R/R target
            'status': 'open',
            'sl_at_breakeven': False
        }
        print(f"\nNew Trade Opened @ {entry_time}:")
        print(f"  Entry Price: {entry_price:.2f}, SL: {self.current_trade['sl_price']:.2f}")

    def _manage_trade(self, current_5min_data, current_15min_data):
        """
        Manages an open trade, checking for SL, TP, or exit signals.
        """
        latest_candle = current_5min_data.iloc[-1]

        # 1. Check for Stop-Loss
        if latest_candle['high'] >= self.current_trade['sl_price']:
            self._close_trade(self.current_trade['sl_price'], latest_candle.name, "Stop-Loss Hit")
            return

        # 2. Check for Profit Target to move SL to Breakeven
        if not self.current_trade['sl_at_breakeven'] and latest_candle['low'] <= self.current_trade['breakeven_price']:
            self.current_trade['sl_price'] = self.current_trade['entry_price']
            self.current_trade['sl_at_breakeven'] = True
            print(f"  Trade Update @ {latest_candle.name}: SL moved to Breakeven ({self.current_trade['sl_price']:.2f})")

        # 3. Check for Reverse Swing Exit Signal on 15-min chart
        if check_exit_signal(current_15min_data):
            self._close_trade(latest_candle['close'], latest_candle.name, "Reverse Swing Exit")

    def _close_trade(self, exit_price, exit_time, reason):
        """
        Simulates closing an open trade.
        """
        self.in_trade = False
        trade = self.current_trade
        trade['exit_time'] = exit_time
        trade['exit_price'] = exit_price
        trade['status'] = 'closed'
        trade['reason'] = reason

        # PnL for a SELL trade
        trade['pnl'] = (trade['entry_price'] - trade['exit_price']) * trade['position_size'] * self.lot_size

        self.trades.append(trade)
        print(f"Trade Closed @ {exit_time}:")
        print(f"  Exit Price: {exit_price:.2f}, Reason: {reason}, PnL: {trade['pnl']:.2f}\n")

    def _print_results(self):
        """
        Prints the summary of the backtest.
        """
        print("\n--- Backtest Results ---")
        if not self.trades:
            print("No trades were executed.")
            return

        results_df = pd.DataFrame(self.trades)
        total_pnl = results_df['pnl'].sum()
        num_trades = len(results_df)
        wins = results_df[results_df['pnl'] > 0]
        losses = results_df[results_df['pnl'] <= 0]
        win_rate = (len(wins) / num_trades) * 100 if num_trades > 0 else 0

        print(f"Total Trades: {num_trades}")
        print(f"Total PnL: {total_pnl:.2f}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Average PnL per trade: {results_df['pnl'].mean():.2f}")
        print("\nIndividual Trades:")
        print(results_df[['entry_time', 'exit_time', 'entry_price', 'exit_price', 'pnl', 'reason']])
        print("\n-----------------------\n")


if __name__ == '__main__':
    # Example Usage:
    backtester = Backtester(
        symbol='BANKNIFTY',
        start_date='2023-01-01',
        end_date='2023-01-02',
        capital=settings.TOTAL_CAPITAL,
        risk_percent=settings.RISK_PER_TRADE_PERCENT,
        sl_points=50,
        lot_size=15
    )
    backtester.run()