import json
from datetime import datetime
from pytz import timezone
from time import sleep
import pandas as pd
from alice_blue import AliceBlue

from pya3 import *

alice = Aliceblue(user_id='AB093838', api_key='cy5uYssgegMaUOoyWy0VGLBA6FsmbxYd0jNkajvBVJuEV9McAM3o0o2yG6Z4fEFYUGtTggJYGu5lgK89HumH3nBLbxsLjgplbodFHDLYeXX0jGQ5CUuGtDvYKSEzWSMk')

print(alice.get_session_id())  # Get Session ID

LTP = 0
socket_opened = False
subscribe_flag = False
subscribe_list = []
unsubscribe_list = []
data_list = []  # List to store the received data
df = pd.DataFrame()  # Initialize an empty DataFrame for storing the data


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


# Connect to AliceBlue


# Socket Connection Request
alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                      socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True,
                      market_depth=False)

while not socket_opened:
    pass

# Subscribe to Tata Motors
subscribe_list = [alice.get_instrument_by_token('NSE', 2885)]
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
        df.to_excel('reliance.xlsx', index=False)

    # Stop the WebSocket after a certain condition or keep running