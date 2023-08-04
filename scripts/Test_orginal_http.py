#Test of original http implementation like sugested on 
#Source: https://scapy.readthedocs.io/en/latest/layers/http.html#http-1-x
#Run with Root-Privileges
#Both ways fail due to RST packets, probably send by the OS because no known open socket
#Workaround would be firewall rules dropping outgoing TCP RST packets
#Could be done with iptables flag in the http_request
#sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -s 10.0.2.15 -j DROP

from scapy.layers.http import *

""" 
print("Way 1. Request over TCPClient")
req = HTTP()/HTTPRequest(
    Accept_Encoding=b'gzip, deflate',
    Cache_Control=b'no-cache',
    Connection=b'keep-alive',
    Host=b'www.secdev.org',
    Pragma=b'no-cache'
)
a = TCP_client.tcplink(HTTP, "www.example.com", 80, iface="enp0s3")
answer = a.sr1(req)
a.close()
with open("localhost", "wb") as file:
    file.write(answer.load) """

req = HTTP()/HTTPRequest(
    Accept_Encoding=b'gzip, deflate',
    Cache_Control=b'no-cache',
    Connection=b'keep-alive',
    Host=b'www.secdev.org',
    Pragma=b'no-cache'
)
a = TCP_client.tcplink(HTTP, "www.secdev.org", 80)
answer = a.sr1(req)
a.close()
with open("www.secdev.org.html", "wb") as file:
    file.write(answer.load)


#Alternative way, iptables rules by function
# print("Way 2:")

#http_request()

#http_request("www.example.com", "/", iptables=True)
#http_request("www.example.com", "/", display=True)
