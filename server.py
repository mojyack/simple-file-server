#!/usr/bin/env python3
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from io import BytesIO

import multipart

class Server(SimpleHTTPRequestHandler):
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
