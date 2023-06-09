#Customized HTTP Module from Scapy
#Provides Connection over Sockets instead of tcpclient
#Also provides a method to build a TLS Connection over the Socket 


from scapy.layers.http import *

import socket
import sys
import scapy.supersocket as SuperSocket
import ssl


class CustomHTTP(HTTP):
    def lookup_dns(self, hostname, portnumber):
        try:
            # Lookup IP of HTTP Endpoint
            address = socket.getaddrinfo(hostname, portnumber, socket.INADDR_ANY, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        except socket.gaierror as e:
            print(f'DNS Lookup failed: {str(e)}')
            sys.exit(1)   
        return address
    
    def create_tcp_socket(self, addrlist):
        # Build socket
        s = socket.socket(addrlist[0][0], addrlist[0][1], addrlist[0][2])
        # Set socket options
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Allow reuse immediately after closed
        if hasattr(socket, 'SO_REUSEPORT'):
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        return s
    
    def upgrade_to_tls(self, s, hostname):
        # Testing support for ALPN
        assert(ssl.HAS_ALPN)
        # Building the SSL context
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT) 
        ssl_ctx.load_verify_locations("/etc/ssl/certs/ca-certificates.crt")
        #Export Sessionkeys, to be able to analyze encrypted Traffic with Wireshark etc.
        ssl_ctx.keylog_filename="sessionkeys.txt"
        ssl_ctx.set_alpn_protocols(['http/1.1'])  # h2 is a RFC7540-hardcoded value
        ssl_sock = ssl_ctx.wrap_socket(s, server_hostname=hostname)
    
        return ssl_sock



    def http_request(self, host, path="/", port=80, timeout=3,
                    display=False, verbose=0, customRequest=None, **headers):
        """Util to perform an HTTP request, using a socket connection.

        :param host: the host to connect to
        :param path: the path of the request (default /)
        :param port: the port (default 80)
        :param timeout: timeout before None is returned
        :param display: display the result in the default browser (default False)
        :param headers: any additional headers passed to the request

        :returns: the HTTPResponse packet
        """
        http_headers = {
            "Accept_Encoding": b'gzip, deflate',
            "Cache_Control": b'no-cache',
            "Pragma": b'no-cache',
            "Connection": b'keep-alive',
            "Host": host,
            "Path": path,
        }
        http_headers.update(headers)
        if customRequest is not None:
            http_headers=customRequest
            req=customRequest.encode()
        else:
            req = HTTP() / HTTPRequest(**http_headers)
        
        #Check
        print(req)
        #Lookup Domain
        host_ip_address_info=self.lookup_dns(host,port)
        # Establish a socket connection
        sock=self.create_tcp_socket(host_ip_address_info)
        # Upgrade to TLS depending on the port
        if (443==port):
            tls_socket = self.upgrade_to_tls(sock, host)
            #Connect Socket to TCP Endpoint
            tls_socket.connect(host_ip_address_info[0][4])
            tls_socket.settimeout(timeout)
            assert('http/1.1' == tls_socket.selected_alpn_protocol())
            stream_socket = SuperSocket.SSLStreamSocket(tls_socket, basecls=HTTP)
        else:
            sock.connect((host_ip_address_info[0][4]))
            sock.settimeout(timeout)
            stream_socket = SuperSocket.StreamSocket(sock, basecls=HTTP)
        
      

        ans = None
        try:
            # Send the request over the socket
            stream_socket.send(req)
            

            # Receive the response

            response = stream_socket.recv()

            # Create an HTTPResponse packet with the received response This part is not working properly
            ans = response #HTTPResponse(response)
        except socket.timeout:
           print("Timeout Limit reached")
           ans = None
        finally:
        
            # Close the socketas
            if (443==port):
                tls_socket.shutdown(1)
                stream_socket.close()
            else:
                sock.shutdown(1)
                stream_socket.close()

        return ans
    
##Testing:


""" 
host='www.example.com'
http_packet = CustomHTTP()
myRequest= generate_chromium_header("www.example.com")
answer=http_packet.http_request(host,port=80, customRequest=myRequest[0])
received_status=answer.Status_Code.decode('utf-8')
print('TCP:')
print(received_status)

host='www.example.com'
http_packet2 = CustomHTTP()

answer=http_packet2.http_request(host,port=443)
received_status=answer.Status_Code.decode('utf-8')
print('TLS:')
print(received_status) """