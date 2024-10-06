from ws4py.client.threadedclient import WebSocketClient
import ssl

class WebSocketClientPatch(WebSocketClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def connect(self):
        """
        Connects this websocket and starts the upgrade handshake
        with the remote endpoint.
        """
        if self.scheme == "wss":
            # default port is now 443; upgrade self.sender to send ssl
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            if self.ssl_options.get('certfile', None):
                context.load_cert_chain(self.ssl_options.get('certfile'), self.ssl_options.get('keyfile'))
            # Prevent check_hostname requires server_hostname (ref #187)
            if "cert_reqs" not in self.ssl_options:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            self.sock = context.wrap_socket(self.sock)
            self._is_secure = True

        self.sock.connect(self.bind_addr)

        self._write(self.handshake_request)

        response = b''
        doubleCLRF = b'\r\n\r\n'
        while True:
            bytes = self.sock.recv(128)
            if not bytes:
                break
            response += bytes
            if doubleCLRF in response:
                break

        if not response:
            self.close_connection()
            raise HandshakeError("Invalid response")

        headers, _, body = response.partition(doubleCLRF)
        response_line, _, headers = headers.partition(b'\r\n')

        try:
            self.process_response_line(response_line)
            self.protocols, self.extensions = self.process_handshake_header(headers)
        except HandshakeError:
            self.close_connection()
            raise

        self.handshake_ok()
        if body:
            self.process(body)
