# logger.py
# Experiment Logging Functions

import subprocess
import time
import os
import json


class ExperimentLogger:
    def __init__(self, experiment_configuration, target_ip, target_port):
        self.experiment_configuration = experiment_configuration
        self.target_ip = target_ip
        self.target_port = target_port
        self.log_dir = self.create_logging_folder(experiment_configuration["target_host"])


    def create_logging_folder(self, target_host):
        '''Create a directory to store the logs'''
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_dir = f"logs/{timestamp}_{target_host}"
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    
    def save_experiment_metadata(self, result_variables):
        '''Save Meta Data connected to experiment'''
        metafile_path = f"{self.log_dir}/metafile.json"
        data = {
            "configuration_variables": self.experiment_configuration,
            "result_variables": result_variables,
        }

        with open(metafile_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def move_tls_keys(self):
        '''Move the TLS seessionkeys to the experiment folder, they are created by the custom http client'''
        if os.path.exists("sessionkeys.txt"):
            try:
                os.rename("sessionkeys.txt", f"{self.log_dir}/sessionkeys.txt")
            except OSError as ex:
                print(f"An error occurred while moving the file: {str(ex)}")

    def create_wireshark_script(self):
        ''' Creates a wireshark script to easily analyze the captured packets, with the need TLS keys'''
        wireshark_cmd = [
            "wireshark",
            "-r",
            "captured_packets.pcap",
            "-o",
            "tls.keylog_file:sessionkeys.txt",
        ]
        wireshark_script_path = f"{self.log_dir}/wireshark_script.sh"
        with open(wireshark_script_path, "w", encoding="utf-8") as file:
            file.write("#!/bin/bash\n")
            file.write(" ".join(wireshark_cmd))

        os.chmod(wireshark_script_path, 0o755)

    def save_request_data(self, request_data):
        '''Save the recorded requests'''
        log_file_path = f"{self.log_dir}/log_file.json"
        with open(log_file_path, "w", encoding="utf-8") as file:
            json.dump(request_data, file, indent=4)
    
    def save_logfiles(self, request_data, result_variables):
        '''Save all files after the experiments'''
        self.save_experiment_metadata(result_variables)
        self.move_tls_keys()
        self.create_wireshark_script()
        self.save_request_data(request_data)

    def capture_packets_dumpcap(
        self,
        stop_capture_flag,
        nw_interface="eth0",
    ):
        '''Function to start a dumpcap network packet capturing process to record the traffic to and from a specified host'''
        # PCAP Files
        # dumpcap needs less privilige than tshark and is maybe faster.
        # Prerequsites:
        #  sudo usermod -a -G wireshark your_username
        #  sudo setcap cap_net_raw=eip $(which dumpcap)
        # Consider if destination port is need or if it is a problem when the connection is updated to TLS

        # Set the output file for captured packets
        pcap_path = f"{self.log_dir}/captured_packets.pcap"

        # Filter for packets related to the specific connection, host filter both directions
        filter_expression = f"host {self.target_ip}"

        # Generate command to run Dumpcap
        dumpcap_cmd = [
            "dumpcap",
            "-i", nw_interface,
            "-w", pcap_path,
            "-f", filter_expression,
            "-q",
        ]

        try:
            subprocess.Popen(dumpcap_cmd)
            # Wait for stop flag
            while not stop_capture_flag.is_set():
                # Continue capturing packets until the response is received or timeout occurs
                pass
            time.sleep(1)
            # If the response arrived, terminate the capturing process early
            print("End of run. Capturing terminated.")
            subprocess.run(["pkill", "dumpcap"], check=False)  # Terminate dumpcap process      
            print("Packets captured and saved to", pcap_path)       
            time.sleep(1)

        except subprocess.TimeoutExpired:
            # If a timeout occurs, terminate the dumpcap process
            print("Timeout limit reached. Capturing terminated.")
            subprocess.run(["pkill", "dumpcap"], check=False)  # Terminate dumpcap process
            print("Process 'dumpcap' was successfully terminated.")
            print("Packets captured and saved to", pcap_path)
        
        except subprocess.CalledProcessError as ex:
            print("Error occurred during packet capture:", ex)
