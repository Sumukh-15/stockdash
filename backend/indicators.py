import numpy as np
import pandas as pd

def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()

def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.clip(lower=0)).rolling(window=window, min_periods=window).mean()
    loss = (-delta.clip(upper=0)).rolling(window=window, min_periods=window).mean()
    rs = gain / (loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi

def compute_metrics(df: pd.DataFrame):
    # expects columns: 'High','Low','Volume'
    high_52w = float(df["High"].max())
    low_52w = float(df["Low"].min())
    avg_volume = float(df["Volume"].mean())
    return high_52w, low_52w, avg_volume
