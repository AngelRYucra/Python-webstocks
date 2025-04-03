import asyncio
import websockets
import json
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import functools
matplotlib.use('TkAgg')

class WS:
    def __init__(self, hostname):
        self.hostname = hostname
        self.ws = None
        self.prices = {}
        self.symbol_to_plot = "BTCUSDT"

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
        #print(data)
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
            print("Prices: ",prices)
    
    def chart(self):
        fig, ax = plt.subplots(figsize=(8, 5))

        symbol_to_plot = "BTCUSDT"

        def update(frame):
            ax.clear()

            if symbol_to_plot in self.prices and len(self.prices[symbol_to_plot]) > 0:
                ax.plot(self.prices[symbol_to_plot], marker="o", linestyle="-")
                ax.set_title(f"Last 10 Prices for {symbol_to_plot}")
                ax.legend(["Price"])
                ax.set_xticks(range(len(self.prices[symbol_to_plot])))

        ani = animation.FuncAnimation(fig, update, interval=1000)
        plt.show()
    
async def main():
    ws = WS("wss://stream.binance.com:9443/ws")

    # 1) Connect (but don't block on receive_messages yet)
    await ws.connect()

    # 2) Start the receive_messages() loop as a background task
    #    so we don't block in main().
    receiver_task = asyncio.create_task(ws.receive_messages())

    # 3) Subscribe to some streams
    await ws.subscribe(["btcusdt@ticker", "ethusdt@ticker"])

    # 4) Simulate waiting or doing something else in the main function
    await asyncio.sleep(5)

    # 5) Subscribe to additional streams AFTER we've already
    #    started receiving messages
    await ws.subscribe(["xrpusdt@ticker"])

    # 6) Let the program run a bit longer to see more messages
    await asyncio.sleep(1)
    ws.chart()
    # 7) If you eventually need to cancel the receiver loop:
    #receiver_task.cancel()
    try:
        await receiver_task
    except asyncio.CancelledError:
        print("Receiver task cancelled. Exiting.")


if __name__ == "__main__":
    asyncio.run(main())
