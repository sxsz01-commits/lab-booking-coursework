"""Local HTTP entry point for the lab booking MVP."""

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .core.booking import ConflictError, ValidationError
from .db import ROOT, cancel_booking, create_booking, init_db, list_bookings, list_labs
from .utils.jsonio import json_bytes


STATIC = Path(__file__).parent / "static"


class Handler(BaseHTTPRequestHandler):
    db_path: Path = ROOT / "data" / "lab.db"

    def respond(self, status: int, data: object) -> None:
        payload = json_bytes(data)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        route = urlsplit(self.path).path
        if route == "/api/labs":
            return self.respond(200, {"labs": list_labs(self.db_path)})
        if route == "/api/bookings":
            return self.respond(200, {"bookings": list_bookings(self.db_path)})
        assets = {"/": ("index.html", "text/html"),
                  "/style.css": ("style.css", "text/css"),
                  "/app.js": ("app.js", "text/javascript")}
        if route in assets:
            name, mime = assets[route]
            data = (STATIC / name).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", f"{mime}; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            return self.wfile.write(data)
        self.respond(404, {"error": "页面不存在"})

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/bookings":
            return self.respond(404, {"error": "接口不存在"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 8192:
                raise ValidationError("请求体大小不正确")
            import json
            data = json.loads(self.rfile.read(length))
            item = create_booking(self.db_path, data)
        except ConflictError as exc:
            return self.respond(409, {"error": str(exc)})
        except (ValueError, ValidationError) as exc:
            return self.respond(400, {"error": str(exc)})
        self.respond(201, {"booking": item})

    def do_DELETE(self) -> None:
        route = urlsplit(self.path).path
        if not route.startswith("/api/bookings/"):
            return self.respond(404, {"error": "接口不存在"})
        try:
            booking_id = int(route.rsplit("/", 1)[1])
        except ValueError:
            return self.respond(400, {"error": "预约编号无效"})
        if cancel_booking(self.db_path, booking_id):
            self.respond(200, {"cancelled": booking_id})
        else:
            self.respond(404, {"error": "预约不存在"})


def main() -> None:
    host = os.getenv("LAB_HOST", "127.0.0.1")
    port = int(os.getenv("LAB_PORT", "8000"))
    Handler.db_path = Path(os.getenv("LAB_DB", str(ROOT / "data" / "lab.db")))
    init_db(Handler.db_path)
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"实验室预约系统：http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

