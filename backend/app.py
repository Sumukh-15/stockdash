from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LinearRegression
import numpy as np

from schemas import Company, Candle, HistoryResponse, Metrics, PredictionResponse
from indicators import sma, rsi, compute_metrics
from datasource import fetch_history

ROOT = Path(__file__).resolve().parent
COMP_PATH = ROOT / "companies.json"

app = FastAPI(title="StockDash API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_companies():
    with open(COMP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/companies", response_model=list[Company])
def get_companies():
    return load_companies()

@app.get("/api/history", response_model=HistoryResponse)
def get_history(symbol: str, period: str = "1y", interval: str = "1d"):
    try:
        df = fetch_history(symbol, period=period, interval=interval)
        if df.empty:
            raise HTTPException(status_code=404, detail="No data for symbol")

        # indicators
        df["SMA20"] = sma(df["Close"], 20)
        df["SMA50"] = sma(df["Close"], 50)
        df["RSI14"] = rsi(df["Close"], 14)

        high_52w, low_52w, avg_volume = compute_metrics(df)

        candles = []
        for idx, row in df.iterrows():
            candles.append(Candle(
                date=idx.strftime("%Y-%m-%d"),
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=float(row["Volume"]),
                sma20=float(row["SMA20"]) if not pd.isna(row["SMA20"]) else None,
                sma50=float(row["SMA50"]) if not pd.isna(row["SMA50"]) else None,
                rsi14=float(row["RSI14"]) if not pd.isna(row["RSI14"]) else None,
            ))

        return HistoryResponse(
            symbol=symbol,
            candles=candles,
            metrics=Metrics(high_52w=high_52w, low_52w=low_52w, avg_volume=avg_volume),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predict/next", response_model=PredictionResponse)
def predict_next(symbol: str, period: str = "6mo", interval: str = "1d"):
    """
    Simple baseline "AI" prediction:
    Linear regression on time index -> next day's close.
    Not for trading; purely academic to meet the assignment bonus.
    """
    try:
        df = fetch_history(symbol, period=period, interval=interval)
        if df.shape[0] < 10:
            raise HTTPException(status_code=400, detail="Not enough data to predict")

        y = df["Close"].values.astype(float)
        X = np.arange(len(y)).reshape(-1, 1)
        model = LinearRegression()
        model.fit(X, y)
        next_x = np.array([[len(y)]])
        pred = float(model.predict(next_x)[0])

        return PredictionResponse(symbol=symbol, next_close_prediction=pred)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
