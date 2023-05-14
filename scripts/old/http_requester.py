import socket
import sys
import ssl
from scapy.layers.http import *
from scapy.layers.http import HTTPResponse
import scapy.supersocket as SuperSocket
import scapy.config



def lookup_dns(hostname, portnumber):
    try:
        # Lookup IP of HTTP Endpoint
        l = socket.getaddrinfo(hostname, portnumber, socket.INADDR_ANY, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    except socket.gaierror as e:
        print(f'DNS Lookup failed: {str(e)}')
        sys.exit(1)
    
    return l
    

def create_tcp_socket(addrlist):
    # Build socket
    s = socket.socket(addrlist[0][0], addrlist[0][1], addrlist[0][2])
    # Set socket options
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Allow reuse immediately after closed
    if hasattr(socket, 'SO_REUSEPORT'):
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    return s
 
 
def upgrade_to_tls(s, hostname):
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

def extract_status_code(raw_tuple):

    headers, body = raw_tuple[0].split('\r\n\r\n', 1)
    header_lines = headers.split('\r\n')
    status_line = header_lines[0]
    status_code = int(status_line.split(' ')[1])
    return

def send_http_request(hostname, portnumber, request):
    # Enable scapy debug mode
    scapy.config.conf.debug_dissector = True    
    # Connect the socket and create a StreamSocket
    host_ip = lookup_dns(hostname, portnumber)
    ip_and_port= lookup_dns(hostname, portnumber)[0][4]
    s = create_tcp_socket(host_ip)
    # Upgrade to TLS depending on the port
    if (443==portnumber):
        tls_socket = upgrade_to_tls(s, hostname)
        #Connect Socket to TCP Endpoint
        tls_socket.connect(ip_and_port)
        assert('http/1.1' == tls_socket.selected_alpn_protocol())
        stream_socket = SuperSocket.SSLStreamSocket(tls_socket, basecls=HTTP)
    else:
        s.connect(ip_and_port)
        stream_socket = SuperSocket.StreamSocket(s, basecls=HTTP)

    # Send the HTTP request and receive the response
    stream_socket.send(request.encode())
    
    http_response = stream_socket.recv().decode()
    print(type(http_response))
    print(http_response[0])
    print(http_response[1])
    print(http_response)
    
    status_code=12#extract_status_code(http_response)
    
    print("Received status code:", status_code)

    # Close the socket
    s.close()

    # Return the status code
    return status_code
