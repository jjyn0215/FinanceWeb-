from flask import Flask, request
from flask_socketio import SocketIO, emit, Namespace, join_room, leave_room
import yfinance as yf
import json
from datetime import datetime, timedelta
import asyncio
import math
import os
import requests
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor
import websocket
import sys
from pykrx import stock
from pykrx import bond
import threading

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet', logger=True, engineio_logger=False, cors_allowed_origins='*')

tickers = {}
roomData = []
stocklist = stock.get_market_ticker_list(market="ALL")
# for n in stocklist:
#     print(stock.get_market_ticker_name(n))

class ChartNamespace(Namespace):
    def on_connect(self):
        print("Chart Client connected.", request.sid, request.remote_addr)
        socketio.emit('welcome', request.remote_addr, namespace='/chart', to=request.sid)
        print(tickers)


    def on_disconnect(self):
        print("Chart Client disconnected.", request.sid, request.remote_addr)
        leave_room(tickers[request.sid])
        b = {
            "header": {"approval_key": i_approval_key, "custtype": "P", "tr_type": "2", "content-type": "utf-8"},
            "body": { "input": {
                                "tr_id": "H0STCNT0",  # API명
                                "tr_key": tickers[request.sid]  # 종목번호
                                }
                    }
        }
        global roomData
        tempticker = tickers[request.sid]
        del tickers[request.sid]
        roomData = set(tickers.values())
        if not tempticker in roomData:
            ws.send(json.dumps(b), websocket.ABNF.OPCODE_TEXT) #종목코드 1
        print(tickers)
        

    def on_join(self, ticker):
        join_room(ticker)
        b = {
            "header": {"approval_key": i_approval_key, "custtype": "P", "tr_type": "1", "content-type": "utf-8"},
            "body": { "input": {
                                "tr_id": "H0STCNT0",  # API명
                                "tr_key": ticker  # 종목번호
                                }
                    }
        }
        global roomData
        global ws
        if not ticker in roomData:
            ws.send(json.dumps(b), websocket.ABNF.OPCODE_TEXT) #종목코드 1
        tickers[request.sid] = ticker
        roomData = set(tickers.values())
        socketio.emit('name', stock.get_market_ticker_name(ticker), namespace='/chart', to=request.sid)

        # event = {
        #     'name': '?',
        #     'current': 0.00,
        #     'diff': 0.00,
        #     '%': 0.00,
        #     'isAfter': 1,
        #     'afterClosed': 0.00,
        #     'diff2': 0.00,
        #     '%2': 0.00
        # }




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

# def get_chart_data(): # 야후주식
#     while True:
#         try:
#             if len(tickers) != 0:
#                 print(tickers)
#                 roomData = set(tickers.values())
#                 ticker_info = yf.Tickers(' '.join(roomData))
#                 stock_data = yf.download(roomData, period=None, interval='1m', group_by='ticker')
#                 for ticker in roomData:
#                     print(roomData)
#                     if len(roomData) == 1: ticker_data = stock_data
#                     else: ticker_data = stock_data[ticker]
#                     header_info = ticker_info.tickers[ticker].info
#                     initialData = []
#                     for index, row in ticker_data.iterrows():
#                         if not math.isnan(row['Open']):
#                             data = {
#                                 "date": str(index),
#                                 "open": row['Open'],
#                                 "low": row['Low'],
#                                 "high": row['High'],
#                                 "close": row['Close'],
#                                 "volume": row['Volume']
#                             }
#                             initialData.append(data)
#                     event = {
#                         'name': header_info['shortName'],
#                         'current': 0.00,
#                         'diff': 0.00,
#                         '%': 0.00,
#                         'isAfter': 1,
#                         'afterClosed': 0.00,
#                         'diff2': 0.00,
#                         '%2': 0.00
#                     }
#                     socketio.emit('chart', json.dumps(initialData), namespace='/chart', to=ticker)
#                     try:
#                         after = yf.Ticker(ticker).history(prepost=True, period=None, interval='1m')
#                         afterData = []
#                         for index, row in after.iterrows():
#                             if not math.isnan(row['Open']):
#                                 data = {
#                                     "date": str(index),
#                                     "open": row['Open'],
#                                     "low": row['Low'],
#                                     "high": row['High'],
#                                     "close": row['Close'],
#                                     "volume": row['Volume']
#                                 }
#                                 afterData.append(data)
#                         event['current'] = header_info['currentPrice']
#                         event['diff'] = float(header_info['currentPrice']) - float(header_info['previousClose'])
#                         event['%'] = event['diff'] / float(header_info['previousClose']) * 100
#                         event['afterClosed'] = afterData[-1]['close']
#                         event['diff2'] = afterData[-1]['close'] - float(header_info['currentPrice'])
#                         event['%2'] = event['diff2'] / float(header_info['currentPrice']) * 100
#                         socketio.emit('header', json.dumps(event), namespace='/chart', to=ticker)
#                     except: 
#                         event['current'] = float(initialData[-1]['close'])
#                         event['diff'] = float(initialData[-1]['close']) - float(header_info['previousClose'])
#                         # print(initialData[-1]['date'])
#                         # diff_data = ''
#                         # for entry in initialData:
#                         #     if entry['date'] == str(datetime.fromisoformat(initialData[-1]['date']) - timedelta(days=1)):
#                         #         diff_data = entry['close']
#                         #         event['diff'] = float(event['current']) - float(diff_data)
#                         #         break
#                         event['%'] = event['diff'] / float(header_info['previousClose']) * 100
#                         event['isAfter'] = 0
#                         socketio.emit('header', json.dumps(event), namespace='/chart', to=ticker)
                        
#                     #socketio.emit('header', json.dumps(initialData), namespace='/header', to=ticker)
#         except Exception as e:
#             print('err :', e)
#         socketio.sleep(1)

# @socketio.on('connect', namespace='/*')
# def handle_connect():
#     print("Client connected.")

# @socketio.on('disconnect')
# def handle_disconnect():
#     print("Client disconnected.")

### 한국투자증권 ### 

# 웹소켓 접속키 발급
def get_approval(key, secret):
    # url = https://openapivts.koreainvestment.com:29443' # 모의투자계좌     
    url = 'https://openapi.koreainvestment.com:9443' # 실전투자계좌
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials",
            "appkey": key,
            "secretkey": secret}
    PATH = "oauth2/Approval"
    URL = f"{url}/{PATH}"
    time.sleep(0.05)
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    approval_key = res.json()["approval_key"]
    return approval_key    
    
i_stock = ["005930","011700","000270"]
i_appkey    = "PSedNV2FutO0im3DxCJ6vhit84wHyyfC6ZxY"
i_appsecret = "fnAIq3eGjYzdlIaaQcpSxWh3rtfTYh/JqUdiBdtd455FqVOH0/AmrOp4Tv30mlufobSclfiuUl6EM7vj0/JBGf2DpoCa74VNGz4yx4rjiR2702LNHg2rcUHJevgDMXzlMx+uNWwTFjrdrDwyjq7Q3nR+AMGOemoOkTp1YtclMbfKzolxhtc="
i_approval_key = get_approval(i_appkey, i_appsecret)
print("approval_key [%s]" % (i_approval_key))

# b = {
#     "header": {"approval_key": i_approval_key, "custtype": "P", "tr_type": "1", "content-type": "utf-8"},
#     "body": { "input": {"tr_id": "H0STCNT0",  # API명
#                         "tr_key": i_stock[0]  # 종목번호
#                        }
#             }
# }
# b2 = {
#     "header": {"approval_key": i_approval_key, "custtype": "P", "tr_type": "1", "content-type": "utf-8"},
#     "body": { "input": {"tr_id": "H0STCNT0",  # API명
#                         "tr_key": i_stock[1]  # 종목번호
#                        }
#             }
# }
# b3 = {
#     "header": {"approval_key": i_approval_key, "custtype": "P", "tr_type": "1", "content-type": "utf-8"},
#     "body": { "input": {"tr_id": "H0STCNT0",  # API명
#                         "tr_key": i_stock[2]  # 종목번호
#                        }
#             }
# }

# Pandas DataFrame 이용

pricetmp = 0.00
def on_message(ws, data):
    #print('type=', type(data), '\ndata=', data)

    def pdbind(result):
        
        if result[2] != pricetmp:
            event = {
            'current': float(result[2]),
            'diff': float(result[4]),
            '%': float(result[5]),
            'isAfter': 1,
            'afterClosed': 0.00,
            'diff2': 0.00,
            '%2': 0.00
            }
            socketio.emit('header', json.dumps(event), namespace='/chart', to=result[0])
            # socketio.start_background_task(socketio.emit('header', json.dumps(event), namespace='/chart', to=result[0]))
            # socketio.start_background_task(send_socket, event)
            print("종목코드1:",result[0], " 체결시간:", result[1], " 현재가:", result[2], result[4], result[5])

        # if i_stock[1] == result[0]:
        #     print("종목코드2:",result[0], " 체결시간:", result[1], " 현재가:", result[2])
        # if i_stock[2] == result[0]:
        #     print("종목코드3:",result[0], " 체결시간:", result[1], " 현재가:", result[2])
        pricetmp = result[2]
    if data[0] in ['0', '1']:  # 시세데이터가 아닌경우
        d1 = data.split("|")
        if len(d1) >= 4:
            isEncrypt = d1[0]
            tr_id = d1[1]
            tr_cnt = d1[2]
            recvData = d1[3]
            result = recvData.split("^")
            #print("start time=", result[1])
            socketio.start_background_task(pdbind(result))
            # pdbind(result)  # pandas dataframe 이용 변경
        else:
            print('Data Size Error=', len(d1))
    else:
        recv_dic = json.loads(data)
        tr_id = recv_dic['header']['tr_id']

        if tr_id == 'PINGPONG':
            send_ping = recv_dic
            ws.send(data, websocket.ABNF.OPCODE_PING)
        else:  # parser data
            print('tr_id=', tr_id, '\nmsg=', data)

def on_error(ws, error):
    print('error=', error)

def on_close(ws, status_code, close_msg):
    print('on_close close_status_code=', status_code, " close_msg=", close_msg)
    start_websocket()
    

def on_open(ws):
    print('on_open')
    # ws.send(json.dumps(b), websocket.ABNF.OPCODE_TEXT) #종목코드 1
    # ws.send(json.dumps(b2), websocket.ABNF.OPCODE_TEXT) #종목코드 2
    # ws.send(json.dumps(b3), websocket.ABNF.OPCODE_TEXT)  # 종목코드 3

# 모의투자
# ws = websocket.WebSocketApp("ws://ops.koreainvestment.com:31000",
#                             on_open=on_open, on_message=on_message, on_error=on_error)    
    
# def send_socket(event):
#     socketio.emit('header', json.dumps(event), namespace='/chart', )
    

def start_websocket():
    global ws
    try:
        while True:
            ws = websocket.WebSocketApp(
                "ws://ops.koreainvestment.com:21000",
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever()

    except Exception as e:
        print('err :', e)

socketio.on_namespace(ChartNamespace('/chart'))

if __name__ == '__main__':
    # socketio.start_background_task(get_chart_data)
    try:
        # with ThreadPoolExecutor() as executor:
        #     executor.submit(start_websocket)
        # threading.Thread(target=start_websocket).start()
        threading.Thread(target=start_websocket).start()
        socketio.run(app, host='localhost', port=8765)

    except KeyboardInterrupt:
        sys.exit(0)
        


