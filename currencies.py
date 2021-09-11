import requests


class CryptoClient(object):
    def get_btc_prices(self):
        """
        Return a list of BTC/USD prices of 24 prices for the last 24 hours
        """
        base_url = "https://api.gemini.com/v2"
        response = requests.get(base_url + "/ticker/btcusd")
        btc_data = response.json()
        changes = btc_data.get("changes")
        prices = [float(change) for change in changes]
        return prices
