from flask import Flask
import yfinance as yf
import json
from datetime import datetime, timedelta

app = Flask(__name__)

def getData():
    ticker = 'NVDA' 
    start_date = (datetime.today() - timedelta(days=6)).strftime('%Y-%m-%d')
    end_date = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d') 

    stock_data = yf.download(ticker, start=start_date, end=end_date, interval='1m')

    initialData = []
    for index, row in stock_data.iterrows():
        data = {
            "date": str(index),
            "open": row['Open'],
            "low": row['Low'],
            "high": row['High'],
            "close": row['Close'],
            "volume": row['Volume']
        }
        initialData.append(data)
    return initialData

@app.route("/data")
def backData():
    return json.dumps(getData(), ensure_ascii=False)

if __name__ == "__main__":
    app.run(debug=True)