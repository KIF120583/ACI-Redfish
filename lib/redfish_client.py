import socket
import ssl
import json
from base64 import b64encode

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

class redfish_client:

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    
    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssl_sock = context.wrap_socket(sock)

    def RESTClient_Init(self , hostname , port , username , password):
        self.hostname = hostname
        self.port = port = int(port)

        self.name_pw = username + ':' + password
        self.encode_name_pw = b64encode(self.name_pw.encode()).decode("ascii")
        self.__open()

    def __open(self):
        self.ssl_sock.connect((self.hostname, self.port))

    def __send(self):
        send_packet = self.send_packet.encode()
        self.ssl_sock.send(send_packet)
        rsp_str = self.ssl_sock.recv(65536)
        rsp_str = rsp_str.decode("utf-8")

        self.response_status = int(rsp_str[9:12])
        self.response_body = rsp_str

        temp_rsp_str = rsp_str.split("\n")

        self.response_body = {}
        header = []
        for item in temp_rsp_str:
            if ":" in item and "{" not in item:
                header.append(item[:-1])
            if "{" in item:
                self.response_body = json.loads(item)

        self.response_header = {}
        temp_allow = []
        for item in header:
            temp = item.split(": ")
            if temp[0] != "Allow":
                self.response_header[temp[0]] = temp[1]
            else:
                temp_allow.append(temp[1])

        self.response_header["Allow"] = temp_allow

    def RESTClient_Get(self , url_path):
        packet_no_etag = "GET %s HTTP/1.1\r\nAuthorization: Basic %s\r\nHost: %s:%s\r\nAccept-Encoding: identity\r\nContent-Type : application/json\r\nUser-Agent: Redfish Client of Python\r\nConnection: Keep-Alive\r\n\r\n"
        self.send_packet = packet_no_etag %(url_path, self.encode_name_pw, self.hostname, self.port)
        self.__send()

    def RESTClient_Post(self , url_path , body):
        body = str(body).replace("'",'"')
        packet_no_etag = "POST %s HTTP/1.1\r\nAuthorization: Basic %s\r\nHost:%s:%s\r\nAccept-Encoding: identity\r\nContent-Length: %s\r\nContent-Type: application/json\r\nUser-Agent: Redfish Client of Python\r\nConnection: Keep-Alive\r\n\r\n%s"
        self.send_packet = packet_no_etag %(url_path, self.encode_name_pw, self.hostname, self.port , len(str(body)), str(body))
        self.__send()

    def RESTClient_Patch(self , url_path , body):
        body = str(body).replace("'",'"')
        packet_no_etag = "PATCH %s HTTP/1.1\r\nAuthorization: Basic %s\r\nHost:%s:%s\r\nAccept-Encoding: identity\r\nContent-Length: %s\r\nContent-Type: application/json\r\nUser-Agent: Redfish Client of Python\r\nConnection: Keep-Alive\r\nif-Match: %s\r\n\r\n%s"
        self.send_packet = packet_no_etag%(url_path, self.encode_name_pw, self.hostname, self.port , len(body) , self.RESTClient_Get_response_etag() , body)
        self.__send()

    def RESTClient_Get_response_status(self):
        return self.response_status

    def RESTClient_Get_response_header(self):
        return self.response_header

    def RESTClient_Get_response_etag(self):
        return self.response_header["ETag"]

    def RESTClient_Get_response_body(self):
        return self.response_body

    def RESTClient_Close(self):
        self.ssl_sock.close()

if __name__ == "__main__":

    hostname = '192.168.23.129'
    port = 8080
    username = "admin"
    password = "Password1"
    
    test = redfish_client()
    test.RESTClient_Init(hostname , port , username , password)
    
    # Get example
    test.RESTClient_Get("/redfish/v1/")
    print(test.RESTClient_Get_response_status())
    print(test.RESTClient_Get_response_header())
    print(test.RESTClient_Get_response_body())
    
    # Post example
    test.RESTClient_Post("/redfish/v1/Managers/bmc/LogServices/SEL/Actions/LogService.ClearLog" , {})
    print(test.RESTClient_Get_response_status())
    print(test.RESTClient_Get_response_header())
    print(test.RESTClient_Get_response_body())
    
    # Patch example
    test.RESTClient_Get("/redfish/v1/SessionService")
    print(test.RESTClient_Get_response_status())
    print(test.RESTClient_Get_response_header())
    print(test.RESTClient_Get_response_body())
    
    test.RESTClient_Patch("/redfish/v1/SessionService" , {"SessionTimeout":500})
    print(test.RESTClient_Get_response_status())
    print(test.RESTClient_Get_response_header())
    print(test.RESTClient_Get_response_body())
    

    