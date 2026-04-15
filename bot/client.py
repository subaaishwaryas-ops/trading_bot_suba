import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

logger = setup_logger("client")

BASE_URL = "https://testnet.binancefuture.com"
RECV_WINDOW = 5000


class BinanceClientError(Exception):
    """Raised on Binance API errors."""

    def __init__(self, message: str, code: Optional[int] = None, status_code: Optional[int] = None):
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError("API key and secret must not be empty.")
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })
        logger.debug("BinanceClient initialised (testnet=%s)", BASE_URL)

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _sign(self, params: Dict[str, Any]) -> str:
        query = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _get(self, path: str, params: Optional[Dict] = None, signed: bool = False) -> Dict:
        params = params or {}
        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params["recvWindow"] = RECV_WINDOW
            params["signature"] = self._sign(params)

        url = BASE_URL + path
        logger.debug("GET %s | params=%s", url, {k: v for k, v in params.items() if k != "signature"})
        try:
            resp = self.session.get(url, params=params, timeout=10)
        except requests.exceptions.RequestException as exc:
            logger.error("Network error on GET %s: %s", url, exc)
            raise BinanceClientError(f"Network error: {exc}") from exc

        return self._handle_response(resp)

    def _post(self, path: str, params: Dict[str, Any]) -> Dict:
        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = RECV_WINDOW
        params["signature"] = self._sign(params)

        url = BASE_URL + path
        logger.debug("POST %s | params=%s", url, {k: v for k, v in params.items() if k != "signature"})
        try:
            resp = self.session.post(url, data=params, timeout=10)
        except requests.exceptions.RequestException as exc:
            logger.error("Network error on POST %s: %s", url, exc)
            raise BinanceClientError(f"Network error: {exc}") from exc

        return self._handle_response(resp)

    def _handle_response(self, resp: requests.Response) -> Dict:
        logger.debug("Response %s: %s", resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except ValueError:
            raise BinanceClientError(
                f"Non-JSON response (HTTP {resp.status_code}): {resp.text[:200]}",
                status_code=resp.status_code,
            )

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            # Binance error envelope: {"code": -1121, "msg": "..."}
            code = data.get("code")
            msg = data.get("msg", "Unknown error")
            logger.error("Binance API error %s: %s", code, msg)
            raise BinanceClientError(msg, code=code, status_code=resp.status_code)

        if not resp.ok:
            raise BinanceClientError(
                f"HTTP {resp.status_code}: {resp.text[:200]}",
                status_code=resp.status_code,
            )

        return data

    # ------------------------------------------------------------------ #
    #  Public methods                                                      #
    # ------------------------------------------------------------------ #

    def get_server_time(self) -> int:
        data = self._get("/fapi/v1/time")
        return data["serverTime"]

    def get_account_info(self) -> Dict:
        return self._get("/fapi/v2/account", signed=True)

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: Optional[str] = None,
        stop_price: Optional[str] = None,
        time_in_force: str = "GTC",
    ) -> Dict:
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            if not price:
                raise BinanceClientError("Price required for LIMIT order.")
            params["price"] = price
            params["timeInForce"] = time_in_force

        if order_type == "STOP_MARKET":
            if not stop_price:
                raise BinanceClientError("stopPrice required for STOP_MARKET order.")
            params["stopPrice"] = stop_price

        logger.info(
            "Placing %s %s order | symbol=%s qty=%s price=%s",
            side, order_type, symbol, quantity, price or stop_price or "N/A",
        )
        response = self._post("/fapi/v1/order", params)
        logger.info("Order placed successfully | orderId=%s status=%s", response.get("orderId"), response.get("status"))
        return response
