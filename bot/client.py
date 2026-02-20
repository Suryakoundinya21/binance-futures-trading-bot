"""Binance Futures Testnet REST client."""
from __future__ import annotations
import certifi, hashlib, hmac, logging, time
from typing import Any, Dict, Optional
from urllib.parse import urlencode
import requests

logger = logging.getLogger("trading_bot.client")
TESTNET_BASE_URL = "https://testnet.binancefuture.com"
FUTURES_ORDER_ENDPOINT = "/fapi/v1/order"
EXCHANGE_INFO_ENDPOINT = "/fapi/v1/exchangeInfo"
ACCOUNT_ENDPOINT = "/fapi/v2/account"

class BinanceAPIError(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"Binance API Error {code}: {msg}")

class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str = TESTNET_BASE_URL):
        self.api_key    = api_key
        self.api_secret = api_secret
        self.base_url   = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = certifi.where()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _get(self, endpoint: str, params: Optional[Dict] = None, signed: bool = False):
        params = params or {}
        if signed:
            params["timestamp"] = self._timestamp()
            params = self._sign(params)
        url = self.base_url + endpoint
        logger.info("GET %s | params: %s", url, {k: v for k, v in params.items() if k != "signature"})
        try:
            resp = self.session.get(url, params=params, timeout=10)
        except requests.exceptions.SSLError as exc:
            logger.error("SSL error: %s", exc)
            raise ConnectionError("SSL verification failed.") from exc
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error: %s", exc)
            raise ConnectionError(f"Cannot reach Binance API: {exc}") from exc
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out.")
        return self._handle_response(resp)

    def _post(self, endpoint: str, params: Dict[str, Any], signed: bool = True):
        params["timestamp"] = self._timestamp()
        if signed:
            params = self._sign(params)
        url = self.base_url + endpoint
        logger.info("POST %s | body: %s", url, {k: v for k, v in params.items() if k != "signature"})
        try:
            resp = self.session.post(url, data=params, timeout=10)
        except requests.exceptions.SSLError as exc:
            logger.error("SSL error: %s", exc)
            raise ConnectionError("SSL verification failed.") from exc
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error: %s", exc)
            raise ConnectionError(f"Cannot reach Binance API: {exc}") from exc
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out.")
        return self._handle_response(resp)

    @staticmethod
    def _handle_response(resp: requests.Response) -> Dict:
        logger.info("Response %s: %s", resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except ValueError:
            resp.raise_for_status()
            return {}
        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceAPIError(data["code"], data.get("msg", "Unknown error"))
        if not resp.ok:
            raise BinanceAPIError(resp.status_code, str(data))
        return data

    def get_exchange_info(self) -> Dict:
        return self._get(EXCHANGE_INFO_ENDPOINT)

    def get_account(self) -> Dict:
        return self._get(ACCOUNT_ENDPOINT, signed=True)

    def place_order(self, symbol: str, side: str, order_type: str, quantity: str,
                    price: Optional[str] = None, stop_price: Optional[str] = None,
                    time_in_force: str = "GTC") -> Dict:
        params: Dict[str, Any] = {
            "symbol": symbol, "side": side, "type": order_type, "quantity": quantity,
        }
        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = time_in_force
        if order_type == "STOP_MARKET":
            params["stopPrice"] = stop_price
        return self._post(FUTURES_ORDER_ENDPOINT, params)
