import asyncio
import websockets
import json
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import functools
import matplotlib.ticker as mticker
import io
import threading
from flask import Flask, Response

matplotlib.use('Agg')

# Flask app
app = Flask(__name__)
ws_instance = None  # Will be assigned in main()


class WS:
    def __init__(self, hostname):
        self.hostname = hostname
        self.ws = None
        self.prices = {}
        self.symbol_to_plot = "XRPUSDT"

    async def connect(self):
        try:
            self.ws = await websockets.connect(self.hostname)
            print(f"Connected to {self.hostname}")
        except Exception as e:
            print(f"Error connecting: {e}")

    async def subscribe(self, tickers):
        if not self.ws:
            print("WebSocket is not connected. Call connect() first.")
            return

        subscribe_request = {
            "method": "SUBSCRIBE",
            "params": tickers,
            "id": 1
        }
        try:
            await self.ws.send(json.dumps(subscribe_request))
            print(f"Subscribed to: {tickers}")
        except Exception as e:
            print(f"Error sending subscription: {e}")

    async def receive_messages(self):
        if not self.ws:
            print("WebSocket is not connected. Call connect() first.")
            return

        try:
            while True:
                msg = await self.ws.recv()
                data = json.loads(msg)
                self.handle_message(data)
                self.store_values(data)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed.")
        except Exception as e:
            print(f"Error while receiving messages: {e}")

    def handle_message(self, data):
        if 's' in data:
            print("Received message:", data['s'], "Price: ", data['c'])

    def store_values(self, data):
        symbol = data.get('s')
        if symbol:
            if symbol not in self.prices:
                self.prices[symbol] = []
            prices = self.prices[symbol]
            prices.append(float(data['c']))
            if len(prices) > 10:
                prices.pop(0)
            print("Prices: ", symbol, prices)

    def chart(self, symbol=None, return_image=False):
        if symbol is None:
            symbol = self.symbol  # fallback to default if not provided

        prices = self.prices.get(symbol, [])
        if not prices:
            print(f"No prices for {symbol}")
            return io.BytesIO()  # return empty image buffer

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(prices, marker='o')
        ax.set_title(f"{symbol} Prices")
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        plt.tight_layout()

        if return_image:
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close(fig)
            return buf
        else:
            plt.show()



@app.route("/chart/<symbol>")
def chart_endpoint(symbol):
    if not ws_instance:
        return "WebSocket not initialized", 500

    symbol = symbol.upper()  # e.g., convert 'xrpusdt' to 'XRPUSDT'
    buf = ws_instance.chart(symbol=symbol, return_image=True)
    return Response(buf.getvalue(), mimetype="image/png")



async def main():
    global ws_instance
    ws_instance = WS("wss://stream.binance.com:9443/ws")

    await ws_instance.connect()
    receiver_task = asyncio.create_task(ws_instance.receive_messages())

    await ws_instance.subscribe(["btcusdt@ticker", "ethusdt@ticker"])
    await asyncio.sleep(5)
    await ws_instance.subscribe(["xrpusdt@ticker"])

    # Start Flask in background thread
    threading.Thread(target=lambda: app.run(port=5000), daemon=True).start()

    # Optional: show chart in desktop window
    # ws_instance.chart()

    try:
        await receiver_task
    except asyncio.CancelledError:
        print("Receiver task cancelled. Exiting.")


if __name__ == "__main__":
    asyncio.run(main())
