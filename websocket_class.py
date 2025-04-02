import websockets
import asyncio
import json

class WS:
    def __init__(self, hostname):
        self.hostname = hostname

    async def connect(self):
        websocket_url = self.hostname
        try:
            async with websockets.connect(websocket_url) as ws:
                print("Connected to WS")
                while True:
                    message = await ws.recv()
                    return(message)
        except Exception as e:
            print(f"Error connecting: {e}")

    def subscribe(self,ticker):
        self.ticker = ticker
        print(ticker)

    def handle_message(self):
        msg = self.connect()
        print(f"Received: {msg}")

ws = WS("wss://stream.binance.com:9443/ws/btcusdt@trade")
print(ws.hostname)
asyncio.run(ws.connect())
asyncio.run(ws.handle_message())