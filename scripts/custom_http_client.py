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
    

    def lookup_dns(self, hostname, portnumber, use_ipv4):
        '''Function to make a DNS Lookup for a specified host or localhost using sockets and return the received data as a dictionary of tuples ''' 
        address=None
        if hostname.lower() == "localhost":
            hostname = "127.0.0.1"
        try:
            # Lookup IP of HTTP Endpoint
                if use_ipv4:
                    family=socket.AF_INET
                else:
                    family=socket.AF_INET6
                address = socket.getaddrinfo(
                    hostname,
                    portnumber,
                    family,
                    socket.SOCK_STREAM,
                    socket.IPPROTO_TCP,
                )
        except socket.gaierror as ex:
            print(f"DNS Lookup failed: {str(ex)}")
            return address, str(ex)
        return address, None

    def create_tcp_socket(self, ip_info, timeout):
        '''Create and Connect a TCP socket'''
        timeout_ms = int(timeout * 1000)   
        try:
            # Build socket
            s = socket.socket(ip_info[0][0], ip_info[0][1], ip_info[0][2])   
            # Set socket options
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.settimeout(timeout)
            #Allow reuse immediately after closed
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            if hasattr(socket, "SO_REUSEPORT"):
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            return s        
        except socket.error as ex:
            error_message = str(ex)
            print(error_message)
            return None
        

    def upgrade_to_tls(self, s, hostname, log_path):
        '''Upgrade a tcp socket connection to TLS'''          
        # Testing support for ALPN
        assert ssl.HAS_ALPN
        # Building the SSL context
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.load_verify_locations("/etc/ssl/certs/ca-certificates.crt")
        # Export Sessionkeys, to be able to analyze encrypted Traffic with Wireshark etc.
        ssl_ctx.keylog_filename = f"{log_path}/sessionkeys.txt"
        ssl_ctx.set_alpn_protocols(["http/1.1"])  # h2 is a RFC7540-hardcoded value
        ssl_sock = ssl_ctx.wrap_socket(s, server_hostname=hostname)
        return ssl_sock

    def connect_tcp_socket(self, sock, host_ip_info, timeout):
            try: 
                error_message="" 
                #print("Host IP Info")
                #print(host_ip_info[0][4])
                sock.settimeout(timeout)   #Can be reset by some functions of the socket libary, just to make sure          
                sock.connect(host_ip_info[0][4])
                stream_socket = SuperSocket.StreamSocket(sock, basecls=HTTP)

                return stream_socket, error_message
            except socket.error as ex:
                error_message = str(ex)
                return None, error_message

    def connect_tls_socket(self, tls_socket, host_ip_info, timeout):
            try: 
                error_message=""
                tls_socket.settimeout(timeout)
                #print("Host IP Info")
               #print(host_ip_info[0][4])
                tls_socket.connect(host_ip_info[0][4])
                tls_socket.settimeout(timeout)
                #assert "http/1.1" == tls_socket.selected_alpn_protocol()  # Assert Error Problem with saving log to json
                stream_socket = SuperSocket.SSLStreamSocket(tls_socket, basecls=HTTP)
                return stream_socket, error_message
            except socket.error as ex:
                error_message = str(ex)
                print(error_message)
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
            crlfcrlfIndex = headers_body.find('\r\n\r\n')
            if crlfcrlfIndex != -1:
                headers=headers_body[:crlfcrlfIndex +4]
                body=headers_body[crlfcrlfIndex+4:]
            else:
                headers = headers_body
                body=""
        
        return response_line, headers, body


    def parse_response_line(self, response_line_str):
        
        parts = response_line_str.split(None, 2)   #WIKIMEDIDA did not send reason phrase, cause crash
        #Split the line 
        if len(parts)==3:
            http_version, status_code, reason_phrase=parts
            response_line = {
                "HTTP_version": http_version,
                "status_code": int(status_code),
                "reason_phrase": reason_phrase.strip(),
            }
        elif len(parts)==2:
            http_version, status_code=parts
            response_line = {
                "HTTP_version": http_version,
                "status_code": int(status_code),
                "reason_phrase": "",
            }
        else:
            raise ValueError("Invalid Response Line")    
        return response_line


    def http_request(
        self,
        host,
        use_ipv4,
        log_path,
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
        stream_socket=None
        
        socket_connect_time=0
        response_time=0
        socket_close_time=0
        error_messages=[]


        # DNS Lookup if info not provided, maybe delete it
        #if host_ip_info is None:
        #    host_ip_info = self.lookup_dns(host,port)
        #print(host_ip_info)
        #TODO Add IPV6 support
        
        req = self.build_http_headers(host, path, headers, custom_request)
 
        # Check
        if verbose==True:
            print(req)
            print(host_ip_info)
        
        try: 
            # Establish a socket connection
            start_time=time.time() 
            sock = self.create_tcp_socket(host_ip_info, timeout) 
            # Upgrade to TLS depending on the port  
            if 443 == port:
                tls_socket=self.upgrade_to_tls(sock, host, log_path)
                stream_socket, error_message=self.connect_tls_socket(tls_socket, host_ip_info, timeout)
            else:
                stream_socket, error_message=self.connect_tcp_socket(sock, host_ip_info, timeout)
            end_time = time.time()
            socket_connect_time=end_time-start_time
            error_messages.append(error_message)
            if verbose==True:
                print("Stream Socket Connection Time")
                print(socket_connect_time)
        except Exception as ex0:
            print("An error occurred:", ex0)
            error_messages.append(ex0)            
            if 'tls_socket' in locals():
                #tls_socket.shutdown(1)
                tls_socket.close()
            if 'sock' in locals():
                #sock.shutdown(1)
                sock.close()
            if 'stream_socket' in locals() and stream_socket is not None:
                stream_socket.close()
     
        if stream_socket is not None:
            try:
                # Send the request over the socket               
                start_time=time.time()
                stream_socket.send(req)       
                # Receive the response
                response = stream_socket.recv()
                
                end_time = time.time()
                response_time=end_time-start_time
                print("Response Time")
                print(response_time)
            except socket.timeout as ex1:
                #error_message="Timeout Limit reached"
                error_messages.append(str(ex1))
                print(ex1)
                response = None
            except socket.error as ex2:
                error_messages.append(str(ex2))
                print(ex2)
                response=None
            finally:
                
                start_time=time.time()
                try:
                    if 443 == port:
                      #  tls_socket.shutdown(1)
                        time.sleep(0.1)
                        stream_socket.close()
                    else:
                       # sock.shutdown(1)
                        time.sleep(0.1) #Preventing RST Packets           
                        stream_socket.close()
                    end_time = time.time()
                    socket_close_time=end_time-start_time
                    if verbose==True:
                        print("Socket close time")
                        print(socket_close_time)
                except socket.error as ex3:
                    error_messages.append(str(ex3))
                    print(ex3)
                    pass

        
        response_line=None
        response_headers=None
        body=None
        if response is not None:
            response_line_str, headers_str, body_str=self.parse_response(response)

            response_line= self.parse_response_line(response_line_str)
            response_headers =self.parse_headers(headers_str)
            body=body_str
         
        measured_times= {
            "Socket_Connect_Time": socket_connect_time,
            "Socket_Close_Time": socket_close_time,
            "Response_Time": response_time,

        }

   
        return response_line, response_headers, body, measured_times, error_messages