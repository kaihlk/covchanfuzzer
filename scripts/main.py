from custom_http_client import CustomHTTP
import http1_covered_channels
import mutators
import random
import threading
import subprocess
import time
import os
import json
import re
from queue import Queue


# PCAP Files
def save_logfiles(log_dir, experiment_variables, triplets_list):
    # Save Meta Data
    metafile_path = f"{log_dir}/metafile.json"
    data = {
        "experiment_variables": experiment_variables,
    }

    with open(metafile_path, "w") as file:
        json.dump(data, file, indent=4)
    # Move TLS Keys to Log Folder when present
    if os.path.exists("sessionkeys.txt"):
        try:
            os.rename("sessionkeys.txt", f"{log_dir}/sessionkeys.txt")
        except OSError as e:
            print(f"An error occurred while moving the file: {str(e)}")
    # Create Bash Script to start Wireshark with TLS KeyFile
    wireshark_cmd = [
        "wireshark",
        "-r",
        "captured_packets.pcap",
        "-o",
        f"tls.keylog_file:sessionkeys.txt",
    ]
    wireshark_script_path = f"{log_dir}/wireshark_script.sh"
    with open(wireshark_script_path, "w") as file:
        file.write("#!/bin/bash\n")
        file.write(" ".join(wireshark_cmd))

    # Add execute permission to the bash file
    os.chmod(wireshark_script_path, 0o755)

    # Save the Triplets Request, Deviation Count and Response Statuscode
    log_file_path = f"{log_dir}/log_file.json"
    with open(log_file_path, "w") as file:
        json.dump(triplets_list, file, indent=4)


# dumpcap needs less privilige than tshark and is maybe faster.
# Prerequsites:
#  sudo usermod -a -G wireshark your_username
#  sudo setcap cap_net_raw=eip $(which dumpcap)


def capture_packets_dumpcap(
    destination_ip,
    destination_port,
    host,
    log_dir,
    coveredchannel,
    stop_capture_flag,
    nw_interface="eth0",
    result_queue=None,
):
    # Set the output file for captured packets
    pcap_path = f"{log_dir}/captured_packets.pcap"

    # Filter for packets related to the specific connection, host filter both directions
    filter_expression = f"host {destination_ip}"

    # Generate command to run Dumpcap
    dumpcap_cmd = [
        "dumpcap",
        "-i",
        nw_interface,
        "-w",
        pcap_path,
        "-f",
        filter_expression,
        "-q",
    ]

    packets_captured = 0

    try:
        dumpcap_process = subprocess.Popen(
            dumpcap_cmd, stdout=subprocess.PIPE, text=True
        )

        # Wait for the HTTP response or timeout
        while not stop_capture_flag.is_set():
            # Continue capturing packets until the response is received or timeout occurs
            pass
        time.sleep(0.1)
        # If the response arrived, terminate the capturing process early
        print("End of run. Capturing terminated.")
        subprocess.run(["pkill", "dumpcap"])  # Terminate dumpcap process
        print("Packets captured and saved to", pcap_path)
        time.sleep(1)
        # When the capturing process is complete, put the captured packets count into the result queue
        output = dumpcap_process.stdout.read() + dumpcap_process.stdout.read()
        print("Here comes the output:")
        print(output)

        packet_count_pattern = r"Packets captured: (\d+)"
        match = re.search(packet_count_pattern, output)
        for line in output.splitlines():
            print("Line 1:" + line)
            match = re.search(packet_count_pattern, line)
            if match:
                packets_captured = int(match.group(1))
                break
        else:
            print("Packets captured information not found.")
        if result_queue:
            result_queue.put(packets_captured)

    except subprocess.TimeoutExpired:
        # If a timeout occurs, terminate the dumpcap process
        print("Timeout limit reached. Capturing terminated.")
        subprocess.run(["pkill", "dumpcap"])  # Terminate dumpcap process
        print("Packets captured and saved to", pcap_path)
    except subprocess.CalledProcessError as e:
        print("Error occurred during packet capture:", e)


def main():
    # Todo
    # host and channelselction, number of attempts as arguments?
    # host and channels as a file?

    # Add a cautios mode that leaves some time between requests to the same adress (Not getting caught by Denial of service counter measures)
    # Add a mode that sends a well formed request every x attempts to verify not being blocked

    # Control the body of the response as well (?)

    hosts = [
        ("localhost", 8080)
        # ('www.example.com', 443),
        # ('www.google.com', 80),
        # ('www.amazon.com', 443)
    ]

    # Select covered channel for forging the header
    covertchannel_number = 7
    # Number of attempts
    num_attempts = 100
    conn_timeout = 20.0
    nw_interface = "lo"  # "enp0s3"
    # Value to change the propability to change packets
    fuzz_value = 0.5
    # Flag if IPv4 should be used when possible

    useIPv4 = True

    for target_host, target_port in hosts:
        # Dns Lookup has to be done here  to get thark parameters
        target_ip_info = CustomHTTP().lookup_dns(target_host, target_port)
        if useIPv4:
            target_ip = target_ip_info[0][4][0]
        else:
            target_ip = target_ip_info[1][4][0]

        # Create a directory to store the logs
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_dir = f"logs/{timestamp}_{target_host}"
        os.makedirs(log_dir, exist_ok=True)

        # Inititialise dictoionaries and lists for logging
        status_code_count = {}
        request_data_list = []

        # Create a flag to stop the capturing process when the response is received
        stop_capture_flag = threading.Event()
        # Create a queue to store the result (captured packets count)
        result_queue = Queue()

        # Create an start thread for the packet capture
        capture_thread = threading.Thread(
            target=capture_packets_dumpcap,
            args=(
                target_ip,
                target_port,
                target_host,
                log_dir,
                covertchannel_number,
                stop_capture_flag,
                nw_interface,
            ),
            kwargs={"result_queue": result_queue},
        )
        capture_thread.start()

        # Time to let the packet dumper work
        time.sleep(1)

        for i in range(num_attempts):
            # Todo:   Baseline Check if Client is not blocked yet

            request, deviation_count = http1_covered_channels.forge_http_request(
                cc_number=covertchannel_number,
                host=target_host,
                port=target_port,
                url="/",
                method="GET",
                headers=None,
                fuzzvalue=fuzz_value,
            )
            # Send the HTTP request and get the response in the main thread
            response = CustomHTTP().http_request(
                host=target_host,
                port=target_port,
                host_ip_info=target_ip_info,
                customRequest=request,
            )
            response_status_code = response.Status_Code.decode("utf-8")

            # Save Data
            status_code_count[response_status_code] = (
                status_code_count.get(response_status_code, 0) + 1
            )

            request_data = {
                "Number": i,
                "request": request,
                "deviation_count": deviation_count,
                "length": len(request),
                "status_code": response_status_code,
            }
            request_data_list.append(request_data)

            # Print the response status code and deviation count
            print("Host: {}".format(target_host))
            print("Port: {}".format(target_port))
            print("Status Code: {}".format(response.Status_Code.decode("utf-8")))
            print("Deviation Count: {}\n".format(deviation_count))

        # Time to let the packet dumper work
        time.sleep(1)
        stop_capture_flag.set()
        # Wait for the capture thread to finish
        capture_thread.join()
        captured_packets_count = result_queue.get()

    print("Status Code Counts:")
    for status_code, count in status_code_count.items():
        print(f"{status_code}: {count}")

    # Save Experiment Metadata

    experiment_variables = {
        "Time Stamp": timestamp,
        "Comment": "Some text describing the Testrun",
        "covertchannel_number": covertchannel_number,
        "number_of_attempts": num_attempts,
        "fuzzvalue": fuzz_value,
        "Timeout_value": conn_timeout,
        "Networkinterface": nw_interface,
        "Use_IPv4": useIPv4,
        "Host": target_host,
        "Port": target_port,
        "Target_IP_Information": target_ip_info,
        "Used_Target_IP": target_ip,
        "Used_Target_Port": target_port,
        "log_dir": log_dir,
        "Received_Status_Codes": status_code_count,
        "Captured Packet": captured_packets_count,
    }
    ##ADD Adhoc Statistics

    save_logfiles(log_dir, experiment_variables, request_data_list)


if __name__ == "__main__":
    main()
