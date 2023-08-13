# Customized HTTP Module from Scapy
# Provides Connection over Sockets instead of tcpclient
# Also provides a method to build a TLS Connection over the Socket

# Inspired by
# See http://www.secdev.org/projects/scapy for more information
# Copyright (C) Philippe Biondi <phil@secdev.org>
# This program is published under a GPLv2 license

from scapy.layers.http import HTTP, HTTPRequest, HTTPResponse

import socket
import sys
import scapy.supersocket as SuperSocket
import ssl
import time
import re


GENERAL_HEADERS = [
    "Cache-Control",
    "Connection",
    "Permanent",
    "Content-Length",
    "Content-MD5",
    "Content-Type",
    "Date",
    "Keep-Alive",
    "Pragma",
    "Upgrade",
    "Via",
    "Warning"
]

COMMON_UNSTANDARD_GENERAL_HEADERS = [
    "X-Request-ID",
    "X-Correlation-ID"
]

REQUEST_HEADERS = [
    "A-IM",
    "Accept",
    "Accept-Charset",
    "Accept-Encoding",
    "Accept-Language",
    "Accept-Datetime",
    "Access-Control-Request-Method",
    "Access-Control-Request-Headers",
    "Authorization",
    "Cookie",
    "Expect",
    "Forwarded",
    "From",
    "Host",
    "HTTP2-Settings",
    "If-Match",
    "If-Modified-Since",
    "If-None-Match",
    "If-Range",
    "If-Unmodified-Since",
    "Max-Forwards",
    "Origin",
    "Proxy-Authorization",
    "Range",
    "Referer",
    "TE",
    "User-Agent"
]

COMMON_UNSTANDARD_REQUEST_HEADERS = [
    "Upgrade-Insecure-Requests",
    "Upgrade-Insecure-Requests",
    "X-Requested-With",
    "DNT",
    "X-Forwarded-For",
    "X-Forwarded-Host",
    "X-Forwarded-Proto",
    "Front-End-Https",
    "X-Http-Method-Override",
    "X-ATT-DeviceId",
    "X-Wap-Profile",
    "Proxy-Connection",
    "X-UIDH",
    "X-Csrf-Token",
    "Save-Data",
]

RESPONSE_HEADERS = [
    "Access-Control-Allow-Origin",
    "Access-Control-Allow-Credentials",
    "Access-Control-Expose-Headers",
    "Access-Control-Max-Age",
    "Access-Control-Allow-Methods",
    "Access-Control-Allow-Headers",
    "Accept-Patch",
    "Accept-Ranges",
    "Age",
    "Allow",
    "Alt-Svc",
    "Content-Disposition",
    "Content-Encoding",
    "Content-Language",
    "Content-Location",
    "Content-Range",
    "Delta-Base",
    "ETag",
    "Expires",
    "IM",
    "Last-Modified",
    "Link",
    "Location",
    "Permanent",
    "P3P",
    "Proxy-Authenticate",
    "Public-Key-Pins",
    "Retry-After",
    "Server",
    "Set-Cookie",
    "Strict-Transport-Security",
    "Trailer",
    "Transfer-Encoding",
    "Tk",
    "Vary",
    "WWW-Authenticate",
    "X-Frame-Options",
]

COMMON_UNSTANDARD_RESPONSE_HEADERS = [
    "Content-Security-Policy",
    "X-Content-Security-Policy",
    "X-WebKit-CSP",
    "Refresh",
    "Status",
    "Timing-Allow-Origin",
    "X-Content-Duration",
    "X-Content-Type-Options",
    "X-Powered-By",
    "X-UA-Compatible",
    "X-XSS-Protection",
]



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
           # sys.exit(1)
            address=None
        return address

    def create_tcp_socket(self, ip_info, use_ipv4):
        '''Create and Connect a TCP socket'''
           
        try:
            # Build socket
            if use_ipv4==True:
                s = socket.socket(ip_info[0][0], ip_info[0][1], ip_info[0][2])
                # Set socket options
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # Allow reuse immediately after closed
                if hasattr(socket, "SO_REUSEPORT"):
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                    
            else:
                s = socket.socket(ip_info[1][0], ip_info[1][1], ip_info[1][2])
                # Set socket options
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # Allow reuse immediately after closed
                if hasattr(socket, "SO_REUSEPORT"):
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            return s 
         
        except socket.error as ex:
                error_message = str(ex)
                return None

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

    def connect_tcp_socket(self, sock, host_ip_info, host, use_ipv4, timeout):
            try: 
                error_message="" 
              
                if use_ipv4==True:            
                    sock.connect(host_ip_info[0][4])
                else:
                    sock.connect(host_ip_info[1][4]) 
                sock.settimeout(timeout)               
                stream_socket = SuperSocket.StreamSocket(sock, basecls=HTTP)
                return stream_socket, error_message
            except socket.error as ex:

                error_message = str(ex)
                return None, error_message

    def connect_tls_socket(self, tls_socket, host_ip_info, host, use_ipv4, timeout):
            try: 
                error_message=""
                if use_ipv4==True:             
                    tls_socket.connect(host_ip_info[0][4])
                else:
                    tls_socket.connect(host_ip_info[1][4])
                tls_socket.settimeout(timeout)
                assert "http/1.1" == tls_socket.selected_alpn_protocol()
                stream_socket = SuperSocket.SSLStreamSocket(tls_socket, basecls=HTTP)
                return stream_socket, error_message
            except socket.error as ex:
                print("Scoket Error")
                error_message = str(ex)
                return None, error_message

    def build_http_headers(self, host, path, headers, custom_request):
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
          #  http_headers = custom_request
            req = custom_request.encode()
        else:
            req = HTTP() / HTTPRequest(**http_headers)

        return req



    def parse_headers(self, headers_str):
        """Extract the header fields from the response"""
        response_headers = {}
        for header_line in headers_str.split('\r\n'):
            try: 
                if ':' in header_line:
                    key, value = header_line.split(':', 1)
                    header_key = key.strip().lower()
                    response_headers[header_key] = value.strip()
            except ValueError:
                continue
            
        return response_headers


    def parse_response(self, http_response):
        """Split the response into response line, headers, and body,    TRAILERS not supported"""
        response_str=str(bytes(http_response),"utf-8", errors="replace")
        crlf_firstline = response_str.find('\r\n')
        if crlf_firstline != -1:
            response_line=response_str[:crlf_firstline+2]
            headers_body=response_str[crlf_firstline+2:]
        crlfcrlfIndex = response_str.find('\r\n\r\n')
        if crlf_firstline != -1:
            headers=response_str[:crlfcrlfIndex +4]
            body=response_str[crlfcrlfIndex+4:]
        
        return response_line, headers, body


    def parse_response_line(self, response_line_str):
        #Split the line
        http_version, status_code, reason_phrase= response_line_str.split(None, 2)
        response_line = {
            "HTTP_version": http_version,
            "status_code": int(status_code),
            "reason_phrase": reason_phrase.strip(),
        }
        return response_line


    def http_request(
        self,
        host,
        use_ipv4,
        port=80,
        path="/",
        host_ip_info=None,
        timeout=3,
        #display=False,
        verbose=True,
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
 
        # DNS Lookup if info not provided, maybe delete it
        if host_ip_info is None:
            host_ip_info = self.lookup_dns(host,port)
        print(host_ip_info)
        #TODO Add IPV6 support
        req = self.build_http_headers(host, path, headers, custom_request)

        # Check
        if verbose==True:
            print(req)
          
        # Establish a socket connection
        sock = self.create_tcp_socket(host_ip_info, use_ipv4)
        
        # Upgrade to TLS depending on the port  

        if 443 == port:
            tls_socket=self.upgrade_to_tls(sock, host)
            stream_socket, error_message=self.connect_tls_socket(tls_socket, host_ip_info, host, use_ipv4, timeout)
        else:
            stream_socket, error_message=self.connect_tcp_socket(sock, host_ip_info, host, use_ipv4, timeout)
     
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
            except socket.error as ex:
                error_message=str(ex)
                response=None
            finally:
                if 443 == port:
                    tls_socket.shutdown(1)
                    stream_socket.close()
                else:
                    sock.shutdown(1)            
                    stream_socket.close()

        response_line=None
        response_headers=None
        body=None
        if response is not None:
            response_line_str, headers_str, body_str=self.parse_response(response)
            response_line= self.parse_response_line(response_line_str)
            response_headers =self.parse_headers(headers_str)
         


        return response_line, response_headers, body, response_time, error_message