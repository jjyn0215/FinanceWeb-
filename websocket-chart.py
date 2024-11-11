#!/usr/bin/env python
import asyncio
import websockets
from websockets import serve
import yfinance as yf
import json
from datetime import datetime, timedelta

async def handler(websocket):
    print("new Connection :", websocket.remote_address[0])
    message = json.loads(await websocket.recv())
    try:
        match message["type"]:
            case "ticker":
                while True:
                    try:
                        start_date = (datetime.today() - timedelta(days=6)).strftime('%Y-%m-%d')
                        end_date = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
                        print(websocket.remote_address[0], message["data"])
                        stock_data = yf.download(message["data"], start=start_date, end=end_date, interval='1m')
                        
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
                        event = {
                            "type" : "chart",
                            "data" : initialData,
                        }
                        await websocket.send(json.dumps(event, ensure_ascii=False))
                        await asyncio.sleep(1)
                    except websockets.exceptions.ConnectionClosed:
                        print("클라이언트 연결 끊김 :", websocket.remote_address[0])
                        break
    except Exception as e:
        print(e)


async def main():
    async with serve(handler, "localhost", 8765):
        print("server is now running")
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())