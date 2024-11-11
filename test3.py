import yfinance as yf
import math

ticker = yf.Ticker("BTC-CAD")
after = ticker.history(interval='1m', period=None, prepost=True)
initialData = []
for index, row in after.iterrows():
    if not math.isnan(row['Open']):
        data = {
            "date": str(index),
            "open": row['Open'],
            "low": row['Low'],
            "high": row['High'],
            "close": row['Close'],
            "volume": row['Volume']
        }
        initialData.append(data)

print(ticker.info)