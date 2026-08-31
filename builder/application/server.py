"""Single-user localhost backend for the BOB application."""

from __future__ import annotations

import json
import os
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .bridge.service import ApplicationBridge, BridgeRequestError


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_REQUEST_BYTES = 4 * 1024 * 1024


class BOBHTTPServer(ThreadingHTTPServer):
    """Threaded localhost server hosting the BOB application bridge."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        server_address: tuple[str, int],
        bridge: ApplicationBridge,
    ) -> None:
        super().__init__(server_address, BOBRequestHandler)
        self.bridge = bridge


class BOBRequestHandler(BaseHTTPRequestHandler):
    """HTTP adapter for the single-user BOB application bridge."""

    server: BOBHTTPServer

    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        """Keep backend output concise and deterministic."""
        print("[BOB]", format % args)

    def _send_json(
        self,
        status: HTTPStatus,
        payload: dict[str, Any],
    ) -> None:
        body = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length")

        if raw_length is None:
            raise BridgeRequestError("Content-Length header is required")

        try:
            length = int(raw_length)
        except ValueError as exc:
            raise BridgeRequestError("Invalid Content-Length") from exc

        if length < 0:
            raise BridgeRequestError("Invalid request length")

        if length > MAX_REQUEST_BYTES:
            raise BridgeRequestError("Request body exceeds maximum size")

        body = self.rfile.read(length)

        if len(body) != length:
            raise BridgeRequestError("Incomplete request body")

        try:
            value = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BridgeRequestError("Request body must be valid JSON") from exc

        if not isinstance(value, dict):
            raise BridgeRequestError("Request body must be a JSON object")

        return value

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(
                HTTPStatus.OK,
                {
                    "success": True,
                    "service": "bob",
                    "status": "healthy",
                    "api_version": "v1",
                },
            )
            return

        self._send_json(
            HTTPStatus.NOT_FOUND,
            {
                "success": False,
                "error": {
                    "type": "NotFound",
                    "message": "Endpoint not found",
                },
            },
        )

    def do_POST(self) -> None:
        if self.path != "/v1/run":
            self._send_json(
                HTTPStatus.NOT_FOUND,
                {
                    "success": False,
                    "error": {
                        "type": "NotFound",
                        "message": "Endpoint not found",
                    },
                },
            )
            return

        try:
            request = self._read_json()
            response = self.server.bridge.run(request)

            status = (
                HTTPStatus.OK
                if response.success
                else HTTPStatus.INTERNAL_SERVER_ERROR
            )

            self._send_json(status, response.to_dict())

        except BridgeRequestError as exc:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {
                    "success": False,
                    "error": {
                        "type": type(exc).__name__,
                        "message": str(exc),
                    },
                },
            )

        except Exception as exc:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {
                    "success": False,
                    "error": {
                        "type": type(exc).__name__,
                        "message": str(exc),
                    },
                },
            )

    def do_HEAD(self) -> None:
        if self.path == "/health":
            body = json.dumps(
                {
                    "success": True,
                    "service": "bob",
                    "status": "healthy",
                },
                separators=(",", ":"),
            ).encode("utf-8")

            self.send_response(HTTPStatus.OK)
            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8",
            )
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return

        self.send_response(HTTPStatus.NOT_FOUND)
        self.send_header("Content-Length", "0")
        self.end_headers()


def create_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    bridge: ApplicationBridge | None = None,
) -> BOBHTTPServer:
    """Create a configured local BOB server without starting it."""
    if host != DEFAULT_HOST:
        raise ValueError(
            "BOB local server must bind to 127.0.0.1"
        )

    if not 1024 <= port <= 65535:
        raise ValueError("port must be between 1024 and 65535")

    return BOBHTTPServer(
        (host, port),
        bridge or ApplicationBridge(),
    )


def serve_forever(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    bridge: ApplicationBridge | None = None,
) -> None:
    """Start the single-user BOB localhost backend."""
    server = create_server(
        host=host,
        port=port,
        bridge=bridge,
    )

    print(
        f"BOB backend listening on http://{host}:{port}"
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBOB backend stopping...")
    finally:
        server.server_close()


def main() -> None:
    """CLI entrypoint for the local backend server."""
    host = os.environ.get(
        "BOB_HOST",
        DEFAULT_HOST,
    )

    port = int(
        os.environ.get(
            "BOB_PORT",
            str(DEFAULT_PORT),
        )
    )

    serve_forever(
        host=host,
        port=port,
    )


if __name__ == "__main__":
    main()
