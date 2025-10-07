# VWAP and EMA Trading Bot

This project is a Python-based trading bot designed to backtest and execute a specific trading strategy using the DhanHQ API.

## Strategy

The bot implements the following strategy:

- **Setup**: Apply VWAP and a 15-min 25 EMA on a 5-min chart.
- **Entry Signal**: Price consolidates between VWAP & EMA, then breaks below both for a SELL.
- **Trade Execution**: Sell the At-the-Money (ATM) option.
- **Risk Management**: Fixed 50-point Stop-Loss. Position size is calculated so that the max loss per trade is <= 0.8% of capital.
- **Profit Protection**: Move SL to breakeven once a 50-point profit (1:1 R/R) is achieved.
- **Exit Signal**: Exit when a "reverse swing" (higher high in a downtrend) appears on the 15-min chart.

## Current Status

The bot is currently in **Phase 1: Backtesting**.

- **Backtesting Engine**: A functional backtesting engine is included, which can simulate the strategy's performance on historical data.
- **Placeholder Data**: **IMPORTANT:** The functions for fetching historical data (`get_historical_data`), finding ATM options (`get_atm_option`), and fetching derivative symbols (`get_derivative_symbols`) are currently **placeholders**. They use simulated data for demonstration and testing purposes. To connect to live data, these functions must be updated to use the actual DhanHQ API endpoints.
- **Live Trading**: The structure for live trading is in place but is not yet implemented.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure your credentials:**
    Open `trading_bot/config/settings.py` and replace the placeholder values with your actual DhanHQ Client ID and Access Token.
    ```python
    DHAN_CLIENT_ID = "YOUR_CLIENT_ID"
    DHAN_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
    ```

## How to Run

### Backtesting

To run a backtest, use the `backtest` mode and specify the symbol and other parameters.

```bash
python main.py --mode backtest --symbol BANKNIFTY --start_date 2023-01-01 --end_date 2023-01-31
```

### Live Trading (Future Implementation)

Once the live trading logic is implemented, you will be able to run the bot in `live` mode.

```bash
python main.py --mode live --symbol BANKNIFTY
```

## Next Steps

-   Replace placeholder functions with actual DhanHQ API calls for data fetching and order execution.
-   Implement the live trading loop with robust error handling and logging.
-   Add more comprehensive tests.