# import asyncio
# import websockets
# import json

# latest_data_btc = {"price": "Loading...", "quantity": "Loading..."}
# latest_data_bnb = {"price": "Loading...", "quantity": "Loading..."}

# async def listen_btcusdt_trades():
#     websocket_url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
    
#     async with websockets.connect(websocket_url) as ws:
#         print("Connected to Binance BTC/USDT trade stream")
#         while True:
#             try:
#                 message = await ws.recv()
#                 data = json.loads(message)
#                 latest_data_btc["price"] = data['p']
#                 latest_data_btc["quantity"] = data['q']
#             except websockets.exceptions.ConnectionClosed:
#                 print("Connection closed")
#                 break
# async def listen_bnbusdt_trades():
#     websocket_url = "wss://stream.binance.com:9443/ws/btcusdt@trade"

#     async with websockets.connect(websocket_url) as ws:
#         print("Connected to BNB BNB/USDT trade stream")
#         while True:
#             try:
#                 message = await ws.recv()
#                 data = json.loads(message)
#                 latest_data_bnb["price"] = data['p']
#                 latest_data_bnb["quantity"] = data['q']
#             except websockets.exceptions.ConnectionClosed:
#                 print("Connection closed")
#                 break
# # BTC
# def start_websocket_btc():
#     loop1 = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop1)
#     loop1.run_until_complete(listen_btcusdt_trades())
# #BNB
# def start_websocket_bnb():
#     loop2 = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop2)
#     loop2.run_until_complete(listen_bnbusdt_trades())

import asyncio
import websockets
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime
import threading
from flask import Flask, jsonify, send_file
import io
import matplotlib.ticker as mticker


# Listas para almacenar los datos
prices_btc, times_btc = [], []
prices_bnb, times_bnb = [], []

app = Flask(__name__)

@app.route('/hola', methods=['GET'])
def hola():
    return "Mensaje de prueba", 200

@app.route('/last_values', methods=['GET'])
def last_values():
    return jsonify({
        "BTC": list(zip(times_btc[-100:], prices_btc[-100:])) if len(prices_btc) >= 100 else list(zip(times_btc, prices_btc)),
        "BNB": list(zip(times_bnb[-100:], prices_bnb[-100:])) if len(prices_bnb) >= 100 else list(zip(times_bnb, prices_bnb))
    })

@app.route('/create_image', methods=['GET'])
def create_image():
    data = last_values().json

    if not data["BTC"] or not data["BNB"]:
        return "No hay datos suficientes", 500

    times_btc, prices_btc = zip(*data["BTC"])
    times_bnb, prices_bnb = zip(*data["BNB"])

    plt.figure(figsize=(8, 5))
    plt.plot(times_btc, prices_btc, marker='o', linestyle='-', color='blue', label="BTC")
    plt.plot(times_bnb, prices_bnb, marker='s', linestyle='-', color='green', label="BNB")

    plt.xlabel("Tiempo")
    plt.ylabel("Precio")
    plt.title("Últimos 10 valores de BTC y BNB")
    plt.legend()
    plt.xticks(rotation=45)

    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    plt.close()
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

@app.route('/create_image/btc', methods=['GET'])
def image_btc():
    data = last_values().json
    if not data["BTC"]:
        return "No data in BTC"
    print(data)
    times_btc, prices_btc = zip(*data["BTC"])
    print("PRICES")
    print(prices_btc)
    print("TIMES")
    print(times_btc)

    plt.figure(figsize=(8, 5))
    plt.plot(times_btc, prices_btc, marker='o', linestyle='-', color='blue', label="BTC")
    plt.xlabel("Tiempo")
    plt.ylabel("Precio")
    plt.title("Últimos 10 valores de BTC")
    plt.legend()
    plt.xticks(rotation=45)

    plt.gca().yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.2f}"))

    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    plt.close()
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

@app.route('/create_image/bnb', methods=['GET'])
def image_bnb():
    data = last_values().json
    if not data["BTC"]:
        return "No data in BNB"
    print(data)
    times_btc, prices_btc = zip(*data["BNB"])
    print("PRICES")
    print(prices_btc)
    print("TIMES")
    print(times_btc)

    plt.figure(figsize=(8, 5))
    plt.plot(times_bnb, prices_btc, marker='o', linestyle='-', color='blue', label="BNB")
    plt.xlabel("Tiempo")
    plt.ylabel("Precio")
    plt.title("Últimos 10 valores de BNB")
    plt.legend()
    plt.xticks(rotation=45)

    plt.gca().yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.2f}"))

    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    plt.close()
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

async def listen_trades(symbol, prices, times):
    websocket_url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
    
    async with websockets.connect(websocket_url) as ws:
        print(f"Connected to Binance {symbol.upper()} trade stream")
        while True:
            try:
                message = await ws.recv()
                data = json.loads(message)
                trade_price = float(data['p'])
                trade_time = float(data['E'])

                if len(prices) >= 100:
                    prices.pop(0)
                    times.pop(0)

                prices.append(trade_price)
                times.append(trade_time)
            except websockets.exceptions.ConnectionClosed:
                print(f"Connection closed for {symbol.upper()}")
                break

def start_websocket(symbol, prices, times):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen_trades(symbol, prices, times))

if __name__ == "__main__":
    threading.Thread(target=start_websocket, args=("btcusdt", prices_btc, times_btc), daemon=True).start()
    threading.Thread(target=start_websocket, args=("bnbusdt", prices_bnb, times_bnb), daemon=True).start()
    app.run(debug=True, use_reloader=True)
