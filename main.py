import datetime
import random
import select
import sys
import time
from queue import Queue
import socket
import matplotlib.pyplot as plt
import mysql.connector
from sshtunnel import SSHTunnelForwarder

from config import connection_info

# initialize SSH tunneling
SSH_TIMEOUT = 3
socket.setdefaulttimeout(SSH_TIMEOUT)
db_config = connection_info
ssh_config = connection_info.get('ssh_config')
remote_address = (db_config.get('host'), db_config.get('port'))
INTERVAL: float = 0.5


# function to check the database connection availability


def check_availability(ssh_tunnel: SSHTunnelForwarder = None):
    if ssh_tunnel:
        try:
            cnx = mysql.connector.connect(user=db_config.get('username'), password=db_config.get('password'),
                                          host='127.0.0.1', port=ssh_tunnel.local_bind_port,
                                          database=db_config.get('database'), connect_timeout=1)
            cursor = cnx.cursor()

            # execute a simple query to check availability
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            cnx.close()
            return 1
        except Exception as e:
            print(e, datetime.datetime.now())
            return 0
    try:
        conn = mysql.connector.connect(**db_config)
        conn.close()
        return 1
    except:
        return 0


# list to store connection availability and timestamps
availabilities = []
timestamps = []

# list to store events
event_queue = Queue()

# create initial plot
plt.figure()
plt.xlabel("Time")
plt.ylabel("Availability")
plt.title("Database Connection Availability")
plt.show(block=False)


def main_loop(ssh_server: SSHTunnelForwarder = None, interval: float = 0.5):
    while True:
        # check connection availability and add to list
        availabilities.append(check_availability(ssh_server))
        # add current timestamp to list
        current_timestamp = datetime.datetime.now()
        timestamps.append(current_timestamp)
        # plot availability graph
        plt.plot(timestamps, availabilities)
        # plot events as vertical lines
        if event_queue.qsize() != 0:
            event = event_queue.get()
            plt.axvline(x=event['timestamp'], color=event['color'], linestyle='--', label=event['name'])
            plt.gca().legend().remove()
            plt.legend()
        plt.draw()
        plt.pause(0.001)
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            event_name = input("Enter event name (leave blank to skip): ")
            if event_name:
                event_queue.put({'name': event_name, 'timestamp': current_timestamp, 'color': random.choice(
                    ['red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'black'])})
        # wait for 5 second before checking again
        time.sleep(interval)


if ssh_config:
    with SSHTunnelForwarder(
            (ssh_config.get('host'), 22),
            ssh_username=ssh_config.get('username'),
            ssh_pkey=ssh_config.get('ssh_key'),
            remote_bind_address=remote_address) as ssh_server:
        main_loop(ssh_server, INTERVAL)
else:
    main_loop(INTERVAL)
