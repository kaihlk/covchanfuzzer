# logger.py
# Experiment Logging Functions

import subprocess
import time
import os
import json
import csv
import class_mapping
# import pyshark # doesnt work so well, probably a sudo problem







class TestRunLogger:
    def __init__(self, experiment_configuration, experiment_folder, host_ip_info, target_host, target_ip, target_port):
        self.experiment_configuration = experiment_configuration
        self.experiment_folder=experiment_folder
        self.host_ip_info=host_ip_info
        self.target_ip = target_ip
        self.target_port = target_port
        self.target_host =target_host
        self.log_folder = self.create_logging_folder()
        self.request_data_list=[]
        self.status_code_count= {}
        self.result_variables={}
        self.capture=None
        self.logged_attempts=0

    def create_logging_folder(self):
        '''Creates in not exists to store the logs'''
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_folder = f"{self.experiment_folder}/{timestamp}_{self.target_host}"
        os.makedirs(log_folder, exist_ok=True)
        return log_folder
    def get_logging_folder(self):
        return self.log_folder

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

    def add_request_response_data(self, attempt_number, request, deviation_count, response_line, response_header_fields, body, measured_times, error_message):
        if response_line is not None:
            response_http_version = response_line["HTTP_version"]
            response_status_code = response_line["status_code"]
            response_reason_phrase = response_line["reason_phrase"]
            
        else:
            response_http_version = ""
            response_status_code = "000"
            response_reason_phrase = error_message
        
                   
        request_data = {
            "number": attempt_number,
            "request": request,
            "deviation_count": deviation_count,
            "request_length": len(request),
            "http_version": response_http_version,
            "status_code": response_status_code,
            "reason_phrase": response_reason_phrase,
            "measured_times": measured_times,
            "error_message": error_message,
            "response_header_fields": response_header_fields,
        }
        self.request_data_list.append(request_data)
        self.status_code_count[request_data["status_code"]] = (self.status_code_count.get(request_data["status_code"], 0) + 1)
        self.logged_attempts+=1
        return    


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
            file.write('script_dir="$(dirname "$0")"\n')
            file.write('cd "$script_dir" || exit 1\n')       
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
    
    def create_result_variables(self):
        #TODO
        codes_count = sum(self.status_code_count.values())
        status_code_ranges = {
            '1xx': range(100, 200),
            '2xx': range(200, 300),
            '3xx': range(300, 400),
            '4xx': range(400, 500),
            '5xx': range(500, 600),
            '000': [0]  # Socket Errors
        }
        status_code_distribution = {}
        for status_range, code_range in status_code_ranges.items():
            count = sum(self.status_code_count.get(code, 0) for code in code_range)
            if codes_count > 0:
                status_code_distribution[status_range] = count / codes_count * 100 
            else:
                status_code_distribution[status_range]=0

        self.result_variables = {
            "host_ip_info": self.host_ip_info,
            "covertchannel_request_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_request_number"]]),
            "covertchannel_request_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_connection_number"]]),
            "covertchannel_timing_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_timing_number"]]),
            "Received_Status_Codes": self.status_code_count,
            "Logged_Messages": self.logged_attempts,
            "Logged_Messages_of_scheduled_attempts": self.logged_attempts/self.experiment_configuration["num_attempts"],
            "Distribution_of_status_codes": status_code_distribution,
            #Here maybe more information would be nice, successful attempts/failures, count of successfull baseline checks, statistical data? medium response time?
        }   
        
        return self.result_variables


    def save_logfiles(self):#, request_data, result_variables):
        '''Save all files after the experiments'''
        self.create_result_variables()
        self.save_run_metadata(self.result_variables)

        self.create_wireshark_script()
        self.save_request_data(self.request_data_list)
        

    def capture_packets(
        self,
        stop_capture_flag
    ):
        '''Function to start a dumpcap network packet capturing process to record the traffic to and from a specified host'''
        # PCAP Files
        # dumpcap needs less privilige than tshark and is maybe faster.
        # Prerequsites:
        #  sudo usermod -a -G wireshark your_username
        #  sudo setcap cap_net_raw=eip $(which dumpcap)
        # Consider if destination port is need or if it is a problem when the connection is updated to TLS
        """ PYSHARK ALTERNATIV IS NOT WORKING
        # Set the output file for captured packets
        pcap_path = f"{self.log_folder}/captured_packets.pcapng"
        #Filter host Address
        filter_host= f"host {self.target_ip}"
        self.capture=pyshark.LiveCapture(interface=self.experiment_configuration["nw_interface"], capture_filter=filter_host, output_file=pcap_path)
        print("Capturing started, Pcapng saved to: "+pcap_path)
        while not stop_capture_flag.is_set():
            # Continue capturing packets until the stop flag is set
            pass

        if self.capture:
            print("capture close")
            self.capture.close()
        return """
    
        # Filter for packets related to the specific connection, host filter both directions
        filter_expression = f"host {self.target_ip}"
        pcap_path = f"{self.log_folder}/captured_packets.pcapng"
        # Generate command to run Dumpcap
        dumpcap_cmd = [
            "dumpcap",
            "-i", self.experiment_configuration["nw_interface"],
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
            
            # If the response arrived, terminate the capturing process early
            print("End of run. Capturing terminated.")
            subprocess.run(["pkill", "dumpcap"], check=False)  # Terminate dumpcap process      
            print("Packets captured and saved to", pcap_path)       
            

        except subprocess.TimeoutExpired:
            # If a timeout occurs, terminate the dumpcap process
            print("Timeout limit reached. Capturing terminated.")
            subprocess.run(["pkill", "dumpcap"], check=False)  # Terminate dumpcap process
            print("Process 'dumpcap' was successfully terminated.")
            print("Packets captured and saved to", pcap_path)
        
        except subprocess.CalledProcessError as ex:
            print("Error occurred during packet capture:", ex)
        return

        def capture_thread():
            try:
                self.capture.apply_on_packets(self.packet_handler, timeout=1)
            except KeyboardInterrupt:
                pass

        capture_thread = threading.Thread(target=capture_thread)
        capture_thread.start()

        while not stop_capture_flag.is_set():
            time.sleep(1)

        print("End of run. Capturing terminated.")
        self.capture.close()

        print("Packets captured and saved to", pcap_path)
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