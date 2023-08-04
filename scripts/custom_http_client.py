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
            print(address)
        except socket.gaierror as ex:
            print(f"DNS Lookup failed: {str(ex)}")
            sys.exit(1)
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
            return s 
        except socket.error as ex:
                print("Error Socket")
                print("Error Socket")
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

    def connect_tls_socket(self, sock, host_ip_info, host, use_ipv4, timeout):
            try: 
                error_message=""
                tls_socket = self.upgrade_to_tls(sock, host)
                if use_ipv4==True:             
                    sock.connect(host_ip_info[0][4])
                else:
                    sock.connect(host_ip_info[1][4])
                sock.settimeout(timeout)
                assert "http/1.1" == tls_socket.selected_alpn_protocol()
                stream_socket = SuperSocket.SSLStreamSocket(tls_socket, basecls=HTTP)
                return stream_socket, error_message
            except socket.error as ex:
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

    

    def extract_response_headers(self, http_response):
        """Extract the header fields from the response"""
        if http_response is not None:
            response_str=str(bytes(http_response),"utf-8", errors="replace") #due to type HTTP
            accept_ranges_pattern= re.compile(r'Accept-Ranges:\s+(.*?)\r\n')
            age_pattern= re.compile(r'Age:\s+(.*?)\r\n')
            cache_control_pattern = re.compile(r'Cache-Control:\s+(.*?)\r\n')
            content_encoding_pattern = re.compile(r'Content-Encoding:\s+(.*?)\r\n')
            content_length_pattern = re.compile(r'Content-Length:\s+(.*?)\r\n')
            content_type_pattern = re.compile(r'Content-Type:\s+(.*?)\r\n')
            date_pattern = re.compile(r'Date:\s+(.*?)\r\n')
            etag_pattern = re.compile(r'Etag:\s+"(.*?)"\r\n')
            expires_pattern = re.compile(r'Expires:\s+(.*?)\r\n')
            last_modified_pattern = re.compile(r'Last-Modified:\s+(.*?)\r\n')
            location_pattern = re.compile(r'Location:\s+(.*?)\r\n')
            server_pattern = re.compile(r'Server:\s+(.*?)\r\n')
            x_cache_pattern = re.compile(r'X-Cache:\s+(.*?)\r\n')
            
            response_header_fields = {
            "Accept-Ranges": accept_ranges_pattern.search(response_str).group(1) if accept_ranges_pattern.search(response_str) else "header field not found",
            "Age": age_pattern.search(response_str).group(1) if age_pattern.search(response_str) else "header field not found",
            "Cache-Control": cache_control_pattern.search(response_str).group(1) if cache_control_pattern.search(response_str) else "header field not found",
            "Content-Encoding": content_encoding_pattern.search(response_str).group(1) if content_encoding_pattern.search(response_str) else "header field not found",
            "Content-Length": content_length_pattern.search(response_str).group(1) if content_length_pattern.search(response_str) else "header field not found",
            "Content-Type": content_type_pattern.search(response_str).group(1) if content_type_pattern.search(response_str) else "header field not found",
            "Date": date_pattern.search(response_str).group(1) if date_pattern.search(response_str) else "header field not found",
            "E-Tag": etag_pattern.search(response_str).group(1) if etag_pattern.search(response_str) else "header field not found",
            "Expires": expires_pattern.search(response_str).group(1) if expires_pattern.search(response_str) else "header field not found",
            "Last-Modified": last_modified_pattern.search(response_str).group(1) if last_modified_pattern.search(response_str) else "header field not found",
            "Location": location_pattern.search(response_str).group(1) if location_pattern.search(response_str) else "header field not found",
            "Server": server_pattern.search(response_str).group(1) if server_pattern.search(response_str) else "header field not found",
            "X-Cache": x_cache_pattern.search(response_str).group(1) if x_cache_pattern.search(response_str) else "header field not found",
            
            }   
        else: return None
        return response_header_fields

    

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
            host_ip_info = self.lookup_dns(host, port)

        #TODO Add IPV6 support
        req = self.build_http_headers(host, path, headers, custom_request)

        # Check
        if verbose==True:
            print(req)
        
        
        # Establish a socket connection
        sock = self.create_tcp_socket(host_ip_info, use_ipv4)
        
        # Upgrade to TLS depending on the port  
        #    
        
        # Upgrade to TLS depending on the port  
        #    
        if 443 == port:
            stream_socket, error_message=self.connect_tls_socket(sock, host_ip_info, host, use_ipv4, timeout)
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
                # Close the socket
                if 443 == port:
                    tls_socket.shutdown(1)
                    stream_socket.close()
                else:
                    sock.shutdown(1)            
                    stream_socket.close()
        
        response_header_fields=self.extract_response_headers(response)
       
        return response, response_time, error_message, response_header_fields