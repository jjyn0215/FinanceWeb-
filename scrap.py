
from flask import Flask, jsonify, render_template, request, make_response
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')  # index.html 파일 렌더링

@app.route('/api/get-stock-data', methods=['GET'])
def get_stock_data():
    ticker = 'AAPL'  # 예시: Apple 주식
    start_date = '2024-08-26'
    end_date = '2024-09-26'

    # yfinance를 통해 주식 데이터를 다운로드합니다.
    stock_data = yf.download(ticker, start=start_date, end=end_date, interval='15m')

    # 필요한 형식에 맞게 데이터를 변환합니다.
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

@app.route('/api/get-popular-stocks', methods=['GET'])
def get_popular_stocks():
    try:
        popular_stocks = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corp.'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.'}
        ]
        
        return jsonify(popular_stocks)  # 인기 종목 리스트 반환
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 오류 메시지를 JSON 형식으로 반환

@app.route('/api/download-csv', methods=['GET'])
def download_csv():
    symbol = request.args.get('symbol', 'AAPL')  # 기본값은 AAPL
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="2y")
        
        # CSV 파일로 저장
        csv_data = data.to_csv()
        
        response = make_response(csv_data)
        response.headers["Content-Disposition"] = f"attachment; filename={symbol}_data.csv"
        response.headers["Content-type"] = "text/csv"
        
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 오류 메시지를 JSON 형식으로 반환

if __name__ == '__main__':
    app.run(debug=True)  # 디버그 모드로 실행