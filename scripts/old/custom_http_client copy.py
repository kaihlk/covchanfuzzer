# Customized HTTP Module from Scapy
# Provides Connection over Sockets instead of tcpclient
# Also provides a method to build a TLS Connection over the Socket

# Inspired by
# See http://www.secdev.org/projects/scapy for more information
# Copyright (C) Philippe Biondi <phil@secdev.org>
# This program is published under a GPLv2 license

from scapy.layers.http import HTTP, HTTPRequest

import socket
import sys
import scapy.supersocket as SuperSocket
import ssl
import time

class CustomHTTP(HTTP):
    '''Class to build up a http/1 connection to host via a socket'''
    
    def lookup_dns(self, hostname, portnumber):
        '''Function to make a DNS Lookup for a specified host or localhost using sockets and return the received data as a dictionary of tuples ''' 
        if hostname.lower() == "localhost":
            hostname = "127.0.0.1"
        try:
            # Lookup IP of HTTP Endpoint
            address = socket.getaddrinfo(
                hostname,
                portnumber,
                socket.INADDR_ANY,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
            )
        except socket.gaierror as ex:
            print(f"DNS Lookup failed: {str(ex)}")
            sys.exit(1)
        return address

    def create_tcp_socket(self, addrlist):
        '''Create a TCP socket'''
        # Build socket
        s = socket.socket(addrlist[0][0], addrlist[0][1], addrlist[0][2])
        # Set socket options
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Allow reuse immediately after closed
        if hasattr(socket, "SO_REUSEPORT"):
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        return s

    def upgrade_to_tls(self, s, hostname):
        '''Upgrade a tcp socket connection to TLS'''
        # Testing support for ALPN
        assert ssl.HAS_ALPN
        # Building the SSL context
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.load_verify_locations("/etc/ssl/certs/ca-certificates.crt")
        # Export Sessionkeys, to be able to analyze encrypted Traffic with Wireshark etc.
        ssl_ctx.keylog_filename = "sessionkeys.txt"
        ssl_ctx.set_alpn_protocols(["http/1.1"])  # h2 is a RFC7540-hardcoded value
        ssl_sock = ssl_ctx.wrap_socket(s, server_hostname=hostname)

        return ssl_sock

    def http_request(
        self,
        host,
        path="/",
        port=80,
        host_ip_info=None,
        timeout=3,
        #display=False,
        #verbose=0,
        custom_request=None,
        **headers,
    ):
        """Util to perform an HTTP request, using a socket connection.

        param host: the host to connect to
        param path: the path of the request (default /)
        param port: the port (default 80)
        param timeout: timeout before None is returned
        param display: display the result in the default browser (default False)
        param headers: any additional headers passed to the request

        returns: the HTTPResponse packet
        """
        #Initialize Variables
        response = None
        response_time=0
        error_message = None
        
        
        # DNS Lookup if info not provided
        if host_ip_info is None:
            host_ip_info = self.lookup_dns(host, port)

        #TODO Add IPV6 support
        http_headers = {
            "Accept_Encoding": b"gzip, deflate",
            "Cache_Control": b"no-cache",
            "Pragma": b"no-cache",
            "Connection": b"keep-alive",
            "Host": host,
            "Path": path,
        }
        http_headers.update(headers)
        if custom_request is not None:
            http_headers = custom_request
            req = custom_request.encode()
        else:
            req = HTTP() / HTTPRequest(**http_headers)

        # Check
        print(req)

        # Establish a socket connection
        sock = self.create_tcp_socket(host_ip_info)
        # Upgrade to TLS depending on the port
        if 443 == port:
            try:
                tls_socket = self.upgrade_to_tls(sock, host)
                # Connect Socket to TCP Endpoint
                tls_socket.connect(host_ip_info[0][4])
                tls_socket.settimeout(timeout)
                assert "http/1.1" == tls_socket.selected_alpn_protocol()
                stream_socket = SuperSocket.SSLStreamSocket(tls_socket, basecls=HTTP)
            except socket.error as ex:
                error_message = str(ex)
                stream_socket = None 
        else:
            try:
                sock.connect((host_ip_info[0][4]))
                sock.settimeout(timeout)
                stream_socket = SuperSocket.StreamSocket(sock, basecls=HTTP)
            except socket.error as ex2:
                error_message = str(ex2)
                stream_socket = None 


        if stream_socket is not None:
            try:
                # Send the request over the socket
                start_time=time.time()
                stream_socket.send(req)
                # Receive the response
                response = stream_socket.recv()
                end_time = time.time()
                response_time=end_time-start_time
    
            except socket.timeout:
                error_message="Timeout Limit reached"
                response = None
            except socket.error as ex3:
                error_message=str(ex3)
                response=None
            finally:
                # Close the socket
                if 443 == port:
                    tls_socket.shutdown(1)
                    stream_socket.close()
                else:
                    stream_socket.shutdown()            
                    stream_socket.close()

        return response, response_time, error_message