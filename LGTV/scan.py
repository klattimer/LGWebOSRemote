import socket
import re
from urllib.parse import unquote
import json


def LGTVScan():
    request = b'M-SEARCH * HTTP/1.1\r\n' \
              b'HOST: 239.255.255.250:1900\r\n' \
              b'MAN: "ssdp:discover"\r\n' \
              b'MX: 2\r\n' \
              b'ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n\r\n'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)

    addresses = []
    attempts = 4
    for i in range(attempts):
        sock.sendto(request, (b'239.255.255.250', 1900))
        uuid = None
        model = None
        address = None
        data = {}
        response, address = sock.recvfrom(512)
        for line in response.split(b'\n'):
            if line.startswith(b'USN'):
                uuid = re.findall(r'uuid:(.*?):', line.decode('utf-8'))[0]
            if line.startswith(b'DLNADeviceName'):
                (junk, data) = line.split(b':')
                data = data.strip().decode('utf-8')
                model = re.findall(r'\[LG\] webOS TV (.*)', unquote(data))[0]
            data = {
                'uuid': uuid,
                'model': model,
                'address': address[0].decode('utf-8')
            }

        if re.search(b'LG', response):
            addresses.append(data)
        else:
            print ('Unknown device')
            print (json.dumps(data))

    sock.close()
    return list(set(addresses))
