"""Launch the offline practice desk with python desk.py."""
import argparse
import json
import random
import threading
import webbrowser
from dataclasses import asdict
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from practice import build_deck, get_card
from progress import history, record


class Desk(BaseHTTPRequestHandler):
    def reply(self, body, mime):
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api":
            seed = random.randrange(2**32)
            data = {"seed": seed, "cards": [asdict(c) for c in build_deck(random.Random(seed))],
                    "history": list(history().values())}
            for row in data["history"]:
                if not row["correct"]:
                    row["card"] = asdict(get_card(row["topic"], row["seed"]))
            self.reply(json.dumps(data).encode(), "application/json")
        elif path == "/":
            self.reply(Path(__file__).with_name("desk.html").read_bytes(), "text/html; charset=utf-8")
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/attempt" or self.headers.get("Content-Type") != "application/json":
            return self.send_error(400)
        try:
            size = int(self.headers.get("Content-Length", 0))
            if not 0 < size <= 2048:
                raise ValueError()
            data = json.loads(self.rfile.read(size))
            topic, mode, seed, token = (data[k] for k in ("topic", "mode", "seed", "token"))
            if not (type(seed) is int and 0 <= seed < 2**32 and mode in ("open", "mcq")
                    and isinstance(token, str) and 8 <= len(token) <= 64):
                raise ValueError()
            card = get_card(topic, seed)
            if mode == "mcq" and data["answer"] in card.choices:
                correct = data["answer"] == card.choices[0]
            elif mode == "open" and type(data["answer"]) is bool:
                correct = data["answer"]
            else:
                raise ValueError()
            record(token, topic, mode, seed, correct)
        except (KeyError, TypeError, ValueError, StopIteration):
            return self.send_error(400)
        self.reply(json.dumps({"correct": correct}).encode(), "application/json")


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--port", type=int, default=0)
    cli.add_argument("--no-browser", action="store_true")
    args = cli.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), Desk) as server:
        url = f"http://127.0.0.1:{server.server_port}/"
        print(f"Quant Practice Desk: {url}", flush=True)
        if not args.no_browser:
            threading.Timer(0.4, partial(webbrowser.open, url)).start()
        server.serve_forever()
