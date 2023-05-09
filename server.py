#!/usr/bin/env python3
import os
from http import HTTPStatus
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from os.path import dirname, join
from io import BytesIO

import multipart

class Server(SimpleHTTPRequestHandler):
    def send_head_abs(self, path):
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        ctype = super().guess_type(path)
        try:
            fs = os.fstat(f.fileno())
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(fs[6]))
            self.end_headers()
            return f
        except:
            f.close()
            raise

    def do_GET(self):
        if self.path == '/':
            path = join(dirname(__file__), "index.html")
            f = self.send_head_abs(path)
            if f:
                try:
                    self.copyfile(f, self.wfile)
                finally:
                    f.close()
        else:
            super().do_GET()

    def do_POST(self):
        ctype = self.headers['content-type']
        clen = int(self.headers['content-length'])
        if ctype.startswith('text/plain'):
            text = self.rfile.read(clen).decode('utf-8')[5:-2]
            print('message: "{}"'.format(text))
        elif ctype.startswith('multipart/form-data'):
            boundary = ctype[ctype.find('=') + 1:]
            parser = multipart.MultipartParser(BytesIO(self.rfile.read(clen)), boundary)

            for part in parser.parts():
                if len(part.filename) == 0:
                    continue
                print("received:", part.filename)
                open(part.filename, "wb").write(part.raw)
        else:
            self.send_response(412)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()

server = HTTPServer(("0.0.0.0", 8000), Server)
server.serve_forever()
