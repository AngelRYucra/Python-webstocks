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
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
import threading

# Listas para almacenar los datos
prices_btc = []
times_btc = []

prices_bnb = []
times_bnb = []

fig, ax = plt.subplots()
line_btc, = ax.plot([], [], 'b-', label="BTC/USDT")
line_bnb, = ax.plot([], [], 'g-', label="BNB/USDT")

ax.set_xlabel("Time")
ax.set_ylabel("Price (USDT)")
ax.set_title("Live BTC/USDT Price from Binance")
ax.legend()
ax.grid()

ax.set_xlim(0, 10)  # Máximo 50 datos visibles
ax.set_ylim(0, 85000)  # Rango inicial estimado

async def listen_btcusdt_trades():
    websocket_url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
    
    async with websockets.connect(websocket_url) as ws:
        print("Connected to Binance BTC/USDT trade stream")
        while True:
            try:
                message = await ws.recv()
                data = json.loads(message)
                trade_price = float(data['p'])
                trade_time = datetime.now().strftime('%H:%M:%S')
                
                if len(prices_btc) >= 10:
                    prices_btc.pop(0)
                    times_btc.pop(0)

                prices_btc.append(trade_price)
                times_btc.append(trade_time)
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

async def listen_bnbusdt_trades():
    websocket_url = "wss://stream.binance.com:9443/ws/bnbusdt@trade"
    
    async with websockets.connect(websocket_url) as ws:
        print("Connected to Binance BNB/USDT trade stream")
        while True:
            try:
                message = await ws.recv()
                data = json.loads(message)
                trade_price = float(data['p'])
                trade_time = datetime.now().strftime('%H:%M:%S')
                
                # Agregar datos a las listas
                if len(prices_bnb) >= 50:  # Mantener solo los últimos 50 datos
                    prices_bnb.pop(0)
                    times_bnb.pop(0)

                prices_bnb.append(trade_price)
                times_bnb.append(trade_time)
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

def update_plot(frame):
    if prices_btc and times_btc:
        line_btc.set_data(range(len(times_btc)), prices_btc)
        line_bnb.set_data(range(len(times_bnb)), prices_bnb)
        # ax.set_xlim(0, len(times))  # Ajustar eje X dinámicamente
        # ax.set_ylim(min(prices) * 0.99, max(prices) * 1.01)  # Ajustar eje Y dinámicamente
        return line_btc, line_bnb

def start_websocket_btc():
    asyncio.run(listen_btcusdt_trades())  # Ejecutar WebSocket en un hilo separado

def start_websocket_bnb():
    asyncio.run(listen_bnbusdt_trades())

if __name__ == "__main__":
    # Iniciar WebSocket en un hilo separado
    websocket_thread1 = threading.Thread(target=start_websocket_btc, daemon=True)
    websocket_thread1.start()
    websocket_thread2 = threading.Thread(target=start_websocket_bnb, daemon=True)
    websocket_thread2.start()
    ani1 = animation.FuncAnimation(fig, update_plot, interval=1000)
    plt.tight_layout()
    plt.show()
