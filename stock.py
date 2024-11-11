import websocket
import ssl
import json

def on_message(ws, message):
    data = json.loads(message)

    # 'data' 리스트의 마지막 항목에서 'p' 값을 추출
    last_p_value = data['data'][-1]['p'] 
    print(last_p_value, data['data'][-1]['s'])

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    # Because on_close was triggered, we know the opcode = 8
    print("on_close args:")
    if close_status_code or close_msg:
        print("close status code: " + str(close_status_code))
        print("close message: " + str(close_msg))

def on_open(ws):
    #ws.send('{"type":"subscribe","symbol":"NVDA"}')

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=crrmjr1r01qmgcu63qpgcrrmjr1r01qmgcu63qq0",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})