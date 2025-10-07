# trading_bot/core/api.py

from dhanhq import dhanhq
from trading_bot.config import settings

def get_dhan_api_instance():
    """
    Initializes and returns a DhanHQ API instance.
    """
    if settings.DHAN_ACCESS_TOKEN == "YOUR_ACCESS_TOKEN" or settings.DHAN_CLIENT_ID == "YOUR_CLIENT_ID":
        raise ValueError("Please replace 'YOUR_ACCESS_TOKEN' and 'YOUR_CLIENT_ID' with your actual DhanHQ credentials in trading_bot/config/settings.py")

    return dhanhq(client_id=settings.DHAN_CLIENT_ID, access_token=settings.DHAN_ACCESS_TOKEN)

def get_derivative_symbols(dhan):
    """
    Fetches the list of all derivative (futures and options) symbols.

    Args:
        dhan: An initialized DhanHQ API instance.

    Returns:
        A list of derivative symbols.
    """
    try:
        # This is a placeholder for the actual function call.
        # The dhanhq library documentation should be consulted for the correct function.
        # For now, we will simulate fetching some symbols.
        print("Fetching derivative symbols from DhanHQ...")
        # In a real implementation, you would use a function like:
        # return dhan.get_all_scrips(exchange='NFO')
        # For now, returning a sample list.
        return ["BANKNIFTY", "NIFTY", "FINNIFTY", "RELIANCE", "INFY"]
    except Exception as e:
        print(f"Error fetching derivative symbols: {e}")
        return []

if __name__ == '__main__':
    # Example usage:
    try:
        dhan = get_dhan_api_instance()
        derivative_symbols = get_derivative_symbols(dhan)
        print("Available Derivative Symbols:")
        for symbol in derivative_symbols:
            print(f"- {symbol}")
    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(f"An error occurred: {e}")