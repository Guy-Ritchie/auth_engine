"""Minimal HTTP server for the auth_engine application.

This module wires together the router and request handler using only
stdlib's ``http.server``. It is intentionally thin - its sole job is
to start listening and delegate every request to the router.

Usage::

    uv run python -m auth_engine.web.server

Phase 0 behaviour:
    - GET  /          → redirects to /login
    - GET  /login     → serves login.html
    - POST /login     → echoes back a 200 (auth logic added in Phase 3)
    - GET  /dashboard → serves dashboard_viewer.html (no auth gate yet)
    - Everything else → 404
"""

from __future__ import annotations

import http.server
import logging
import pathlib
import sys
from http import HTTPStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# Logging - plain, no third-party logging library.
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
HOST: str = "127.0.0.1"
PORT: int = 8080
UI_DIR: pathlib.Path = pathlib.Path(__file__).parent / "ui"

_MIME_TYPES: dict[str, str] = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------
class AuthEngineHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the auth_engine application.

    Dispatches GET and POST requests to the appropriate static file or
    stub handler. All authentication and authorisation logic is added in
    later phases by replacing stub handlers with real implementations.
    """

    # Suppress the default per-request log line from BaseHTTPRequestHandler
    # (it writes to stderr via print). We use our own structured logger instead.
    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        """Override default stderr logging with structured logger."""
        logger.info("%s %s", self.address_string(), format % args)

    # ------------------------------------------------------------------
    # Route dispatch
    # ------------------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802  (stdlib naming convention)
        """Dispatch GET requests to the appropriate handler."""
        routes: dict[str, str] = {
            "/": "login.html",  # root → login
            "/login": "login.html",
            "/dashboard": "dashboard_viewer.html",
            "/dashboard/admin": "dashboard_admin.html",
        }

        if self.path == "/":
            self._redirect("/login")
            return

        template_name = routes.get(self.path)
        if template_name is None:
            self._send_not_found()
            return

        self._serve_html(template_name)

    def do_POST(self) -> None:  # noqa: N802
        """Dispatch POST requests to the appropriate handler.

        Phase 0: login form submission returns 200 with a placeholder body.
        Real credential verification is wired in Phase 3.
        """
        if self.path == "/login":
            self._handle_login_post()
        else:
            self._send_not_found()

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _handle_login_post(self) -> None:
        """Handle a login form POST submission.

        Phase 0 stub: reads and discards the body, returns 200.
        Phase 3 will replace this with credential verification.
        """
        content_length = int(self.headers.get("Content-Length", 0))
        _body = self.rfile.read(content_length)  # consumed but not yet used

        # TODO(Phase 3): parse form body, delegate to PasswordAuthenticator
        placeholder = (
            b"<html><body><p>Login stub - Phase 3 will wire auth here.</p></body>"
            b"</html>"
        )
        self._send_response_bytes(
            HTTPStatus.OK, "text/html; charset=utf-8", placeholder
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _serve_html(self, filename: str) -> None:
        """Read an HTML file from the ui directory and write it to the response.

        Args:
            filename: Basename of the file within the ui/ directory.
        """
        filepath = UI_DIR / filename
        if not filepath.is_file():
            logger.error("Template not found: %s", filepath)
            self._send_not_found()
            return

        content = filepath.read_bytes()
        self._send_response_bytes(HTTPStatus.OK, "text/html; charset=utf-8", content)

    def _redirect(self, location: str) -> None:
        """Send a 302 Found redirect response.

        Args:
            location: The URL to redirect the client to.
        """
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", location)
        self.end_headers()

    def _send_not_found(self) -> None:
        """Send a 404 Not Found response with a plain text body."""
        body = b"404 Not Found"
        self._send_response_bytes(HTTPStatus.NOT_FOUND, "text/plain", body)

    def _send_response_bytes(
        self,
        status: HTTPStatus,
        content_type: str,
        body: bytes,
    ) -> None:
        """Send an HTTP response with the given status, content-type, and body.

        Args:
            status: HTTP status code enum value.
            content_type: Value for the Content-Type response header.
            body: Response body as bytes.
        """
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run_server(host: str = HOST, port: int = PORT) -> None:
    """Start the HTTP server and block until interrupted.

    Args:
        host: Interface to bind to. Defaults to loopback (127.0.0.1).
        port: TCP port to listen on. Defaults to 8080.
    """
    address = (host, port)
    with http.server.HTTPServer(address, AuthEngineHandler) as server:
        logger.info("auth_engine listening on http://%s:%d", host, port)
        logger.info("Press Ctrl+C to stop.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down.")


if __name__ == "__main__":
    run_server()
