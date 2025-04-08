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
from flask import Flask, Response, jsonify
from collections import defaultdict

matplotlib.use('Agg')
loop = asyncio.new_event_loop()

# Flask app
app = Flask(__name__)
ws_instance = None 


class WS:
    def __init__(self, hostname):
        self.hostname = hostname
        self.ws = None
        self.prices = defaultdict(list)
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
            return True
        except Exception as e:
            print(f"Error sending subscription: {e}")
        return False

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
        if 's' in data and 'c' in data:
            symbol = data['s'].upper()
            price = float(data['c'])
            print(f"Received message: {symbol} Price: {price}")


    def store_values(self, data):
        symbol = data.get('s')
        if symbol:
            if symbol not in self.prices:
                self.prices[symbol] = []
                print(f"New symbol added: {symbol}")
            # Append the latest price
            prices = self.prices[symbol]
            prices.append(float(data['c']))
            
            if len(prices) > 1000:
                prices.pop(0)

            print(f"Updated Prices for {symbol}: {prices}")

    def chart(self, symbol=None, return_image=False):
        if symbol is None:
            symbol = self.symbol

        prices = self.prices.get(symbol, [])
        if not prices:
            print(f"No prices for {symbol}")
            return io.BytesIO()

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

    symbol = symbol.upper()
    buf = ws_instance.chart(symbol=symbol, return_image=True)
    return Response(buf.getvalue(), mimetype="image/png")

@app.route("/subcribed")
def subscribed():
    suscritos = list(ws_instance.prices.keys())
    return jsonify(suscritos)

@app.route("/subscribe/<symbol>")
async def subscribe(symbol):
    #the currency need to be in lowercaser
    if symbol.upper() + "USDT" in ws_instance.prices:
        return jsonify({"message": f"Already Subscribed to {symbol}"})

    symbol = symbol + "usdt@ticker"

    subcribed = await ws_instance.subscribe([symbol])

    if subcribed:
        return jsonify({"message": f"Subscribed successfully to {symbol}"})
    else:
        return jsonify({"message": f"Not Subscribed to {symbol}"})

@app.route("/values")
def values():
    value_currency = ws_instance.store_values()
    return value_currency

async def main():
    global ws_instance
    global loop
    # Start Flask in background thread
    threading.Thread(target=lambda: app.run(port=5000), daemon=True).start()

    ws_instance = WS("wss://stream.binance.com:9443/ws")
    asyncio.set_event_loop(loop)
    await ws_instance.connect()
    receiver_task = asyncio.create_task(ws_instance.receive_messages())

    await ws_instance.subscribe(["btcusdt@ticker", "ethusdt@ticker"])
    await asyncio.sleep(5)

    try:
        await receiver_task
    except asyncio.CancelledError:
        print("Receiver task cancelled. Exiting.")


if __name__ == "__main__":
    asyncio.run(main())
