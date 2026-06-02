"""iFlytek digital human WebSocket service — manages a single avatar session."""
from typing import Optional

import json
import uuid
import time
import queue
import threading
import logging

import websocket

from backend.config import (
    IFLYTEK_APP_ID, IFLYTEK_APP_KEY, IFLYTEK_APP_SECRET,
    IFLYTEK_AVATAR_ID, IFLYTEK_VCN, IFLYTEK_SPEED, IFLYTEK_WS_URL,
)
from backend.utils.iflytek_auth import assemble_auth_url

logger = logging.getLogger(__name__)


class DigitalHumanService:

    def __init__(self):
        self._ws: Optional[websocket.WebSocketApp] = None
        self._thread: Optional[threading.Thread] = None
        self._queue: queue.Queue = queue.Queue(maxsize=256)
        self._running = False
        self._connected = False
        self._avatar_linked = False
        self._stream_url: Optional[str] = None
        self._stream_extend: Optional[dict] = None
        self._sid: Optional[str] = None

    # ---- public API ----

    @property
    def ready(self) -> bool:
        return self._avatar_linked

    def start(self) -> dict:
        if self._running and self._connected and self._avatar_linked:
            return self._build_result()

        self.stop()
        time.sleep(0.3)
        self._running = True

        auth_url = assemble_auth_url(IFLYTEK_WS_URL, "GET", IFLYTEK_APP_KEY, IFLYTEK_APP_SECRET)
        self._ws = websocket.WebSocketApp(
            auth_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self._thread = threading.Thread(target=self._ws.run_forever, daemon=True)
        self._thread.start()

        deadline = time.time() + 15
        while not self._avatar_linked and time.time() < deadline:
            time.sleep(0.3)

        if not self._avatar_linked:
            self.stop()
            raise RuntimeError("数字人启动超时，请检查讯飞配置。")

        return self._build_result()

    def _build_result(self) -> dict:
        url = self._stream_url or ""
        # Parse server from xrtcs://host/roomId
        server_host = ""
        room_id = ""
        if "://" in url:
            rest = url.split("://", 1)[1]
            if "/" in rest:
                server_host, room_id = rest.split("/", 1)
        return {
            "stream_url": url,
            "stream_extend": self._stream_extend,
            "sid": self._sid,
            "server": f"https://{server_host}" if server_host else "",
            "room_id": room_id,
        }

    def send_text(self, text: str):
        if not self._running:
            raise RuntimeError("数字人会话未启动。")
        msg = {
            "header": {
                "app_id": IFLYTEK_APP_ID,
                "request_id": str(uuid.uuid4()),
                "ctrl": "text_driver",
            },
            "parameter": {
                "tts": {"vcn": IFLYTEK_VCN, "speed": IFLYTEK_SPEED},
                "avatar_dispatch": {"interactive_mode": 0},
            },
            "payload": {
                "text": {"content": text},
            },
        }
        try:
            self._queue.put_nowait(json.dumps(msg))
        except queue.Full:
            logger.warning("Digital human queue full, dropping message.")

    def stop(self):
        self._running = False
        self._avatar_linked = False
        self._stream_url = None
        self._stream_extend = None
        self._sid = None
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    # ---- WebSocket callbacks ----

    def _on_open(self, ws):
        self._connected = True
        start_msg = {
            "header": {
                "app_id": IFLYTEK_APP_ID,
                "request_id": str(uuid.uuid4()),
                "ctrl": "start",
            },
            "parameter": {
                "tts": {"vcn": IFLYTEK_VCN, "speed": IFLYTEK_SPEED},
                "avatar": {
                    "stream": {"protocol": "xrtc", "alpha": 1},
                    "avatar_id": IFLYTEK_AVATAR_ID,
                },
            },
        }
        ws.send(json.dumps(start_msg))
        logger.info("Digital human start command sent.")
        threading.Thread(target=self._sender_loop, daemon=True).start()

    def _sender_loop(self):
        while self._running and self._connected:
            try:
                msg = self._queue.get(timeout=5)
                if self._ws:
                    self._ws.send(msg)
            except queue.Empty:
                if self._running and self._avatar_linked and self._ws:
                    ping = json.dumps({
                        "header": {
                            "app_id": IFLYTEK_APP_ID,
                            "request_id": str(uuid.uuid4()),
                            "ctrl": "ping",
                        },
                    })
                    try:
                        self._ws.send(ping)
                    except Exception:
                        break

    def _on_message(self, ws, raw_message):
        try:
            data = json.loads(raw_message)
            code = data.get("header", {}).get("code", -1)
            if code != 0:
                logger.error(f"Digital human error: {raw_message}")
                return

            self._sid = data.get("header", {}).get("sid", self._sid)

            payload = data.get("payload", {})
            avatar = payload.get("avatar", {})

            if avatar.get("event_type") == "stream_info":
                self._avatar_linked = True
                self._stream_url = avatar.get("stream_url", "")
                self._stream_extend = avatar.get("stream_extend")
                logger.info(f"Digital human stream ready: {self._stream_url}")
        except Exception as e:
            logger.error(f"Error parsing message: {e}")

    def _on_error(self, ws, error):
        logger.error(f"Digital human WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        self._connected = False
        self._avatar_linked = False
        logger.info(f"Digital human WebSocket closed: {close_status_code}")


# Singleton
_dh_service: Optional[DigitalHumanService] = None


def get_dh_service() -> DigitalHumanService:
    global _dh_service
    if _dh_service is None:
        _dh_service = DigitalHumanService()
    return _dh_service
