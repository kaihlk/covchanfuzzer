# logger.py
# Experiment Logging Functions

import subprocess
import time
import os
import json
import csv
import class_mapping
import math
import pandas
import scipy.stats as scistats
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
        self.logged_attempts=0
        self.data_count={
            "Messages": 0,
            "1xx": 0,
            "2xx": 0,
            "3xx": 0,
            "4xx": 0,
            "5xx": 0,
            "9xx": 0,
       
        }
        self.reponse_time_list=[]
        self.request_length_list=[]
        self.uri_length_list=[]
        self.deviation_count_list=[]
        self.response_header_keys_list=[]
        self.response_body_list=[]
        self.deviation_to_status_code=[]

    def create_logging_folder(self):
        '''Creates in not exists to store the logs'''
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_folder = f"{self.experiment_folder}/{timestamp}_{self.target_host}"
        os.makedirs(log_folder, exist_ok=True)
        return log_folder
    def get_logging_folder(self):
        return self.log_folder

    def save_run_metadata(self, result_variables, statistics):
        '''Save Meta Data connected to experiment'''
        metafile_path = f"{self.log_folder}/metafile.json"
        data = {
            "configuration_variables": self.experiment_configuration,
            "result_variables": result_variables,
            "statistics": statistics,
        }

        with open(metafile_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        return



    def add_request_response_data(self, attempt_number, request, deviation_count, uri, response_line, response_header_fields, body, measured_times, error_message):
        if response_line is not None:
            response_http_version = response_line["HTTP_version"]
            response_status_code = response_line["status_code"]
            response_reason_phrase = response_line["reason_phrase"]
            
        else:
            response_http_version = ""
            response_status_code = 999
            response_reason_phrase = error_message
        
        if body is None:
            length_body=0
        else:
            length_body=len(body)
        
        if response_header_fields is None:
            length_header=0
        else: 
            length_header=len(response_header_fields.items())
                   
        request_data = {
            "number": attempt_number,
            "request": request,
            "deviation_count": deviation_count,
            "uri":uri,
            "request_length": len(request),
            "http_version": response_http_version,
            "status_code": response_status_code,
            "reason_phrase": response_reason_phrase,
            "measured_times": measured_times,
            "error_message": error_message,
            "response_header_fields": response_header_fields,
            "response_length": length_body
        }
        self.request_data_list.append(request_data)
        self.status_code_count[request_data["status_code"]] = (self.status_code_count.get(request_data["status_code"], 0) + 1)
        self.logged_attempts+=1
        self.data_count["Messages"]+=1
        first_digit = str(response_status_code)[0]
        if first_digit == "1":
            self.data_count["1xx"]+=1
        elif first_digit == "2":
            self.data_count["2xx"]+=1
        elif first_digit == "3":
            self.data_count["3xx"]+=1
        elif first_digit == "4":
            self.data_count["4xx"]+=1
        elif first_digit == "5":
            self.data_count["5xx"]+=1
        elif first_digit== "9":
            self.data_count["9xx"]+=1

        dev_to_status= {"Attempt No.": attempt_number, "Deviation Count": deviation_count, "Status Code": response_status_code}
  
        self.deviation_to_status_code.append(dev_to_status) 
        
        self.reponse_time_list.append(measured_times["Response_Time"])
        self.deviation_count_list.append(deviation_count)
        self.request_length_list.append(len(request))
        self.uri_length_list.append(len (uri))
        self.response_header_keys_list.append(length_header)
        self.response_body_list.append(length_body)
            
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

    def save_deviation_status_code(self, data):
        log_file_path = f"{self.log_folder}/deviation-statuscode.csv"
        data_frame=pandas.DataFrame(data)
        data_frame.to_csv(log_file_path)
        return data_frame

    
    def calcluate_avg(self,value_list):
        if len(value_list)==0:
            avg=0
        else:
            avg=sum(value_list)/len(value_list)
        return avg
    
    def calculate_standard_deviation(self, value_list):
        #Sum of differences
        if len(value_list)==0:
            standard_deviation=0
            avg=0
        else:
            avg=sum(value_list)/len(value_list)
            squared_difference_sum=0.0
            for value in value_list:
                squared_difference_sum+=(value-avg)**2
            variance=squared_difference_sum / len(value_list)
            std_deviation=math.sqrt(variance)
        return std_deviation
    
    def calculate_statistics(self, data_frame):
        statistics={}
        if self.data_count["Messages"]==0:  #Prevent division by zero
            return statistics
        else:
            grouped = data_frame.groupby("Deviation Count")
            #Build a crosstabele for every combination
            crosstable = grouped["Status Code"].value_counts().unstack().fillna(0)
            chi2, p, _, _ = scistats.chi2_contingency(crosstable)

            statistics= {
                "Host": self.target_host,
                "IP": self.target_ip,
                "IPv4": self.experiment_configuration["use_ipv4"],
                "TLS": self.experiment_configuration["use_TLS"],
                "HTTP/2": self.experiment_configuration["use_HTTP2"],
                "Messages Send": self.data_count["Messages"],    
                "1xx": self.data_count["1xx"]/self.data_count["Messages"]*100,
                "2xx": self.data_count["2xx"]/self.data_count["Messages"]*100,
                "3xx": self.data_count["3xx"]/self.data_count["Messages"]*100,
                "4xx": self.data_count["4xx"]/self.data_count["Messages"]*100,
                "5xx": self.data_count["5xx"]/self.data_count["Messages"]*100,
                "9xx": self.data_count["9xx"]/self.data_count["Messages"]*100,
                "Avg Response Time": self.calcluate_avg(self.reponse_time_list),
                "StdD Response Time": self.calculate_standard_deviation(self.reponse_time_list),
                "Avg Deviation Count": self.calcluate_avg(self.deviation_count_list),
                "StdD Deviation Count": self.calculate_standard_deviation(self.deviation_count_list),
                "Avg Request Length": self.calcluate_avg(self.request_length_list),
                "StdD Request Length": self.calculate_standard_deviation(self.request_length_list),
                "Avg URI Length": self.calcluate_avg(self.uri_length_list),
                "StdD URI Length": self.calculate_standard_deviation(self.uri_length_list),
                "Avg Response Header Keys":self.calcluate_avg(self.response_header_keys_list),
                "StdD Response Header Keys": self.calculate_standard_deviation(self.response_header_keys_list),
                "Avg Response Body Length": self.calcluate_avg(self.response_body_list),
                "StdD Response Body Length": self.calculate_standard_deviation(self.response_body_list),
                "CHI2 Test Deviation-Statuscode": chi2,
                "CHI2 Test p": p,
            }
        
        return statistics    
    
    def create_result_variables(self):
    

        self.result_variables = {
            "host_ip_info": self.host_ip_info,
            "covertchannel_request_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_request_number"]]),
            "covertchannel_request_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_connection_number"]]),
            "covertchannel_timing_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_timing_number"]]),
            "Received_Status_Codes": self.status_code_count,
            "Logged_Messages": self.logged_attempts,
            "Logged_Messages_of_scheduled_attempts": self.logged_attempts/self.experiment_configuration["num_attempts"],
            #Here maybe more information would be nice, successful attempts/failures, count of successfull baseline checks, statistical data? medium response time?
            "Response Properties": self.data_count,
        }   
        
        return self.result_variables


    def update_entry_to_experiment_list(self, statistics):
        file_path = f"{self.experiment_folder}/experiment_stats.csv"
        exists = os.path.exists(file_path)
        
        with open(file_path, "a+", newline="") as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=statistics.keys())
            if not exists:
                csv_writer.writeheader()
            row = statistics.copy()
            csv_writer.writerow(row)
        
        
        return

    def save_logfiles(self):#, request_data, result_variables):
        '''Save all files after the experiments'''
        self.create_result_variables()
        data_frame=self.save_deviation_status_code(self.deviation_to_status_code)
        statistics= self.calculate_statistics(data_frame)
        self.save_run_metadata(self.result_variables, statistics)
        self.update_entry_to_experiment_list(statistics)
        self.create_wireshark_script()
        self.save_request_data(self.request_data_list)
        
        """ PYSHARK ALTERNATIV IS NOT WORKING
        # Set the output file for captured packets
        pcap_path = f"{self.log_folder}/captured_packets.pcapng"
        #Filter host Address
        filter_host= f"host {self.target_ip}"
        self.capture=pyshark.LiveCapture(interface=self.experiment_configuration["nw_interface"], capture_filter=filter_host, output_file=pcap_path)
        print("Capturing started, Pcapng saved to: "+pcap_path)
        while no termntinue capturing packets until the stop flag is set
            pass

        if self.capture:
            print("capture close")
            self.capture.close()
        return """
    def capture_packets(
        self, stop_event
    ):
        '''Function to start a dumpcap network packet capturing process to record the traffic to and from a specified host'''
        # PCAP Files
        # dumpcap needs less privilige than tshark and is maybe faster.
        # Prerequsites:
        #  sudo usermod -a -G wireshark your_username
        #  sudo setcap cap_net_raw=eip $(which dumpcap)
        # Consider if destination port is need or if it is a problem when the connection is updated to TLS

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
            while not stop_event.is_set():
                # Continue capturing packets until the response is received or timeout occurs
                pass
            
            # If the response arrived, terminate the capturing process early
            print("End of run. Capturing terminated.")
            subprocess.run(["pkill", "dumpcap"], check=False)  # Terminate dumpcap process
            #capture_process.terminate()
            #capture_process.wait()
            #subprocess.run(["pkill", "dumpcap"], check=False)  # Terminate dumpcap process      
            print("Packets captured and saved to", pcap_path)       
            

        except subprocess.TimeoutExpired:
            # If a timeout occurs, terminate the dumpcap process
            print("Timeout limit reached. Capturing terminated.")
            subprocess.run(["pkill", "dumpcap"], check=False)  # Terminate dumpcap process
            print("Process 'dumpcap' was successfully terminated.")
            print("Packets captured and saved to", pcap_path)
        
        except subprocess.CalledProcessError as ex:
            print("Error occurred during packet capture:", ex)
        
        return True

        """  def capture_thread():
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
        return """

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
    
    def save_dns_fails(self, dns_fails):
        """Adds an entry describing the experiment and the outcome into a list"""
        file_path = f"{self.experiment_folder}/dns_lookup_fails.csv"            
        with open(file_path, "a+", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            for entry in dns_fails:
                csv_writer.writerow([entry])
        print("DNS Lookup Fails Saved")
        return

    def save_prerequests(self, prerequests):
        """Saves the prerequest list"""
        
        file_path = f"{self.experiment_folder}/prerequests.csv"
        
        with open(file_path, "w", newline="") as csvfile:
            
            csv_writer = csv.DictWriter(csvfile, fieldnames=prerequests[0].keys())
            csv_writer.writeheader()

            for prerequest in prerequests:
                csv_writer.writerow(prerequest)
        print("Prerequest saved")
        return

    def analyze_prerequest_outcome(self):
        file_path = f"{self.experiment_folder}/prerequests.csv"
        data_frame = pandas.read_csv(file_path)
        grouped = data_frame.groupby('deviation_count')[['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']].sum().reset_index()
        chi2, p, _, _ = scistats.chi2_contingency(grouped)
        log_file_path = f"{self.experiment_folder}/prerequest_stats.json"
        data={"CHI2": chi,"p": p,}
        with open(log_file_path, "w", encoding="utf-8") as file:
            json.dump(request_data, file, indent=4)
        return

    def capture_packets_dumpcap(
        self, stop_capture_flag
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
            "-i", self.experiment_configuration["nw_interface"],
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
            print("Packets of all communication captured and saved to", pcap_path)       
            time.sleep(1)

        except subprocess.TimeoutExpired:
            # If a timeout occurs, terminate the dumpcap process
            print("Timeout limit reached. Capturing terminated.")
            subprocess.run(["pkill", "dumpcap"], check=False)  # Terminate dumpcap process
            print("Process 'dumpcap' was successfully terminated.")
            
        
        except subprocess.CalledProcessError as ex:
            print("Error occurred during packet capture:", ex)
        return True
    def extract_packets_per_host(host_list):
        return 0