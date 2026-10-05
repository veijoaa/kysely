from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import urllib.error
import urllib.request


HOST = "127.0.0.1"
PORT = 8000
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"
MODEL = "jobautomation/OpenEuroLLM-Finnish:latest"  # oletusmalli
ROOT = Path(__file__).resolve().parent
MAX_REQUEST_SIZE = 1_000_000


def list_models():
    with urllib.request.urlopen(OLLAMA_TAGS_URL, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    return sorted(
        item["name"]
        for item in data.get("models", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    )


class RequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        if self.path not in ("/api/chat", "/api/models", "/api/load"):
            self.send_error(404)
            return

        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/models":
            try:
                models = list_models()
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
                self._send_json(502, {"error": f"Mallilistaa ei saatu Ollamalta. ({error})"})
                return
            self._send_json(200, {"models": models, "default": MODEL})
            return

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
        if self.path not in ("/api/chat", "/api/load"):
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

        if self.path == "/api/load":
            self._load_model(payload)
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

        model = self._requested_model(payload)
        if model is None:
            return

        request_data = json.dumps(
            {"model": model, "messages": messages, "stream": False}
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
                        f"käynnissä ja malli {model} on ladattu. ({error})"
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

    def _requested_model(self, payload):
        model = payload.get("model", MODEL) if isinstance(payload, dict) else None
        if not isinstance(model, str):
            self._send_json(400, {"error": "Mallin nimi on virheellinen."})
            return None
        if model != MODEL:
            try:
                installed = list_models()
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
                self._send_json(502, {"error": f"Mallilistaa ei saatu Ollamalta. ({error})"})
                return None
            if model not in installed:
                self._send_json(400, {"error": f"Mallia {model} ei ole asennettu."})
                return None
        return model

    def _load_model(self, payload):
        model = self._requested_model(payload)
        if model is None:
            return

        # Ollama lataa mallin muistiin, kun chat-pyyntö on ilman viestejä.
        request = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps({"model": model, "messages": []}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                response.read()
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            self._send_json(502, {"error": f"Mallin lataus epäonnistui ({error.code}): {detail}"})
            return
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            self._send_json(502, {"error": f"Mallin lataus epäonnistui. ({error})"})
            return

        self._send_json(200, {"loaded": model})

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
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}")


if __name__ == "__main__":
    print(f"Kyselysivu: http://localhost:{PORT}")
    print(f"Paikallinen malli: {MODEL}")
    ThreadingHTTPServer((HOST, PORT), RequestHandler).serve_forever()
