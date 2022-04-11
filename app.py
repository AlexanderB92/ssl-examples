import ssl
import urllib.parse

#GET CERT
url = 'https://www.google.com'
addr = urllib.parse.urlsplit(url).hostname
port = 443
cert = ssl.get_server_certificate((addr, port))
print(cert)