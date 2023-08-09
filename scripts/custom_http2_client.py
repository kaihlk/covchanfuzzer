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
from scapy.all import *  
import scapy.supersocket as SuperSocket
import scapy.contrib.http2 as h2
import scapy.config
import scapy.packet as packet

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

class H2Settings:
    def __init__(self):
        self.header_table_size = 4096 #S ETTINGS_HEADER_TABLE_SIZE (0x1): Allows the sender to inform the remote endpoint of the maximum size of the header compression table used to decode header blocks, in octets. Standardvalue 4096
        self.enable_push = 0 # SETTINGS_ENABLE_PUSH (0x02):This setting can be used to enable or disable server push. A server MUST NOT send a PUSH_PROMISE frame if it receives this parameter set to a value of 0;
        self.max_concurrent_streams = 100 # SETTINGS_MAX_CONCURRENT_STREAMS (0x03): This setting indicates the maximum number of concurrent streams that the sender will allow. Value greater 100 suggested
        self.intial_window_size = 1 << 12 # SETTINGS_INITIAL_WINDOW_SIZE (0x4): Strame Level Flow Control Initial Value 2^16-1 (65,535))
        self.max_frame_size = 1 << 14 # SETTINGS_MAX_FRAME_SIZE (0x5): Indicates the size of the largest frame payload that the sender is willing to receive, in octets. Initial Value 2^14 (16,384), must between Initila Value and max allowed framesize 2^24-1 or 16,777,215 octets
        self.max_header_list_size = 1 << 14 # SETTINGS_MAX_HEADER_LIST_SIZE (0x6):s This advisory setting informs a peer of the maximum size of header list that the sender is prepared to accept, in octets.  The value is based on the uncompressed size of header fields, including the length of the name and value in octets plus an overhead of 32 octets for each header field.

    def build_setting_frame(self):
        own_set = h2.H2Frame()/h2.H2SettingsFrame()
        own_set.settings = [
            h2.H2Setting(id = h2.H2Setting.SETTINGS_HEADER_TABLE_SIZE, value = self.header_table_size ),
            h2.H2Setting(id = h2.H2Setting.SETTINGS_ENABLE_PUSH, value = self.enable_push ),
            h2.H2Setting(id = h2.H2Setting.SETTINGS_MAX_CONCURRENT_STREAMS, value = self.max_concurrent_streams),
            h2.H2Setting(id = h2.H2Setting.SETTINGS_INITIAL_WINDOW_SIZE, value=self.intial_window_size),
            h2.H2Setting(id = h2.H2Setting.SETTINGS_MAX_FRAME_SIZE, value=self.max_frame_size ),
            h2.H2Setting(id = h2.H2Setting.SETTINGS_MAX_HEADER_LIST_SIZE, value=self.max_header_list_size),
        ]
        return own_set

    def update_settings(self, setting_frame):
        for setting in setting_frame.payload.settings:
            if setting.id == h2.H2Setting.SETTINGS_HEADER_TABLE_SIZE: #0x01
                self.header_table_size = setting.value
            elif setting.id ==h2.H2Setting.SETTINGS_ENABLE_PUSH: #0x02
                self.enable_push = setting.value
            elif setting.id == h2.H2Setting.SETTINGS_MAX_CONCURRENT_STREAMS: #0x03
                self.max_concurrent_streams_streams= setting.value
            elif setting.id == h2.H2Setting.SETTINGS_INITIAL_WINDOW_SIZE: #0x04
                self.intial_window_size = setting.value
            elif setting.id == h2.H2Setting.SETTINGS_MAX_FRAME_SIZE: #0x05
                self.max_frame_size = setting.value    
            elif setting.id == h2.H2Setting.SETTINGS_MAX_HEADER_LIST_SIZE:#0x06
                self.max_header_list_size = setting.value
        return self.build_setting_frame()

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
        except socket.error as ex:
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
        ssl_ctx.set_alpn_protocols(["h2"])  # h2 is a RFC7540-hardcoded value
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
                stream_socket = SuperSocket.StreamSocket(sock, basecls=h2.H2Frame)
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
                assert "h2" == tls_socket.selected_alpn_protocol()
                stream_socket = SuperSocket.SSLStreamSocket(tls_socket, basecls=h2.H2Frame)
                return stream_socket, error_message
            except socket.error as ex:
                error_message = str(ex)
                return None, error_message



    def connect_h2(self, ss):
        #Server may send immidiatley a Setting Frame?
        settings=H2Settings()
        #Step 1 RFC9113: Client sends Connection Preface
        #Preface: "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
        #http2_preface = b'\x50\x52\x49\x20\x2a\x20\x48\x54\x54\x50\x2f\x32\x2e\x30\x0d\x0a\x0d\x0a\x53\x4d\x0d\x0a\x0d\x0a'
        ss.send(h2.H2_CLIENT_CONNECTION_PREFACE)

        #Step2: Clients sends Settings Frame (may be empty)
        own_setting_frame=H2Settings().build_setting_frame()
        ss.send(own_setting_frame)

        #Step2a: Curls send Window Update and Get right afterwards
        #Step3: Receive Setting Frame from Server


        # Loop until an acknowledgement for our settings is received
        new_frame = None
        while isinstance(new_frame, type(None)) or not (
                new_frame.type == h2.H2SettingsFrame.type_id 
                and 'A' in new_frame.flags
            ):
            if not isinstance(new_frame, type(None)):
                # If we received a frame about window management 
                if new_frame.type == h2.H2WindowUpdateFrame.type_id:
                    # For this tutorial, we don't care about stream-specific windows, but we should :)
                    if new_frame.stream_id == 0:
                        settings.intial_window_size += new_frame.payload.win_size_incr
                # If we received a Ping frame, we acknowledge the ping, 
                # just by setting the ACK flag (A), and sending back the query
                elif new_frame.type == h2.H2PingFrame.type_id:
                    new_flags = new_frame.getfieldval('flags')
                    new_flags.add('A')
                    new_frame.flags = new_flags
                    srv_global_window -= len(str(new_frame))
                    assert(srv_global_window >= 0)
                    ss.send(new_frame)
                else:
                    assert new_frame.type != h2.H2ResetFrame.type_id \
                        and new_frame.type != h2.H2GoAwayFrame.type_id, \
                        "Error received; something is not right!"
            try:
                new_frame = ss.recv()
                print("new_frame:")
                new_frame.show()
            except:
                import time
                time.sleep(1)
                new_frame = None
        print("Client Settings send and ack")
        return settings


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
        port=443,
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
  
        # Upgrade to TLS 
        tls_socket=self.upgrade_to_tls(sock, host)
        stream_socket, error_message=self.connect_tls_socket(tls_socket, host_ip_info, host, use_ipv4, timeout)
    

        
        
        ##Handling the Reqeust Updata Later
        if stream_socket is not None:
            try:
                # Connect H2
                settings=self.connect_h2(stream_socket)
                tblhdr = h2.HPackHdrTable()
                request=b":method GET\r\n:path /\r\n:authority www.example.com\r\n:scheme https\r\naccept-encoding: gzip, deflate\r\naccept-language: fr-FR\r\naccept: text/html\r\nuser-agent: Scapy HTTP/2 Module\r\n"
                
                qry_frontpage = tblhdr.parse_txt_hdrs(
                    request,
                    stream_id=1,
                    max_frm_sz=settings.max_frame_size,
                    max_hdr_lst_sz=settings.max_header_list_size,
                    is_sensitive=lambda hdr_name, hdr_val: hdr_name in ['cookie'],
                    should_index=lambda x: x in [
                            'x-requested-with', 
                            'user-agent', 
                            'accept-language',
                            ':authority',
                            'accept',
                        ]
                )
                print("Query:")
                qry_frontpage.show()
                # Send the request over the socket               
               #start_time=time.time()
                stream_socket.send(qry_frontpage.frames[0])
                print("Gesendet!!!")
                stream = h2.H2Seq()
                # Number of streams closed by the server
                closed_stream = 0

                new_frame = None
                while True:
                    if not isinstance(new_frame, type(None)):
                        if new_frame.stream_id in [1, 3]:
                            stream.frames.append(new_frame)
                            if 'ES' in new_frame.flags:
                                closed_stream += 1
                        # If we read a PING frame, we acknowledge it by sending the same frame back, with the ACK flag set.
                        elif new_frame.stream_id == 0 and new_frame.type == h2.H2PingFrame.type_id:
                            new_flags = new_frame.getfieldval('flags')
                            new_flags.add('A')
                            new_frame.flags = new_flags
                            stream_socket.send(new_frame)
                            
                        # If two streams were closed, we don't need to perform the next operations
                        if closed_stream >= 1:
                            break
                    try:
                        new_frame = stream_socket.recv()
                        new_frame.show()
                    except:
                        import time
                        time.sleep(1)
                        new_frame = None

                stream.show()
                srv_tblhdr = h2.HPackHdrTable(dynamic_table_max_size=settings.header_table_size, dynamic_table_cap_size=settings.header_table_size)
                #Structure used to store textual representation of the stream headers
                stream_txt = {}
                # Structure used to store data from each stream
                stream_data = {}

                # For each frame we previously received
                for frame in stream.frames:
                    # If this frame is a header
                    if frame.type == h2.H2HeadersFrame.type_id:
                        # Convert this header block into its textual representation.
                        # For the sake of simplicity of this tutorial, we assume 
                        # that the header block is not large enough to require a Continuation frame
                        stream_txt[frame.stream_id] = srv_tblhdr.gen_txt_repr(frame)
                    # If this frame is data
                    if frame.type == h2.H2DataFrame.type_id:
                        if frame.stream_id not in stream_data:
                            stream_data[frame.stream_id] = []
                        stream_data[frame.stream_id].append(frame)
                print(stream_txt[1])
                #end_time = time.time()
                #response_time=end_time-start_time
                import zlib
                data = b''
                for frgmt in stream_data[1]:
                    data += frgmt.payload.data
                html=zlib.decompress(data, 16+zlib.MAX_WBITS).decode('UTF-8', 'ignore')
                print(html)
                #from IPython.core.display import HTML
                #HTML(zlib.decompress(data, 16+zlib.MAX_WBITS).decode('UTF-8', 'ignore'))
            except socket.timeout:
                error_message="Timeout Limit reached"
                response = None
            except socket.error as ex:
                error_message=str(ex)
                response=None
            finally:
                # Close the socket
                    print("Finally")
                    tls_socket.shutdown(1)
                    stream_socket.close()

        response_line=None
        response_headers=None
        body=None
        if response is not None:
            response_line_str, headers_str, body_str=self.parse_response(response)
            response_line= self.parse_response_line(response_line_str)
            response_headers =self.parse_headers(headers_str)
         


        return response_line, response_headers, body, response_time, error_message


#Testing:
experiment_configuration = {
        "comment": "H2 Test",
        "covertchannel_request_number": 4,
        "covertchannel_connection_number": 1,
        "covertchannel_timing_number": 1,
        "content": "random",  #"random", "some_text"  
        "num_attempts": 100,
        "wait_between_request": 0,
        "base_line_check_frequency": 0,
        "conn_timeout": 0.5,
        "nw_interface": "lo",#"enp0s3",  #lo, docker, enp0s3
        "fuzz_value": 0.9,
        "use_ipv4": True,
        "use_TLS": False,
        "target_host": "www.example.com",
        "target_port": 443, #443, 8080 Apache
        "method" : "GET",
        "url": "/",
        "headers": None,
        "standard_headers": "firefox_HTTP/1.1",  #curl_HTTP/1.1(TLS), firefox_HTTP/1.1, firefox_HTTP/1.1_TLS, chromium_HTTP/1.1, chromium_HTTP/1.1_TLS"
        "verbose": True,    
}

response_line, response_header_fields, body, response_time, error_message  = CustomHTTP().http_request(
            host=experiment_configuration["target_host"],
            use_ipv4=experiment_configuration["use_ipv4"],
            port=experiment_configuration["target_port"],
            host_ip_info=None,
            custom_request="LALLALA",
            timeout=experiment_configuration["conn_timeout"],
            verbose=experiment_configuration["verbose"],
        )