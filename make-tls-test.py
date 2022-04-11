

from collections import namedtuple
from http.client import HTTPResponse
import urllib.parse
import cgi
import socket
import ssl
import certifi

ca_certs = certifi.where()

def http(url, secure=443, encoding='utf-8'):
    components = urllib.parse.urlsplit(url)
    path = '%s' % components.path if components.path else '/'
    HTTPS = (components.scheme == 'https')
    address = components.hostname
    port = secure if HTTPS else 80
    #carriage return def
    CRLF = '\r\n\r\n'

    Page = namedtuple('Page', ('code', 'headers', 'body'))

    def handshake(sock):
        new_sock = ssl.wrap_socket(sock,
                                ciphers="HIGH:-aNULL:-eNULL:-PSK:RC4-SHA:RC4-MD5",
                                ssl_version=ssl.PROTOCOL_TLSv1,
                                cert_reqs=ssl.CERT_REQUIRED, #verify server
                                ca_certs=ca_certs
                                ) #with this
        return new_sock
    
    def make_header():
        headers = [
            'GET %s HTTP/1.1' % (path),
            'Host: %s' % address,
            'User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1',
            'Charset: %s' % encoding
        ]

        header = '\n'.join(headers)
        header += CRLF
        return bytes(header, encoding=encoding)

    def parse_response(resp):
        '''
        resp
            http.client.HTTPResponse, not closed
        '''
        resp.begin()
        status = resp.getcode()
        headers = dict(resp.getheaders())
        def get_charset():
            ctt_type = headers.get('Content-Type')
            return cgi.parse_header(ctt_type)[1].get('charset', encoding)
        body = resp.read()
        body = str(body, encoding=get_charset())
        return Page(status, headers, body)
    
    def request(header):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((address, port))
        try:
            if HTTPS: sock = handshake(sock)
            sock.sendall(header)
            resp = HTTPResponse(sock)
            #log resp
            print(parse_response(resp))
            return parse_response(resp)
        finally:
            sock.shutdown(1)
            sock.close()
    
    return request(make_header())

http("https://www.google.com")