from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import urllib.error
import urllib.request


HOST = "127.0.0.1"
PORT = 8000
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "jobautomation/OpenEuroLLM-Finnish:latest"
ROOT = Path(__file__).resolve().parent
MAX_REQUEST_SIZE = 1_000_000


class RequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        if self.path != "/api/chat":
            self.send_error(404)
            return

        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return

        try:
            page = (ROOT / "index.html").read_bytes()
        except OSError as error:
            self.send_error(500, f"Sivun lukeminen epäonnistui: {error}")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "Virheellinen Content-Length."})
            return

        if content_length <= 0 or content_length > MAX_REQUEST_SIZE:
            self._send_json(413, {"error": "Pyyntö puuttuu tai on liian suuri."})
            return

        try:
            payload = json.loads(self.rfile.read(content_length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "Pyyntö ei ole kelvollista JSON-dataa."})
            return

        messages = payload.get("messages") if isinstance(payload, dict) else None
        if (
            not isinstance(messages, list)
            or not messages
            or any(
                not isinstance(message, dict)
                or message.get("role") not in ("user", "assistant", "system")
                or not isinstance(message.get("content"), str)
                for message in messages
            )
        ):
            self._send_json(400, {"error": "Viestihistoria on virheellinen."})
            return

        request_data = json.dumps(
            {"model": MODEL, "messages": messages, "stream": False}
        ).encode("utf-8")
        request = urllib.request.Request(
            OLLAMA_URL,
            data=request_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            self._send_json(
                502,
                {"error": f"Ollama palautti virheen ({error.code}): {detail}"},
            )
            return
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            self._send_json(
                502,
                {
                    "error": (
                        "Ollamaan ei saatu yhteyttä. Varmista, että Ollama on "
                        f"käynnissä ja malli {MODEL} on ladattu. ({error})"
                    )
                },
            )
            return
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            self._send_json(502, {"error": f"Ollaman vastaus ei ollut kelvollinen: {error}"})
            return

        message_data = result.get("message") if isinstance(result, dict) else None
        message = message_data.get("content") if isinstance(message_data, dict) else None
        if not isinstance(message, str):
            self._send_json(502, {"error": "Ollaman vastauksesta puuttui viestisisältö."})
            return

        self._send_json(200, {"answer": message})

    def _send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}")


if __name__ == "__main__":
    print(f"Kyselysivu: http://localhost:{PORT}")
    print(f"Paikallinen malli: {MODEL}")
    ThreadingHTTPServer((HOST, PORT), RequestHandler).serve_forever()
