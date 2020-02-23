import sys
import socket
import struct
import time
from timeit import default_timer

ipaddress = "192.168.1.102"
ini_serveripv4 = "192.168.1.105"

class SSDPClient:
    def __init__(self):
        self.message = "init"
        #self.status = DRIVER_OK
        self.SSDP_PORT = 1900
        self.scope = None

        socket.setdefaulttimeout(1)

    def open_v4(self, ipaddress):
        self.SSDP_ADDR = '239.255.255.250'
        self.myIP = ipaddress
        self.mysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def open_v6(self, scope, ipaddress):
        self.scope = scope
        self.myIP = ipaddress

        if self.scope == IPV6_SITE_LOCAL:
            # Site-local multicast scope: FF05::C
            self.SSDP_ADDR = 'FF05::C'
        elif self.scope == IPV6_LINK_LOCAL:
            # Link-local multicast scope: FF02::C
            self.SSDP_ADDR = 'FF02::C'
        else:
            pass

        self.mysocket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

    def close(self):
        self.mysocket.close()

    def handle_ssdp_packet(self, recv_packet, first_line):
        # notify_dict = self.handle_ssdp_packet(packet, {'req_line': 'NOTIFY * HTTP/1.1'})
        # ms_dict     = self.handle_ssdp_packet(packet, {'resp_line': 'HTTP/1.1 200 OK'})
        #
        # receive packet =>
        # HTTP/1.1 200 OK\r\n
        # CACHE-CONTROL: max-age=1800\r\n
        # DATE: Mon, 12 Jan 1970 23:02:19 GMT\r\n
        # ST: urn:redfishspecification-org:service:redfish-rest:1\r\n
        # USN: uuid:4154270c-b47b-4e52-8ae2-64d809bf82f5::urn:redfishspecification-org:service:redfish-rest:1\r\n
        # EXT:\r\n
        # SERVER: Ubuntu/precise UPnP/1.1 MiniUPnPd/1.8\r\n
        # LOCATION: http://10.162.244.176:0/rest/v1\r\n\r\n

        # ['M-SEARCH * HTTP/1.1', 'Host:239.255.255.250:1900', 'ST:urn:schemas-upnp-org:device:InternetGatewayDevice:1',
        # 'Man:"ssdp:discover"', 'MX:3']

        # ['NOTIFY * HTTP/1.1', 'HOST: 239.255.255.250:1900', 'CACHE-CONTROL: max-age=1800', 'AL: https://10.162.247.213:8080/redfish/v1', 
        # 'SERVER: Linux/3.11.0-15-generic Redfish/1.0', 'NT: urn:dmtf-org:service:redfish-rest:1', 'USN: uuid:00000000-0000-0000-0005-000000000001::urn:dmtf-org:service:redfish-rest:1',
        # 'NTS: ssdp:alive']

        key, value = first_line.popitem()
        ssdp_dict = {}

        raw_ssdp_content = recv_packet.decode()
        list_raw_ssdp_content = raw_ssdp_content.split("\r\n")
        # remove "\r\n\r\n" in the tail.
        list_raw_ssdp_content = list_raw_ssdp_content[:-2]

        # list_raw_ssdp_content[0] == 'M-SEARCH * HTTP/1.1' or 'NOTIFY * HTTP/1.1'
        if list_raw_ssdp_content[0] == value:
            ssdp_dict[key] = list_raw_ssdp_content[0]
            for ssdp_content in list_raw_ssdp_content[1:]:
                ssdp_content = ssdp_content.split(":", 1)
                ssdp_dict[ssdp_content[0].upper()] = ssdp_content[1].strip()
        else:
            # if it doesn't match the request line, return {}
            pass

        return ssdp_dict
        
class SSDPNotify(SSDPClient):
    def __init__(self,ip_address):
        #SSDPClient.__init__(self)
        super().__init__()


        self.__setup_v4(ip_address)


        try:
            self.mysocket.bind(('', self.SSDP_PORT))
        except:
            #$self.status = DRIVER_BIND_ERROR
            self.message = sys.exc_info()[0]

            # Print error message on the screen.
            # Traceback (most recent call last):
            #   File "main.py", line 22, in <module>
            #     from lib.system_api import *
            #   File "E:\Work\mywork_git\Redfish_script\RedFish\lib\system_api.py", line 14, in <module>
            #     import test_case.ssdp as ssdp
            #   File "E:\Work\mywork_git\Redfish_script\RedFish\test_case\ssdp.py", line 3, in <module>
            #     from lib.ssdp_api import *
            #   File "E:\Work\mywork_git\Redfish_script\RedFish\lib\ssdp_api.py", line 7, in <module>
            #     sc1 = SSDPNotify()
            #   File "E:\Work\mywork_git\Redfish_script\RedFish\lib\driver.py", line 123, in __init__
            #     self.mysocket.bind((any_ip, self.SSDP_PORT))
            # OSError: [WinError 10022]
            #raise
    def __del__():
        print("SSDPNotify instance was deleted...")

    def __setup_v4(self, ip_address):
        self.open_v4(ip_address)
        self.mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Receive UDP multicast
        # The ip_mreq structure (taken from /usr/include/linux/in.h) has the following members:
        #
        # struct ip_mreq
        # {
        #         struct in_addr imr_multiaddr;   /* IP multicast address of group */
        #         struct in_addr imr_interface;   /* local IP address of interface */
        # };
        #
        # struct:
        #  = : native byte order
        #  I : unsigned int
        #
        # mreq = <IP multicast address> + <interface>
        # mreq = b'\xef\xff\xff\xfa\x00\x00\x00\x00'

        self.mreq = socket.inet_pton(socket.AF_INET, self.SSDP_ADDR) + struct.pack('=I', socket.INADDR_ANY)
        self.mysocket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)

    def __del__(self):
        self.close()

    def recv_notify(self, timeout):
        notify_list = []

        start_time = time.time()
        end_time = start_time
        while (end_time - start_time) < timeout:
            end_time = time.time()
            try:
                packet, address = self.mysocket.recvfrom(2048)
            except socket.timeout:
                # If receive nothing in 1 seconds, it will timeout.
                # But some cases we wait for a little more time to make sure all the response return.
                continue

            # To filter if first line must be 'NOTIFY * HTTP/1.1'
            notify_dict = self.handle_ssdp_packet(packet, {'req_line': 'NOTIFY * HTTP/1.1'})
            if notify_dict:
                notify_list.append(notify_dict)

        return notify_list

class SSDPMsearch(SSDPClient):
    def __init__(self, ip_type, ip_address, ipv6_type):
        #SSDPClient.__init__(self)
        super().__init__()

        if ip_type == IP_V4:
            self.__setup_v4(ip_address)
        else:
            self.__setup_v6(ip_address, ipv6_type)

    def __del__(self):
        self.close()

    def __setup_v4(self, ipaddress):
        self.open_v4(ipaddress)
        # multicast the packet
        self.mysocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        self.mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Format example:
        # >>> '{2}, {1}, {0}'.format(*'abc')      # unpacking argument sequence
        # =>  'c, b, a'
        #
        # >>> coord = {'latitude': '37.24N', 'longitude': '-115.81W'}
        # >>> 'Coordinates: {latitude}, {longitude}'.format(**coord)
        # =>  'Coordinates: 37.24N, -115.81W'
        self.msearch_header = 'M-SEARCH * HTTP/1.1\r\nHOST: {host_ip}:{host_port}\r\nMAN: "{MAN_header}"\r\nMX: {MAX_wait_time}\r\nST: {search_target}\r\n\r\n\r\n'

    def send_msearch(self, timeout, specific_req_field={}, invalid_header=[]):
        # In Windows, if we don't use the following code, sometimes we can't receive M-Search response.
        #
        # In Linux, it should need to bind selected IP address, espically for IPv6(site-local).
        # Because we usually have more than 1 IPv6 address for our ethernet card.
        if platform.system() == "Windows" or (platform.system() == "Linux" and self.scope == IPV6_SITE_LOCAL):
            try:
                self.mysocket.bind((self.myIP, 0))
            except:
                #self.status = DRIVER_BIND_ERROR
                self.message = str(sys.exc_info()[1])
                # Print error message on the screen.
                # Traceback (most recent call last):
                #   File "main.py", line 22, in <module>
                #     from lib.system_api import *
                #   File "E:\Work\mywork_git\Redfish_script\RedFish\lib\system_api.py", line 14, in <module>
                #     import test_case.ssdp as ssdp
                #   File "E:\Work\mywork_git\Redfish_script\RedFish\test_case\ssdp.py", line 3, in <module>
                #     from lib.ssdp_api import *
                #   File "E:\Work\mywork_git\Redfish_script\RedFish\lib\ssdp_api.py", line 7, in <module>
                #     sc1 = SSDPNotify()
                #   File "E:\Work\mywork_git\Redfish_script\RedFish\lib\driver.py", line 123, in __init__
                #     self.mysocket.bind((any_ip, self.SSDP_PORT))
                # OSError: [WinError 10022]
                #raise
                return []

        # M-SEARCH request default value
        req_field = {'host_ip': self.SSDP_ADDR, 'host_port': self.SSDP_PORT,
                     'MAN_header': 'ssdp:discover', 'MAX_wait_time': 2,
                     'search_target': 'ssdp:all'}

        if specific_req_field:
            for key, value in specific_req_field.items():
                req_field[key] = value

        if invalid_header:
            msearch = invalid_header
        else:
            msearch = self.msearch_header.format(**req_field)

        # ms_list = [{ms_dict1}, {ms_dict2}, ...]
        ms_list = []
        self.mysocket.sendto(msearch.encode(), (req_field['host_ip'], req_field['host_port']))

        start_time = time.time()
        end_time = start_time
        while (end_time - start_time) < timeout:
            end_time = time.time()
            try:
                packet, address = self.mysocket.recvfrom(2048)

            except socket.timeout:
                # If receive nothing in 1 seconds, it will timeout.
                # But some cases we wait for a little more time to make sure all the response return.
                continue
            ms_dict = self.handle_ssdp_packet(packet, {'resp_line': 'HTTP/1.1 200 OK'})
            if ms_dict:
                ms_list.append(ms_dict)

        return ms_list

test = SSDPNotify(ipaddress)
test1 = test.recv_notify(20)
print(test1)