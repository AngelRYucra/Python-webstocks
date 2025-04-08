import websockets
import asyncio
import json

class WS:
    def __init__(self, hostname):
        self.hostname = hostname
        self.ws = None

    async def connect(self):

        subscribe_request = {
            "method": "SUBSCRIBE",
            "params": [
                "btcusdt@ticker",
                "ethusdt@ticker"
            ],
            "id": 1
        }
        print(self.hostname)
        try:
            async with websockets.connect(self.hostname) as ws:
                print("Connected to WS")
                # await ws.send(json.dumps(subscribe_request))
                while True:
                    message = await ws.recv()
                    print(message)
        except Exception as e:
            print(f"Error connecting: {e}")

    def subscribe(self,ticker):
        self.ticker = ticker
        print(ticker)

    def handle_message(self):
        msg = self.connect()
        print(f"Received: {msg}")


async def main():
    ws = WS("wss://stream.binance.com:9443/ws")
    print(ws.hostname)
    await ws.connect()

if __name__ == "__main__":
    asyncio.run(main())