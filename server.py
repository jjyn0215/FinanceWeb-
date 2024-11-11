from flask import Flask, request
from flask_socketio import SocketIO, emit, Namespace, join_room, leave_room
import yfinance as yf
import json
from datetime import datetime, timedelta
import asyncio
import math


app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet', logger=True, engineio_logger=False, cors_allowed_origins='*')

tickers = {}

class ChartNamespace(Namespace):
    def on_connect(self):
        print("Chart Client connected.", request.sid, request.remote_addr)
        socketio.emit('welcome', request.remote_addr, namespace='/chart', to=request.sid)

    def on_disconnect(self):
        print("Chart Client disconnected.", request.sid, request.remote_addr)
        leave_room(tickers[request.sid])
        del tickers[request.sid]

    def on_join(self, ticker):
        join_room(ticker)
        tickers[request.sid] = ticker


# @socketio.on('connect', namespace='/header')
# def handle_connect():
#     print("Header Client connected.", request.sid, request.remote_addr)

# @socketio.on('disconnect', namespace='/header')
# def handle_disconnect():
#     leave_room(ticker)
    
# @socketio.on('join', namespace='/header')
# def handle_join(ticker):
#     join_room(ticker)

     
@app.route("/")
def get_Data():
    pass

def get_chart_data():
    while True:
        try:
            if len(tickers) != 0:
                print(tickers)
                roomData = set(tickers.values())
                ticker_info = yf.Tickers(' '.join(roomData))
                stock_data = yf.download(roomData, period=None, interval='1m', group_by='ticker')
                for ticker in roomData:
                    print(roomData)
                    if len(roomData) == 1: ticker_data = stock_data
                    else: ticker_data = stock_data[ticker]
                    header_info = ticker_info.tickers[ticker].info
                    initialData = []
                    for index, row in ticker_data.iterrows():
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
                    event = {
                        'name': header_info['shortName'],
                        'current': 0.00,
                        'diff': 0.00,
                        '%': 0.00,
                        'isAfter': 1,
                        'afterClosed': 0.00,
                        'diff2': 0.00,
                        '%2': 0.00
                    }
                    socketio.emit('chart', json.dumps(initialData), namespace='/chart', to=ticker)
                    try:
                        after = yf.Ticker(ticker).history(prepost=True, period=None, interval='1m')
                        afterData = []
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
                                afterData.append(data)
                        event['current'] = header_info['currentPrice']
                        event['diff'] = float(header_info['currentPrice']) - float(header_info['previousClose'])
                        event['%'] = event['diff'] / float(header_info['previousClose']) * 100
                        event['afterClosed'] = afterData[-1]['close']
                        event['diff2'] = afterData[-1]['close'] - float(header_info['currentPrice'])
                        event['%2'] = event['diff2'] / float(header_info['currentPrice']) * 100
                        socketio.emit('header', json.dumps(event), namespace='/chart', to=ticker)
                    except: 
                        event['current'] = float(initialData[-1]['close'])
                        event['diff'] = float(initialData[-1]['close']) - float(header_info['previousClose'])
                        # print(initialData[-1]['date'])
                        # diff_data = ''
                        # for entry in initialData:
                        #     if entry['date'] == str(datetime.fromisoformat(initialData[-1]['date']) - timedelta(days=1)):
                        #         diff_data = entry['close']
                        #         event['diff'] = float(event['current']) - float(diff_data)
                        #         break
                        event['%'] = event['diff'] / float(header_info['previousClose']) * 100
                        event['isAfter'] = 0
                        socketio.emit('header', json.dumps(event), namespace='/chart', to=ticker)
                        
                    #socketio.emit('header', json.dumps(initialData), namespace='/header', to=ticker)
        except Exception as e:
            print('err :', e)
        socketio.sleep(1)

# @socketio.on('connect', namespace='/*')
# def handle_connect():
#     print("Client connected.")

# @socketio.on('disconnect')
# def handle_disconnect():
#     print("Client disconnected.")

socketio.on_namespace(ChartNamespace('/chart'))

if __name__ == '__main__':
    socketio.start_background_task(get_chart_data)
    socketio.run(app, host='localhost', port=8765)

