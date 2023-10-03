from scapy.all import *
import socket   
import ssl
import scapy.supersocket as supersocket
import scapy.contrib.http2 as h2
import scapy.config
import time
import scapy.packet as packet


domainname="www.amazon.com"
portnumber=443

##Building Socket

#Lookup  IP of  HTTP Endpoint
l = socket.getaddrinfo(domainname, portnumber, socket.INADDR_ANY, socket.SOCK_STREAM, socket.IPPROTO_TCP)
assert len(l) > 0, 'DNS Lookup failed'

#Build socket 
s = socket.socket(l[0][0], l[0][1], l[0][2])
#Set socket options
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#Allow reuse immediatly after closed
if hasattr(socket, 'SO_REUSEPORT'):
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)


#????????????????
s.settimeout(1)

#Print fetched Adress 
ip_and_port = l[0][4]
print('IP and Port of ' + domainname + ' is: ')
print(ip_and_port)


##Building TLS Context (Scapys's HTTP/2 Notebook uses TLS 1.2 and older Version off ssl)
if 443==portnumber:

	# Testing support for ALPN
	assert(ssl.HAS_ALPN)

	# Building the SSL context,latest protocol verison

	ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT) 
    #ssl_ctx.load_defult_certs(purpose=Purpose.SERVER_AUTH)?ß??

	ssl_ctx.load_verify_locations("/etc/ssl/certs/ca-certificates.crt")


    #Export the Session Key for later analysis
	ssl_ctx.keylog_filename="sessionkeys.txt"

	ssl_ctx.set_alpn_protocols(['h2'])  # h2 is a RFC7540-hardcoded value
	ssl_sock = ssl_ctx.wrap_socket(s, server_hostname=domainname)

	#Connect Socket to TCP Endpoint
	ssl_sock.connect(ip_and_port)
	assert('h2' == ssl_sock.selected_alpn_protocol())     
	#TODO ADD VERBOSE
	print(ssl_sock.version())
	print(ssl_sock.context)
	print(ssl_sock.server_hostname)
    #?
	scapy.config.conf.debug_dissector = True
	ss = supersocket.SSLStreamSocket(ssl_sock, basecls=h2.H2Frame)

####Not from original scapy HTTP/2 Notebook
####Some servers send their setting frames directly after establishing the TLS Connection (i.e. amazon.com)
####While others expect the client to send the HTTP/2 Preface (google.com)
#Preface: "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
#http2_preface = b'\x50\x52\x49\x20\x2a\x20\x48\x54\x54\x50\x2f\x32\x2e\x30\x0d\x0a\x0d\x0a\x53\x4d\x0d\x0a\x0d\x0a'
#http2C Preface: PRI * HTTP/2.0\r\n\r\nH2C\r\n\r\n
#h2cpreface = b'\x50\x52\x49\x20\x2a\x20\x48\x54\x54\x50\x2f\x32\x2e\x30\x0d\x0a\x0d\x0a\x48\x32\x43\x0d\x0a\x0d\x0a' #
#ss.send(h2.H2_CLIENT_CONNECTION_PREFACE)




try:
    srv_set = ss.recv()
    print("Server Settings received!")
except socket.timeout:
    print("Server settings frame not received within the timeout. Sending preface.")
    ss.send(h2.H2_CLIENT_CONNECTION_PREFACE)
    srv_set = ss.recv()


# h2c is not so easy to implement, delete ?
    #elif 80==portnumber:
 #   scapy.config.conf.debug_dissector = True
   # s.connect(ip_and_port)
  #  print("Test S Connect")
   # ss= supersocket.StreamSocket(s, basecls=h2.H2Frame)
   # ss.send(h2cpreface) 
   # ss.send(packet.Raw(h2.H2SettingsFrame()))
#TODO ADD Verbose
print("srv_set.show:")
srv_set.show()

###TODO check, comment understand RFC7540
#Define Standard Values
print("Assigning own values")
srv_hdr_tbl_sz = 4096 #SETTINGS_HEADER_TABLE_SIZE (0x1): Allows the sender to inform the remote endpoint of the maximum size of the header compression table used to decode header blocks, in octets. Standardvalue 4096
srv_ena_push = 0 # SETTINGS_ENABLE_PUSH (0x02):This setting can be used to enable or disable server push. A server MUST NOT send a PUSH_PROMISE frame if it receives this parameter set to a value of 0;
srv_max_con_streams = 101 #SETTINGS_MAX_CONCURRENT_STREAMS (0x03): This setting indicates the maximum number of concurrent streams that the sender will allow. Value greater 100 suggested
srv_global_window = 1<<12 #SETTINGS_INITIAL_WINDOW_SIZE (0x4): Strame Level Flow Control Initial Value 2^16-1 (65,535))
srv_max_frm_sz = 1<<14    #SETTINGS_MAX_FRAME_SIZE (0x5): Indicates the size of the largest frame payload that the sender is willing to receive, in octets. Initial Value 2^14 (16,384), must between Initila Value and max allowed framesize 2^24-1 or 16,777,215 octets
srv_max_hdr_list_sz = 1<<14 #   SETTINGS_MAX_HEADER_LIST_SIZE (0x6):s This advisory setting informs a peer of the maximum size of header list that the sender is prepared to accept, in octets.  The value is based on the uncompressed size of header fields, including the length of the name and value in octets plus an overhead of 32 octets for each header field.


###WHY NOT FRAMESZE???
#SET Serversettings  ADD All possible settings from the RFC 9113  Scapy Doc lacks of some
for setting in srv_set.payload.settings:
    if setting.id == h2.H2Setting.SETTINGS_HEADER_TABLE_SIZE: #0x01
        srv_hdr_tbl_sz = setting.value
    elif setting.id ==h2.H2Setting.SETTINGS_ENABLE_PUSH: #0x02
        srv_ena_push= setting.value
    elif setting.id == h2.H2Setting.SETTINGS_MAX_CONCURRENT_STREAMS: #0x03
        srv_max_con_streams= setting.value
    elif setting.id == h2.H2Setting.SETTINGS_INITIAL_WINDOW_SIZE: #0x04
        srv_global_window = setting.value
    elif setting.id == h2.H2Setting.SETTINGS_MAX_FRAME_SIZE: #0x05
        srv_max_frm_sz = setting.value    
    elif setting.id == h2.H2Setting.SETTINGS_MAX_HEADER_LIST_SIZE:#0x06
        srv_max_hdr_list_sz = setting.value

print("Settings:")
print(setting)

# We verify that the server window is large enough for us to send some data.
srv_global_window -= len(h2.H2_CLIENT_CONNECTION_PREFACE)
assert(srv_global_window >= 0)
""" print(h2.H2_CLIENT_CONNECTION_PREFACE)"""
ss.send(h2.H2_CLIENT_CONNECTION_PREFACE) 
set_ack = h2.H2Frame(flags={'A'})/h2.H2SettingsFrame()
set_ack.show()

#Receive Window Update
window_update_frame=ss.recv()
window_update_frame.show()


print("acknowledge")

own_set = h2.H2Frame()/h2.H2SettingsFrame()
hdr_tbl_sz = srv_hdr_tbl_sz#4096
ena_push = srv_ena_push#0
max_con_streams =  srv_max_con_streams#101
global_window = srv_global_window+window_update_frame.payload.win_size_incr#(1 << 16) - 1
max_frm_sz = srv_max_frm_sz#(1 << 16) - 1
max_hdr_list_sz = srv_max_hdr_list_sz +1#( 1 << 16) - 1

own_set.settings = [
    h2.H2Setting(id = h2.H2Setting.SETTINGS_HEADER_TABLE_SIZE, value = hdr_tbl_sz),
    h2.H2Setting(id = h2.H2Setting.SETTINGS_ENABLE_PUSH, value = ena_push),
    h2.H2Setting(id = h2.H2Setting.SETTINGS_MAX_CONCURRENT_STREAMS, value = max_con_streams),
    h2.H2Setting(id = h2.H2Setting.SETTINGS_INITIAL_WINDOW_SIZE, value=global_window),
    h2.H2Setting(id = h2.H2Setting.SETTINGS_MAX_FRAME_SIZE, value=max_frm_sz),
    h2.H2Setting(id = h2.H2Setting.SETTINGS_MAX_HEADER_LIST_SIZE, value=max_hdr_list_sz),
]

h2seq = h2.H2Seq()
h2seq.frames = [
    set_ack,
    own_set
]
time.sleep(1)
# We verify that the server window is large enough for us to send our frames.
srv_global_window -= len(str(h2seq))
assert(srv_global_window >= 0)

ss.send(h2seq)

print("Test")

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
                srv_global_window += new_frame.payload.win_size_incr
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
        new_frame.show()
    except:
        import time
        time.sleep(1)
        new_frame = None

        
ss.close()