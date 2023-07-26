from custom_http import CustomHTTP
import http1_covered_channels 
import mutators
import random
import threading
import subprocess
import time
import os
import json



# PCAP Files 
def save_logfiles(log_dir, experiment_variables, triplets_list):
    
    #Save Meta Data
    metafile_path=f"{log_dir}/metafile.json"
    data = {
        "experiment_variables": experiment_variables,    
    }

    with open(metafile_path, "w") as file:
        json.dump(data, file, indent=4)
    #Move TLS Keys to Log Folder
    os.rename("sessionkeys.txt", f"{log_dir}/sessionkeys.txt")    
    # Create Bash Script to start Wireshark with TLS KeyFile
    wireshark_cmd = ["wireshark", "-r", "captured_packets.pcap", "-o", f"tls.keylog_file:sessionkeys.txt"]
    wireshark_script_path = f"{log_dir}/wireshark_script.sh"
    with open(wireshark_script_path, "w") as file:
        file.write("#!/bin/bash\n")
        file.write(" ".join(wireshark_cmd))

    # Add execute permission to the bash file
    os.chmod(wireshark_script_path, 0o755)

    #Save the Triplets Request, Deviation Count and Response Statuscode
    log_file_path = f"{log_dir}/log_file.json"
    with open(log_file_path, "w") as file:
        json.dump(triplets_list, file, indent=4)




#dumpcap needs less privilige than tshark and is maybe faster.
# Prerequsites:
#  sudo usermod -a -G wireshark your_username
#  sudo setcap cap_net_raw=eip $(which dumpcap)

def capture_packets_dumpcap(destination_ip, destination_port, host, log_dir, coveredchannel, stop_capture_flag, nw_interface="eth0"):
    # Set the output file for captured packets
    pcap_path = f"{log_dir}/captured_packets.pcap"

    # Filter for packets related to the specific connection, host filter both directions
    filter_expression = f"host {destination_ip}"

    # Generate command to run Dumpcap
    dumpcap_cmd = [
        "dumpcap",
        "-i", nw_interface,
        "-w", pcap_path,
        "-f", filter_expression,
        "-q",
        ]

    try:
        # Start the dumpcap process in a separate thread
      
        dumpcap_thread = threading.Thread(target=subprocess.run, args=(dumpcap_cmd,))#, kwargs={"timeout": timeout})
        dumpcap_thread.start()

        # Wait for the HTTP response or timeout
        while not stop_capture_flag.is_set():
            # Continue capturing packets until the response is received or timeout occurs
            pass
        time.sleep(0.1)
        # If the response arrived, terminate the capturing process early
        print("End of run. Capturing terminated.")
        subprocess.run(["pkill", "dumpcap"])  # Terminate dumpcap process
        print("Packets captured and saved to", pcap_path)

        # Wait for the capture thread to finish
        dumpcap_thread.join()

    except subprocess.TimeoutExpired:
        # If a timeout occurs, terminate the dumpcap process
        print("Timeout limit reached. Capturing terminated.")
        subprocess.run(["pkill", "dumpcap"])  # Terminate dumpcap process
        print("Packets captured and saved to", pcap_path)
    except subprocess.CalledProcessError as e:
        print("Error occurred during packet capture:", e)

def main():
    #Todo
    #host and channelselction, number of attempts as arguments?
    #host and channels as a file?
    
    # Add a cautios mode that leaves some time between requests to the same adress (Not getting caught by Denial of service counter measures)
    # Add a mode that sends a well formed request every x attempts to verify not being blocked
    
    # Control the body of the response as well (?)

    hosts = [
        ('www.example.com', 443),
    # ('www.google.com', 80),
    #('www.amazon.com', 443)
    ]
    
    # Select covered channel for forging the header
    covertchannel_number = 3
    # Number of attempts
    num_attempts = 10
    conn_timeout=20.0
    nw_interface="enp0s3"
    #Value to change the propability to change packets
    fuzz_value=0.5
    #Flag if IPv4 should be used when possible
    
    useIPv4=True
    
    #Inititialise dictoionaries and lists for logging
    status_code_count = {}
    triplets_list = []

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

        # Create an start thread for the packet capture
        capture_thread = threading.Thread(target=capture_packets_dumpcap, args=(target_ip, target_port, target_host, log_dir, covertchannel_number, stop_capture_flag, nw_interface))
        capture_thread.start()

        #Time to let the packet dumper work
        time.sleep(1)

        for _ in range(num_attempts):
            #Todo:   Baseline Check if Client is not blocked yet
       
            request, deviation_count = http1_covered_channels.forge_http_request(cc_number=covertchannel_number, host=target_host, port=target_port, url='/', method="GET", headers=None, fuzzvalue=fuzz_value)    
            # Send the HTTP request and get the response in the main thread                             
            response=CustomHTTP().http_request(host=target_host, port=target_port, host_ip_info=target_ip_info, customRequest=request)            
            response_status_code=response.Status_Code.decode('utf-8')

            #Save Data
            status_code_count[response_status_code] = status_code_count.get(response_status_code, 0) + 1

            triplet = {
            "request": request,
            "deviation_count": deviation_count,
            "status_code": response_status_code
            }
            triplets_list.append(triplet)
            
            # Print the response status code and deviation count
            print("Host: {}".format(target_host))
            print("Port: {}".format(target_port))
            print("Status Code: {}".format(response.Status_Code.decode('utf-8')))
            print("Deviation Count: {}\n".format(deviation_count))

        #Time to let the packet dumper work
        time.sleep(1)
        stop_capture_flag.set()
        # Wait for the capture thread to finish
        capture_thread.join()

    
    print("Status Code Counts:")
    for status_code, count in status_code_count.items():
        print(f"{status_code}: {count}")

    #TODO Create Meta Data
    experiment_variables = {
        'Time Stamp': timestamp,
        "Comment": "Some text describing the Testrun",
        "covertchannel_number": covertchannel_number,
        "number_of_attempts": num_attempts,
        "fuzzvalue": fuzz_value,
        "timeout_value": conn_timeout,
        "networkinterface": nw_interface,
        "use_IPv4": useIPv4,
        "host": target_host,
        "port": target_port,
        "Target_IP_Information": target_ip_info,
        "Used_Target_IP": target_ip,
        "Used_Target_Port": target_port,
        "log_dir": log_dir,
        "Received_Status_Codes": status_code_count,
    }
    
    save_logfiles(log_dir, experiment_variables, triplets_list)   
   
if __name__ == '__main__':
    main()
