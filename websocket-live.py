#!/usr/bin/env python
import asyncio
import websockets
import json

EXTERNAL_WS_URL = "wss://ws.finnhub.io?token=crrmjr1r01qmgcu63qpgcrrmjr1r01qmgcu63qq0"
clients = {}
external_ws = None  # 외부 WebSocket 연결 객체를 저장할 전역 변수

async def start_external_ws():
    global external_ws
    external_ws = await websockets.connect(EXTERNAL_WS_URL)
    message = await external_ws.recv()

    data = json.loads(message)
    print(data)
    symbol = data.get("s")
    
    # 구독 중인 티커의 데이터를 각 클라이언트에게 전송
    if symbol in clients:
        for websocket in clients[symbol]:
            await websocket.send(json.dumps(data))
        


async def handler(websocket):
    print("New Connection:", websocket.remote_address[0])

    try:
        while True:
            message = json.loads(await websocket.recv())
            action = message.get("type")
            ticker = message.get("data")

            # 외부 WebSocket 세션에 subscribe/unsubscribe 요청 보내기
            if action == "subscribe" and external_ws:
                await external_ws.send(json.dumps({"type": "subscribe", "symbol": ticker}))

                # 각 티커에 대해 클라이언트 추가
                if ticker not in clients:
                    clients[ticker] = set()
                clients[ticker].add(websocket)

            elif action == "unsubscribe" and external_ws:
                await external_ws.send(json.dumps({"type": "unsubscribe", "symbol": ticker}))

                # 클라이언트를 티커 목록에서 제거
                if ticker in clients:
                    clients[ticker].discard(websocket)
                    if not clients[ticker]:  # 더 이상 구독 중인 클라이언트가 없으면 삭제
                        del clients[ticker]

    except websockets.exceptions.ConnectionClosed:
        print("Connection closed by client")
    finally:
        # 클라이언트가 연결을 종료할 경우 구독에서 삭제
        for tickers, websockets in clients.items():
            websockets.discard(websocket)
            if not websockets:
                del clients[tickers]

async def main():
    # 외부 WebSocket과 클라이언트 서버를 병렬로 실행
    external_ws_task = asyncio.create_task(start_external_ws())
    client_server_task = websockets.serve(handler, "localhost", 8766)

    await asyncio.gather(external_ws_task, client_server_task)

if __name__ == "__main__":
    asyncio.run(main())
