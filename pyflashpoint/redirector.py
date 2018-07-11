import asyncio
import email
import os
import subprocess
import ssl
import hashlib
#import aiofiles
from urllib.parse import urlparse
from textwrap import dedent

""" This proxy script was originally written to archive web requests. It's repurposed into a redirector."""

#HTTP_PATH = "http"
CERTS_PATH = "certs"
CA_PATH = "ca"
#HISTORY_FILE = "http/history.txt"


class MemoryReader:
    def __init__(self, data : bytes):
        self.data = data

    async def readuntil(self, a):
        pivot = self.data.index(a) + len(a)
        ret = self.data[:pivot]
        self.data = self.data[pivot:]

        return ret

    async def readexactly(self, n):
        ret = self.data[:n]
        self.data = self.data[n:]
        return ret


class HTTPProxyHandler:
    def __init__(self, reader : asyncio.StreamReader, writer : asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.ssl = False
        self.addr = writer.get_extra_info('peername')

    async def handle(self):
        """ does the thing """

        self.body = b''
        try:
            method_line, self.headers, self.body = await self.read_request(self)
        except asyncio.streams.IncompleteReadError:
            self.writer.close()
            return False

        # GET http://www.example.com/ HTTP/1.1
        self.method, self.url, self.version = method_line.decode().split()
        if self.ssl:
            # if https, the host is omitted because the client thinks its talking directly to the server
            self.url = f"https://{self.ssl_hostname}{self.url}"

        self.log(f"{self.method} {self.url} {self.version}")

        """
        if self.url == 'http://oopsiewhoopsie.proxy/breakhttps.crt':
            async with aiofiles.open(CA_PATH + "/ca.crt", "rb") as f:
                self.body = await f.read()
            await self.send_response("200 :ok_hand:", body=self.body, addn_headers={
                'Content-Type': 'application/x-x509-ca-cert',
                'Connection': 'close'
            })

            self.writer.close()
            return False
        """


        # SSL proxy
        # CONNECT example.com:443 HTTP/1.1
        if self.method == "CONNECT" and self.url.endswith(":443"):
            self.ssl_hostname = self.url.split(':')[0]
            cert_path = os.path.join(CERTS_PATH, self.ssl_hostname + ".crt")
            if not os.path.isfile(cert_path):
                subprocess.check_call(["./mkcrt", self.ssl_hostname])
                self.log(f"./mkcrt {self.ssl_hostname} -> {cert_path}")
            self.writer.write(b"HTTP/1.1 200 Yeet Dab\r\n\r\n")

            # REALLY hacky lul
            self.ssl = True
            self._ssl_ctx = ssl.SSLContext()
            self._ssl_ctx.load_cert_chain(cert_path, keyfile=f"{CA_PATH}/cert.key")
            self._ssl_in = ssl.MemoryBIO()
            self._ssl_out = ssl.MemoryBIO()
            self._ssl_obj = self._ssl_ctx.wrap_bio(self._ssl_in, self._ssl_out, server_side=True, server_hostname=self.ssl_hostname)
            self._ssl_buf = b''
            await self.ssl_handshake()
            return True

        # drop unsupported headers oopsy whoopsy
        # reee keepalives

        keepalive = self.headers.get("Connection", "f").lower() == "keep-alive" or \
            self.headers.get("Proxy-Connection", "f").lower() == "keep-alive"

        # to hell with trailers, also the client doesn't support keepalive
        for k in ["Connection", "Proxy-Connection", "TE"]:
            try:
                del self.headers[k]
            except KeyError:
                pass

        # make the request to the host
        await self.respond()

        #self.log(f"keepalive == {keepalive}")
        if not keepalive:
            self.writer.close()

        return keepalive

    async def _ssl_op(self, op : int, data=None):
        # op
        n = 0
        while True:
            try:
                n += 1
                if op == 0:
                    self._ssl_obj.do_handshake()
                elif op == 1:
                    data = self._ssl_obj.read(8192)
                    if not data:
                        raise ConnectionAbortedError("Client broke connection!")
                    return data
                elif op == 2:
                    self._ssl_obj.write(data)
                    if self._ssl_out.pending:
                        self.writer.write(self._ssl_out.read())
                        await self.writer.drain()
                return
            except (ssl.SSLWantReadError, ssl.SSLWantWriteError) as e:
                if self._ssl_out.pending:
                    self.writer.write(self._ssl_out.read())
                self._ssl_in.write(await self.reader.read(8192))

    async def ssl_handshake(self):
        await self._ssl_op(0)

    async def ssl_read(self):
        return await self._ssl_op(1)

    async def ssl_write(self, data):
        await self._ssl_op(2, data)

    async def readuntil(self, a : bytes):
        if not self.ssl:
            return await self.reader.readuntil(a)
        else:
            while a not in self._ssl_buf:
                self._ssl_buf += await self.ssl_read()
            res = self._ssl_buf[:self._ssl_buf.index(a) + len(a)]
            self._ssl_buf = self._ssl_buf[self._ssl_buf.index(a) + len(a):]
            return res

    async def readexactly(self, n : int):
        if not self.ssl:
            return await self.reader.readexactly(n)
        else:
            while len(self._ssl_buf) < n:
                self._ssl_buf += await self.ssl_read()
            res = self._ssl_buf[:n]
            self._ssl_buf = self._ssl_buf[n:]
            return res

    async def write(self, data):
        if not self.ssl:
            return self.writer.write(data)
        else:
            await self.ssl_write(data)

    def log(self, m):
        print(f"[{self.addr[0]}:{self.addr[1]}] " + m)

    @staticmethod
    def encode_payload(prefix, headers, body):
        payload = prefix
        for k, v in headers.items():
            payload += f"{k}: {v}\r\n"
        payload += "\r\n"
        payload = payload.encode("latin-1")
        payload += body
        return payload

    @staticmethod
    async def read_request(reader):
        status_line = await reader.readuntil(b"\r\n")
        body = b''
        raw_headers = b''
        while True:
            line = await reader.readuntil(b'\r\n')
            if line == b'\r\n': break # end of headers
            raw_headers += line
        headers = dict(email.message_from_bytes(raw_headers).items())
        content_length = int(headers.get("Content-Length", 0))
        if content_length:
            body = await reader.readexactly(content_length)
        return status_line, headers, body

    async def respond(self):
        url = urlparse(self.url)
        req_line = self.url[len(url.scheme) + 3 + len(url.netloc):]

        payload = self.encode_payload(f"{self.method} {req_line} HTTP/1.1\r\n", self.headers, self.body)

        if not self.ssl:
            clreader, clwriter = await asyncio.open_connection("127.0.0.1", 22500)
        else:
            clreader, clwriter = await asyncio.open_connection("127.0.0.1", 22501, ssl=True)
        clwriter.write(payload)

        response_line, clreheaders, clrebody = await self.read_request(clreader)
        response_version, response_code, response_msg = response_line.decode().split(" ", 2)

        self.log(f"request:  {self.method} {req_line} HTTP/1.1")# {self.headers}")
        self.log(f"response: {response_version} {response_code} {response_msg}")# {clreheaders}")

        if clreheaders.get("Transfer-Encoding", "identity").lower() == "chunked":
            self.log(f"loading Transfer-Encoding: chunked")
            clreheaders['Transfer-Encoding'] = "identity"
            data = b''
            while True:
                line = (await clreader.readuntil(b"\r\n")).strip().decode()
                chunk_len = int(line, 16)
                if not chunk_len: break # reached terminating chunk
                data += await clreader.readexactly(chunk_len)
                await clreader.readexactly(2) # strip the next \r\n
            clrebody = data
            clreheaders['Content-Length'] = len(clrebody)

        response = response_line + self.encode_payload("", clreheaders, clrebody)
        #asyncio.get_event_loop().create_task(self.archive_path(url, req_line, response))

        await self.write(response)
        clwriter.close()

    async def send_response(self, status="200 OK", addn_headers={}, body=b''):
        status_line = "HTTP/1.1" + status + "\r\n"
        headers = {'Server': 'redirector', 'Content-Length': len(body), 'Content-Type': 'text/html; charset=UTF-8'}
        headers.update(addn_headers)
        await self.write(self.encode_payload(status_line, headers, body))

    def hash(self, s : str):
        return hashlib.sha256(s.encode()).hexdigest()

"""
    async def archive_path(self, url, req_line, payload):
        path = os.path.join(HTTP_PATH, self.hash(url.netloc + req_line) + ".req")
        dirs, file = os.path.split(path)
        os.makedirs(dirs, 0o755, True)
        async with aiofiles.open(path, "wb") as f:
            await f.write(payload)
            self.log(f"archived {url.netloc}{req_line} -> {path}")
        async with aiofiles.open(HISTORY_FILE, "a") as f:
            await f.write(f'{url.geturl()}\r\n')
"""



"""
class HTTPProxyReplayHandler(HTTPProxyHandler):
    async def respond(self):
        url = urlparse(self.url)
        req_line = self.url[len(url.scheme) + 3 + len(url.netloc):]
        path = os.path.join(HTTP_PATH, self.hash(url.netloc + req_line) + ".req")
        if not os.path.isfile(path):
            await self.send_response("404 Not Found", addn_headers={"Access-Control-Allow-Origin": "*"}, body=dedent(
                " ""
                <html>
                    <head><title>404 Not Archived</title></head>
                    <body>
                        <h1>OOPSIE WHOOPSIE!!</h1>
                        <p>Uwu We made a fucky wucky!! A wittle fucko boingo! The code monkeys at our headquarters are working VEWY HAWD to fix this!</p>
                    </body>
                </html>
                " "").encode("utf-8")
            )
        else:
            async with aiofiles.open(path, 'rb') as f:
                data = await f.read()
                line, headers, body = await self.read_request(MemoryReader(data))
                self.log(f"Replied {line} {headers}")
                # given only one server is ever serving anything who cares about CORS
                headers['Access-Control-Allow-Origin'] = "*"

                await self.write(self.encode_payload(line.decode(), headers, body))
"""


async def http_handler(reader, writer):
    session = HTTPProxyHandler(reader, writer)
    while True:
        try:
            if not await session.handle(): break
        except ConnectionAbortedError:
            return

"""
async def http_handler_replay(reader, writer):
    session = HTTPProxyReplayHandler(reader, writer)
    while True:
        try:
            if not await session.handle(): break
        except ConnectionAbortedError:
            return
"""

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(http_handler, '127.0.0.1', 8888, loop=loop)

    server = loop.run_until_complete(coro)

    try:
        print("starting redirection proxy")
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

