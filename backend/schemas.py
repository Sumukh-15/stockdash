from pydantic import BaseModel
from typing import List, Optional

class Company(BaseModel):
    symbol: str
    name: str

class Candle(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    sma20: Optional[float] = None
    sma50: Optional[float] = None
    rsi14: Optional[float] = None

class Metrics(BaseModel):
    high_52w: float
    low_52w: float
    avg_volume: float

class HistoryResponse(BaseModel):
    symbol: str
    candles: List[Candle]
    metrics: Metrics

class PredictionResponse(BaseModel):
    symbol: str
    next_close_prediction: float
