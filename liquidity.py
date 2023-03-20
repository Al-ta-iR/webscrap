import requests

url = "https://api.binance.com/api/v3/depth"

params = {
    "symbol": "BTCUSDT",
    "limit": 100
}

response = requests.get(url, params=params)

order_book = response.json()
buy_volume = sum([float(order[1]) for order in order_book["bids"] if float(order[0]) >= 50000])
