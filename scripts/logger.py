# logger.py
# Experiment Logging Functions

import subprocess
import time
import os
import json
import csv








class TestRunLogger:
    def __init__(self, experiment_configuration, experiment_folder, target_host, target_ip, target_port):
        self.experiment_configuration = experiment_configuration
        self.experiment_folder=experiment_folder
        self.target_ip = target_ip
        self.target_port = target_port
        self.target_host =target_host
        self.log_folder = self.create_logging_folder()
        self.request_data_list=[]
        self.status_code_count= {}
        self.result_variables={}


    def create_logging_folder(self):
        '''Creates in not exists to store the logs'''
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_folder = f"{self.experiment_folder}/{timestamp}_{self.target_host}"
        os.makedirs(log_folder, exist_ok=True)
        return log_folder


    def save_run_metadata(self, result_variables):
        '''Save Meta Data connected to experiment'''
        metafile_path = f"{self.log_folder}/metafile.json"
        data = {
            "configuration_variables": self.experiment_configuration,
            "result_variables": result_variables,
        }

        with open(metafile_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        return

    def add_request_response_data(self, attempt_number, request, deviation_count, response_line, response_header_fields, body, response_time, error_message):
        if response_line is not None:
            response_http_version = response_line["HTTP_version"]
            response_status_code = response_line["status_code"]
            response_reason_phrase = response_line["reason_phrase"]
            
        else:
            response_http_version = ""
            response_status_code = 000
            response_reason_phrase = "Error"
        
                   
        request_data = {
            "number": attempt_number,
            "request": request,
            "deviation_count": deviation_count,
            "request_length": len(request),
            "http_version": response_http_version,
            "status_code": response_status_code,
            "reason_phrase": response_reason_phrase ,
            "response_time": response_time,
            "error_message": error_message,
            "response_header_fields": response_header_fields,
        }
        self.request_data_list.append(request_data)
        self.status_code_count[request_data["status_code"]] = (self.status_code_count.get(request_data["status_code"], 0) + 1)

        return    



     #TODO: better naming
    def move_tls_keys(self):
        '''Move the TLS seessionkeys to the experiment folder, they are created by the custom http client'''
        if os.path.exists("sessionkeys.txt"):
            try:
                os.rename("sessionkeys.txt", f"{self.log_folder}/sessionkeys.txt")
            except OSError as ex:
                print(f"An error occurred while moving the file: {str(ex)}")

    
    def create_wireshark_script(self):
        ''' Creates a wireshark script to easily analyze the captured packets, with the need TLS keys'''
        wireshark_cmd = [
            "wireshark",
            "-r",
            "captured_packets.pcapng",
            "-o",
            "tls.keylog_file:sessionkeys.txt",
        ]
        wireshark_script_path = f"{self.log_folder}/wireshark_script.sh"
        with open(wireshark_script_path, "w", encoding="utf-8") as file:
            file.write("#!/bin/bash\n")
            file.write(" ".join(wireshark_cmd))

        os.chmod(wireshark_script_path, 0o755)

    def logger_print():
        #TODO
        print("Status Code Counts:")
        for status_code, count in self.status_code_count.items():
            print(f"{status_code}: {count}")
    
    def save_request_data(self, request_data):
        '''Save the recorded requests'''
        log_file_path = f"{self.log_folder}/log_file.json"
        with open(log_file_path, "w", encoding="utf-8") as file:
            json.dump(request_data, file, indent=4)
    
    def create_result_variables():
        #TODO
        self.result_variables = {
            "covertchannel_request_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_request_number"]]),
            "covertchannel_request_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_connection_number"]]),
            "covertchannel_timing_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_timing_number"]]),
            "Received_Status_Codes": self.status_code_count,
            "Message_Count": 1234,
            "Share_2xx": 100.0,
            "Response_2xx": 1200,
            "Response_4xx": 30,
            "Response_Error": 4,
            #Here maybe more information would be nice, successful attempts/failures, count of successfull baseline checks, statistical data? medium response time?
        }   
        
        return self.result_variables


    def save_logfiles(self):#, request_data, result_variables):
        '''Save all files after the experiments'''
        self.save_run_metadata(self.result_variables)
        self.move_tls_keys()
        self.create_wireshark_script()
        self.save_request_data(self.request_data_list)

    def extract_pcapng():
        #TODO
        return

class ExperimentLogger:
    def __init__(self, experiment_configuration):
        self.experiment_configuration = experiment_configuration
        self.experiment_folder = self.create_experiment_folder(experiment_configuration["experiment_no"])
    
    def get_experiment_folder(self):
        return self.experiment_folder

    def create_experiment_folder(self, exp_number):
        '''Create an experiment folder, if not already exist '''
       
        exp_folder = f"logs/experiment_{exp_number}"
        os.makedirs(exp_folder, exist_ok=True) #If it already exists, doesn't care
        return exp_folder


    def add_global_entry_to_experiment_list(self, exp_no):
        """Adds an entry describing the experiment and the outcome into a list"""
        #TODO update header line when new keys are added to experiment konfiguration

        file_path = "logs/experiment_list.csv"
        exists = os.path.exists(file_path)
        
        with open(file_path, "a+", newline="") as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=self.experiment_configuration.keys())
            if not exists:
                csv_writer.writeheader()
            row = self.experiment_configuration.copy()
            csv_writer.writerow(row)
 

    def update_entry_to_experiment_list():
        """TODO add statistical data to experiment list"""

        with open(f"/logs/experiment_list.csv", "w", newline="") as csvfile:
            csv_writer=csv.writer(csvfile)
            csv_writer.writerow(["Key","Value"])
            for key,value in self.experiment_configuration:
                csv_writer.writerow([key,value])

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
        pcap_path = f"{self.experiment_folder}/captured_packets.pcapng"

        # Filter for packets related to the specific connection, host filter both directions
        #filter_expression = f"host {self.target_ip}"

        # Generate command to run Dumpcap
        dumpcap_cmd = [
            "dumpcap",
            "-i", nw_interface,
            "-w", pcap_path,
            #"-f", filter_expression,
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
    
    def extract_packets_per_host(host_list):
        return 0
