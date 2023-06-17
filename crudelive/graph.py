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

# Create empty lists to store x and y values
timestamps = []
prices = []

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
    plt.clf()

    # Determine the color based on price movement
    colors = ['green' if p > prices[i-1] else 'red' for i, p in enumerate(prices[1:], start=1)]

    # Plot the updated data with color
    plt.plot(timestamps[1:], prices[1:], color=colors)
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('Live Data')

    # Adjust the plot layout
    plt.gcf().autofmt_xdate()
    plt.tight_layout()

    # Display the updated plot
    plt.pause(0.01)

# Set up AliceBlue API connection
alice = Aliceblue(user_id='AB093838', api_key='cy5uYssgegMaUOoyWy0VGLBA6FsmbxYd0jNkajvBVJuEV9McAM3o0o2yG6Z4fEFYUGtTggJYGu5lgK89HumH3nBLbxsLjgplbodFHDLYeXX0jGQ5CUuGtDvYKSEzWSMk')

LTP = 0
socket_opened = False
subscribe_flag = False
subscribe_list = []
unsubscribe_list = []
data_list = []  # List to store the received data
df = pd.DataFrame()  # Initialize an empty DataFrame for storing the data

# Create empty lists to store x and y values
timestamps = []
prices = []

def socket_open():
    print("Connected")
    global socket_opened
    socket_opened = True
    if subscribe_flag:
        alice.subscribe(subscribe_list)

def socket_close():
    global socket_opened, LTP
    socket_opened = False
    LTP = 0
    print("Closed")

def socket_error(message):
    global LTP
    LTP = 0
    print("Error:", message)

def feed_data(message):
    global LTP, subscribe_flag, data_list
    feed_message = json.loads(message)
    if feed_message["t"] == "ck":
        print("Connection Acknowledgement status: %s (Websocket Connected)" % feed_message["s"])
        subscribe_flag = True
        print("subscribe_flag:", subscribe_flag)
        print("-------------------------------------------------------------------------------")
        pass
    elif feed_message["t"] == "tk":
        print("Token Acknowledgement status: %s" % feed_message)
        print("-------------------------------------------------------------------------------")
        pass
    else:
        print("Feed:", feed_message)
        timestamp = datetime.now(timezone('Asia/Kolkata'))
        feed_message['timestamp'] = timestamp.strftime('%Y-%m-%d %H:%M:%S %Z%z')
        LTP = feed_message['lp'] if 'lp' in feed_message else LTP
        data_list.append(feed_message)  # Append the received data to the list
        update_graph(feed_message['lp'])  # Update the graph with the new data

# Connect to AliceBlue
alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                      socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True,
                      market_depth=False)

while not socket_opened:
    pass

# Subscribe to Tata Motors
subscribe_list = [alice.get_instrument_by_token('NSE', 3426)]
alice.subscribe(subscribe_list)
print(datetime.now())
sleep(10)
print(datetime.now())

# Run the WebSocket connection and data retrieval indefinitely
while True:
    # Wait for 1 second
    sleep(1)

    # Check if there is new data
    if len(data_list) > 0:
        # Convert the received data list to a DataFrame
        new_df = pd.DataFrame(data_list)

        # Append the new data to the existing DataFrame
        df = df.append(new_df, ignore_index=True)

        data_list = []  # Clear the data list

        # Save the DataFrame to an Excel file
        df.to_excel('TATAMOTORSLIVEGRAPHDATA.xlsx', index=False)

    # Stop the WebSocket after the market close time
    current_time = datetime.now().time()
    if current_time >= market_close_time:
        break

# Save the final graph locally
plt.savefig('market_data_graph.png')
plt.show()
