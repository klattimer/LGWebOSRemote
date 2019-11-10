import socket
import re
from urllib.parse import unquote


def LGTVScan():
    request = 'M-SEARCH * HTTP/1.1\r\n' \
              'HOST: 239.255.255.250:1900\r\n' \
              'MAN: "ssdp:discover"\r\n' \
              'MX: 2\r\n' \
              'ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n\r\n'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)

    addresses = []
    attempts = 4
    for i in range(attempts):
        sock.sendto(request, ('239.255.255.250', 1900))
        uuid = None
        model = None
        address = None
        data = {}
        try:
            response, address = sock.recvfrom(512)
            for line in response.split('\n'):
                if line.startswith("USN"):
                    uuid = re.findall(r'uuid:(.*?):', line)[0]
                if line.startswith("DLNADeviceName"):
                    (junk, data) = line.split(':')
                    data = data.strip()
                    data = unquote(data)
                    model = re.findall(r'\[LG\] webOS TV (.*)', data)[0]
                data = {
                    'uuid': uuid,
                    'model': model,
                    'address': address[0]
                }

        except Exception as e:
            print(e)
            continue

        if re.search('LG', response):
            addresses.append(data)

    sock.close()
    return list(set(addresses))
