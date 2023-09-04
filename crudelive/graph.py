import json
from datetime import datetime, time
from pytz import timezone
from time import sleep
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from alice_blue import AliceBlue
from pya3 import *
# Replace with your API credentials
user_id = 'AB093838'
api_key = 'cy5uYssgegMaUOoyWy0VGLBA6FsmbxYd0jNkajvBVJuEV9McAM3o0o2yG6Z4fEFYUGtTggJYGu5lgK89HumH3nBLbxsLjgplbodFHDLYeXX0jGQ5CUuGtDvYKSEzWSMk'

# Define market open and close times
market_open_time = time(9, 15)  # Adjust the time according to your market's opening time
market_close_time = time(15, 30)  # Adjust the time according to your market's closing time

# Set up AliceBlue API connection
alice = Aliceblue(user_id='AB093838', api_key='cy5uYssgegMaUOoyWy0VGLBA6FsmbxYd0jNkajvBVJuEV9McAM3o0o2yG6Z4fEFYUGtTggJYGu5lgK89HumH3nBLbxsLjgplbodFHDLYeXX0jGQ5CUuGtDvYKSEzWSMk')

# Create empty lists to store x and y values
timestamps = []
prices = []

# Create a figure and axis for the live graph
fig, ax = plt.subplots()

def update_graph(price):
    timestamp = datetime.now(timezone('Asia/Kolkata'))
    timestamps.append(timestamp)
    prices.append(price)

    # Remove outdated data points
    cutoff_time = timestamp - pd.Timedelta(seconds=60)  # Keep data of the last 60 seconds
    while timestamps[0] < cutoff_time:
        timestamps.pop(0)
        prices.pop(0)

    # Clear the previous plot
    ax.clear()

    # Determine the color based on price movement
    colors = ['green' if p > prices[i-1] else 'red' for i, p in enumerate(prices[1:], start=1)]

    # Plot the updated data with color
    ax.plot(timestamps[1:], prices[1:], color=colors)
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.set_title('Live Data')

    # Adjust the plot layout
    plt.gcf().autofmt_xdate()
    plt.tight_layout()

# Set up WebSocket callbacks
def socket_open_callback():
    print("WebSocket opened")
    subscribe_list = [alice.get_instrument_by_symbol('NSE', 'TATAMOTORS')]
    alice.subscribe(subscribe_list)

def socket_close_callback():
    print("WebSocket closed")

def socket_error_callback(error):
    print("WebSocket error:", error)

def feed_data_callback(message):
    feed_message = json.loads(message)
    if feed_message["type"] == "ltp":
        timestamp = datetime.now(timezone('Asia/Kolkata'))
        price = feed_message["ltp"]
        update_graph(price)

# Connect to AliceBlue WebSocket
alice.start_websocket(socket_open_callback, socket_close_callback, socket_error_callback, feed_data_callback)

# Run the WebSocket connection and data retrieval until market close
while True:
    current_time = datetime.now().time()
    if current_time >= market_close_time:
        break

    # Update the live graph every 1 second
    plt.pause(1)

# Save the final graph locally
plt.savefig('market_data_graph.png')
plt.show()
