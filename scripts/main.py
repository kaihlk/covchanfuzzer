from custom_http import CustomHTTP
import http1_covered_channels 
import mutators
import random
import threading
import subprocess
import time
import os

#Todo
#host and channelselction, number of attempts as arguments?
#host and channels as a file?
#auto capture the packets, tls with wireshark/tshark
# Data Output: Host, port, Channel, Request Packet, Answer Status Code
#Add a mode that leaves some time between requests to the same adress (Not getting caught by Denial of service counter measures)
# Add a mode that sends a well formed request every x attempts to verify not being blocked
# Control the body of the response as well (?)

hosts = [
    ('www.example.com', 443),
   # ('www.google.com', 80),
   #('www.amazon.com', 443)
]

#dumpcap needs less privilige than tshark and is maybe faster.
# Prerequsites:
#  sudo usermod -a -G wireshark your_username
#  sudo setcap cap_net_raw=eip $(which dumpcap)
def capture_packets_dumpcap(destination_ip, destination_port, host, log_dir, coveredchannel, stop_capture_flag, timeout=20.0, nw_interface="eth0"):
    # Set the output file for captured packets
    pcap_file = f"{log_dir}/captured_packets_{host}_{coveredchannel}_{destination_ip}_{destination_port}.pcap"

    # Filter for packets related to the specific connection, host filter both directions
    filter_expression = f"host {destination_ip}"

    # Generate command to run Dumpcap
    dumpcap_cmd = [
        "dumpcap",
        "-i", nw_interface,
        "-w", pcap_file,
        "-f", filter_expression,
        ]

    try:
        # Start the dumpcap process in a separate thread
      
        dumpcap_thread = threading.Thread(target=subprocess.run, args=(dumpcap_cmd,), kwargs={"timeout": timeout})
        dumpcap_thread.start()

        # Wait for the HTTP response or timeout
        while not stop_capture_flag.is_set():
            # Continue capturing packets until the response is received or timeout occurs
            pass
        time.sleep(0.1)
        # If the response arrived, terminate the capturing process early
        print("HTTP Response received. Capturing terminated.")
        subprocess.run(["pkill", "dumpcap"])  # Terminate dumpcap process
        print("Packets captured and saved to", pcap_file)

        # Wait for the capture thread to finish
        dumpcap_thread.join()

    except subprocess.TimeoutExpired:
        # If a timeout occurs, terminate the dumpcap process
        print("Timeout limit reached. Capturing terminated.")
        subprocess.run(["pkill", "dumpcap"])  # Terminate dumpcap process
        print("Packets captured and saved to", pcap_file)
    except subprocess.CalledProcessError as e:
        print("Error occurred during packet capture:", e)



def capture_packets_tshark(destination_ip, destination_port, host, coveredchannel, timeout=20.0, nw_interface="eth0" ):

    # Set the output file for captured packets
    pcap_file = f"captured_packets_{host}_{coveredchannel}_{destination_ip}_{destination_port}.pcap"
   
    # Filter for packets related to the specific connection, host filter both direction
    filter_expression = f"host {destination_ip} and port {destination_port}"

    # Generate command to run TShark
    tshark_cmd = [
        "tshark",
        "-i", nw_interface,     
        "-w", pcap_file,
        "-f", filter_expression
    ]

     # Function to terminate the tshark process after timeout
    def terminate_capture():
        tshark_process.terminate()

    # Start tshark process
    tshark_process = subprocess.Popen(tshark_cmd, stdout=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)

    # Flag to track if complete HTTP response is found
    complete_response_found = False

    # Create a timer thread to terminate the capture after timeout
    timeout_timer = threading.Timer(timeout, terminate_capture)
    timeout_timer.start()

    # Loop through the captured packets
    for line in iter(tshark_proce.stdout.readline, ''):
        # Check if the blank line (end of HTTP response headers) is found
        if line == '\r\n':  #This needs testing
            complete_response_found = True
            break

    # Stop capturing by killing the tshark process (if not already terminated)
    tshark_proce.terminate()

    # Cancel the timeout timer
    timeout_timer.cancel()

    if complete_response_found:
        print("Complete HTTP response found. Capturing stopped.")
    else:
        print("Complete HTTP response not found. Capturing completed.")

    print(f"Packets captured and saved to {pcap_file}")



def main():

    
 # Select the method for forging the header
    covertchannel_number = 3
    # Number of attempts
    num_attempts = 10
    ok=0
    conn_timeout=20.0
    nw_interface="enp0s3"
    #Flag if IPv4 should be used when possible
    useIPv4=True

    for target_host, target_port in hosts:
        # Dns Lookup has to be done here  to get thark parameters          
        target_ip_info=CustomHTTP().lookup_dns(target_host,target_port)
        if useIPv4:
            target_ip=target_ip_info[0][4][0]
        else: target_ip=target_ip_info[1][4][0] 

        #Create a directory to store the logs
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_dir = f"logs/{timestamp}_{target_host}"
        os.makedirs(log_dir, exist_ok=True)
         # Create a flag to stop the capturing process when the response is received
        stop_capture_flag = threading.Event()

        # Start thread to capture the packets
        # Create an start thread for the packet capture
        capture_thread = threading.Thread(target=capture_packets_dumpcap, args=(target_ip, target_port, target_host, log_dir, covertchannel_number, stop_capture_flag, conn_timeout, nw_interface))
        capture_thread.start()

        for _ in range(num_attempts):
            #Todo:   Baseline Check if Client is not blocked yet
       
            request, deviation_count = http1_covered_channels.forge_http_request(cc_number=covertchannel_number, host=target_host, port=target_port, url='/', method="GET", headers=None, fuzzvalue=0.1)


           
            # Send the HTTP request and get the response in the main thread                             
            response=CustomHTTP().http_request(host=target_host, port=target_port, host_ip_info=target_ip_info, customRequest=request)
            # Set the stop_capture_flag to signal the capturing thread to stop earlier 
 

            response_status_code=response.Status_Code.decode('utf-8')


            # Print the response status code and deviation count
            print("Host: {}".format(target_host))
            print("Port: {}".format(target_port))
            print("Status Code: {}".format(response.Status_Code.decode('utf-8')))
            print("Deviation Count: {}\n".format(deviation_count))

            if response_status_code=='200':
                ok+=1
            #ToDo Save request, deviation, status_code maybe response Time? 
        stop_capture_flag.set()
        # Wait for the capture thread to finish
        capture_thread.join()

    print('Successfull packets: '+str(ok) + ' of '+str(num_attempts)+ ' attempts.')

    #TODO Create Meta Data
    # Save SSHKeys and Clean Up
    os.rename("sessionkeys.txt", f"{log_dir}/sessionkeys.txt")    

if __name__ == '__main__':
    main()
