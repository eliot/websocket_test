import urllib3
import json
import asyncio

from os import getenv

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

# Ameritrade API key
API_KEY = getenv('API_KEY')

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Stonks</title>
    </head>
    <body>
        <h1>AAPL Price</h1>
        <h1 id="price">0.00</h1>
        <!--<form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>-->
        <script>
            var ws = new WebSocket("ws://localhost:7000/price");
            ws.onmessage = function(event) {
                var price = document.getElementById('price')
                //var message = document.createElement('li')
                //var content = document.createTextNode(event.data)
                //message.appendChild(content)
                //messages.appendChild(message)
                price.innerText = event.data;
                console.log("Message received", event.data);
            };
            //function sendMessage(event) {
            //    var input = document.getElementById("messageText")
            //    ws.send(input.value)
            //    input.value = ''
            //    event.preventDefault()
            //}
        </script>
    </body>
</html>
"""

http = urllib3.PoolManager()

prices = {}

def quote(ticker='AAPL', apikey=API_KEY):
    url = f"https://api.tdameritrade.com/v1/marketdata/{ticker}/quotes?apikey={apikey}"
    response = http.request('GET', url)
    if response.status != 200:
        return None
    data = json.loads(response.data)
    #['Meta Data', 'Time Series (1min)']
    #  data['Time Series (1min)']['2021-02-16 20:00:00']
    return data[ticker]['lastPrice']


def update_price(ticker):
    '''Update the price of a symbol in the `prices` dict'''
    price = quote(ticker=ticker)
    prices[ticker] = price

def get_price(ticker):
    '''Get price from `prices` dict'''
    return prices[ticker]



async def update_price_tick(timeout=5000):
    while True:
        update_price('AAPL')
        price = get_price('AAPL')
        print(f'price updated, price={price}')
        await asyncio.sleep(timeout)


async def get_price_tick(timeout=5000):
    while True:
        await asyncio.sleep(timeout)
        update_price('AAPL')
        price = get_price('AAPL')
        print('got price')
        return price

@app.get("/")
async def get():
    return HTMLResponse(html)

        
@app.websocket("/price")
async def websocket_aaplprice(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await get_price_tick()
        await websocket.send_text(f"{data}")


# loop = asyncio.get_running_loop()
# task = loop.create_task(update_price_tick())

# try:
#     loop.run_until_complete(task)
# except asyncio.CancelledError:
#     print('asyncio.CancelledError')