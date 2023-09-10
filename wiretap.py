import logging
import sys
import requests
import json
import asyncio
import websockets
import signal

from event import Event

def setup_logging():
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('Welcome to wiretap')
    logging.info('I monitor the websockets at the IPs you provide and write the data to log files')
    logging.info('Press Ctrl+C to exit')

def get_websocket_url(addr):
    """
    Sends a request to register with the websocket. Returns the websocket url
    """
    try:
        r = requests.get(f'http://{addr}:3012/register')
    except Exception as e:
        logging.error(f"The Iris server at {addr} didn't respond. Is it running? Do you have the right IP?")
        logging.error(e)
        sys.exit(1)

    assert r.status_code == 200
    url = json.loads(r.text)['url']
    logging.info(f"Registered with {addr} and got websocket url: `{url}`")
    return url


async def on_message(message):
    """
    Incoming websocket messages are sent here
    """
    event = Event(message)
    if event.should_be_logged():
        event.write_to_file()
    else:
        logging.warning(f"Received an event that we don't want to keep: {event.response_type} with message {event.message}")

async def watch_iris_server(url):
    """
    Connects to the websocket and loops indefinitely, saving the output
    to a file
    """
    async with websockets.connect(url, ping_interval=None) as websocket:
        logging.info('Connected to iris server')
        while True:
            await on_message(await websocket.recv())

def signal_handler(sign, frame):
    print()
    logging.info("Ctrl+C pressed. Exiting...")
    sys.exit(0)

async def main():
    setup_logging()

    signal.signal(signal.SIGINT, signal_handler)

    if len(sys.argv) < 2:
        print('Usage: python wiretap.py [RTU ip addresses..]')
        sys.exit(1)

    urls = [get_websocket_url(ip) for ip in sys.argv[1:]]

    tasks = [watch_iris_server(url) for url in urls]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
