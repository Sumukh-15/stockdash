import os
import pandas as pd

def load_mock_csv(symbol: str) -> pd.DataFrame:
    # Replace dots in filename if you prefer; here we keep them as-is
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    path = os.path.join(data_dir, f"{symbol}.csv")
    if not os.path.exists(path):
        # Try AAPL.csv as generic fallback
        path = os.path.join(data_dir, "AAPL.csv")
    df = pd.read_csv(path, parse_dates=["Date"])
    df.set_index("Date", inplace=True)
    return df

def fetch_history(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Try live via yfinance; on any failure, fall back to mock CSV.
    Returns a DataFrame indexed by Date with columns: Open, High, Low, Close, Volume
    """
    try:
        import yfinance as yf
        df = yf.download(
            symbol, period=period, interval=interval,
            auto_adjust=False, progress=False, threads=False
        )
        if df is None or df.empty:
            raise RuntimeError("Empty live data")
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        return df
    except Exception:
        return load_mock_csv(symbol)
