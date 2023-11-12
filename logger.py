# logger.py
# Experiment Logging Functions

import subprocess
import time
import os
import json
import csv
import class_mapping
import shutil
import math
import pandas
import scipy.stats as scistats
import logging
from http1_request_builder import HTTP1_Request_Builder
import itertools
# import pyshark # doesnt work so well, probably a sudo problem







class TestRunLogger:
    def __init__(self, experiment_configuration, experiment_folder, host_ip_info, target_host, target_ip, target_port, target_paths, base_uri):
        self.experiment_configuration = experiment_configuration
        self.experiment_folder=experiment_folder
        self.host_ip_info=host_ip_info
        self.target_ip = target_ip
        self.target_port = target_port
        self.target_host =target_host
        self.target_paths=target_paths
        self.base_uri=base_uri
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
        self.request_response_data_list=[]
        self.rel_uri_stats=[]

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

    def rel_uri_count(self, new_uri, status_code, deviation_count, attempt_no):
        row={}
        host=self.target_host
        original_uri= self.base_uri
        
        #Calc Relative Deviation
        letter_count = sum(1 for char in new_uri if char.isalpha())
        rel_deviation = (deviation_count / letter_count) * 100

        #Check if URI Parts are changed
        o_scheme, o_subdomains, o_hostname, o_tldomain, _port, o_path = HTTP1_Request_Builder().parse_host(original_uri)
        n_scheme, n_subdomains, n_hostname, n_tldomain, _port, n_path = HTTP1_Request_Builder().parse_host(new_uri)
        if o_scheme!=n_scheme: scheme_mod=1
        else: scheme_mod=0
        if o_subdomains!=n_subdomains: subdomain_mod=1
        else: subdomain_mod=0
        if o_hostname!=n_hostname: hostname_mod=1 
        else: hostname_mod=0
        if o_tldomain!=n_tldomain: tlddomain_mod=1 
        else: tlddomain_mod=0
        if o_path!=n_path: path_mod=1 
        else: path_mod=0
        row['Attempt_No']=attempt_no
        row['Host'] = host
        row['Original_URI'] = original_uri
        row['New_URI'] = new_uri
        row['Status_Code'] = status_code
        row['Deviation_Count'] = deviation_count
        row['Letter_Count'] = letter_count
        row['Relative_Deviation'] = rel_deviation
        row['Scheme_Modification'] = scheme_mod
        row['Subdomain_Modification'] = subdomain_mod
        row['Hostname_Modification'] = hostname_mod
        row['Tlddomain_Modification'] = tlddomain_mod
        row['Path_Modification'] = path_mod

        self.rel_uri_stats.append(row)

        return 

      

    def add_request_response_data(self, attempt_number, request, deviation_count, uri, response_line, response_header_fields, body, measured_times, error_message):
        """Save as csv."""
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
            count_header_fields=0
            length_header=0
        else: 
            count_header_fields=len(response_header_fields.items())
            length_header=len(response_header_fields)
                   
        request_data = {
            "number": attempt_number,
            "request": request,
            "deviation_count": deviation_count,
            "uri":uri,
            "request_length": len(request),
            "http_version": response_http_version,
            "Socket_Connect_Time": measured_times["Socket_Connect_Time"],
            "Socket_Close_Time": measured_times["Socket_Close_Time"],
            "Response_Time": measured_times["Response_Time"],            
            "status_code": response_status_code,
            "reason_phrase": response_reason_phrase,
            "error_message": error_message,
            "response_header_count": count_header_fields,
            "response_header_length": length_header,
            "response_body_length": length_body,
            "response_header_fields": json.dumps(response_header_fields),
            
        }
        self.request_data_list.append(request_data)
        request_response_data={
            "number": attempt_number,
            "request": request,
            "deviation_count": deviation_count,
            "uri":uri,
            "request_length": len(request),
            "Response_Time": measured_times["Response_Time"],            
            "status_code": response_status_code,
            "reason_phrase": response_reason_phrase,
            "error_message": error_message,
            "response_header_count": count_header_fields,
            "response_header_length": length_header,
            "response_body_length": length_body,
            "response_header_fields": response_header_fields,
            
        }

        self.request_response_data_list.append(request_response_data)
        
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

        dev_to_status= {
            "Attempt No.": attempt_number,
            "uri":uri, 
            "Deviation Count": deviation_count, 
            "Status Code": response_status_code, 
            "Response_Time": measured_times["Response_Time"],
            "response_header_count": count_header_fields,
            "response_header_length": length_header,
            "response_body_length": length_body,
            "response_header_fields": response_header_fields, }

    

        self.deviation_to_status_code.append(dev_to_status) 
        
        self.reponse_time_list.append(measured_times["Response_Time"])
        self.deviation_count_list.append(deviation_count)
        self.request_length_list.append(len(request))
        self.uri_length_list.append(len (uri))
        self.response_header_keys_list.append(length_header)
        self.response_body_list.append(length_body)
        self.rel_uri_count(uri, response_status_code, deviation_count, attempt_number)
        return    

    """ def add_request_response_data(self, attempt_number, request, deviation_count, uri, response_line, response_header_fields, body, measured_times, error_message):
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
            
        return     """


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
    
    def save_request_response_data(self, request_response_data):
        '''Save the recorded requests'''
        log_file_path = f"{self.log_folder}/request_response.json"
        with open(log_file_path, "w", encoding="utf-8") as file:
            json.dump(request_response_data, file, indent=4)

    def save_request_data(self, request_data):
        '''Save the recorded requests'''
        log_file_path = f"{self.log_folder}/log_file.csv"
        with open(log_file_path, "w", newline="") as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=request_data[0].keys())
            csv_writer.writeheader()

            for request in request_data:
                csv_writer.writerow(request)
        print("Request log file.csv saved")
    
    def save_deviation_status_code(self, data):
        log_file_path = f"{self.log_folder}/deviation-statuscode.csv"
        data_frame=pandas.DataFrame(data)
        data_frame.to_csv(log_file_path)
        return data_frame

    def save_rel_uri_status_code(self, data):
        log_file_path = f"{self.log_folder}/rel_uri_deviation.csv"
        data_frame=pandas.DataFrame(data)
        data_frame.to_csv(log_file_path)

        data_frame['Modification_ID'] = (
            data_frame['Scheme_Modification'] * 10000 +
            data_frame['Subdomain_Modification'] * 1000 +
            data_frame['Hostname_Modification'] * 100 +
            data_frame['Tlddomain_Modification'] * 10 +
            data_frame['Path_Modification']).astype(str)

        data_frame['1xx'] = data_frame['Status_Code'].astype(str).str.startswith('1').astype(int)
        data_frame['2xx'] = data_frame['Status_Code'].astype(str).str.startswith('2').astype(int)
        data_frame['3xx'] = data_frame['Status_Code'].astype(str).str.startswith('3').astype(int)
        data_frame['4xx'] = data_frame['Status_Code'].astype(str).str.startswith('4').astype(int)
        data_frame['5xx'] = data_frame['Status_Code'].astype(str).str.startswith('5').astype(int)
        data_frame['9xx'] = data_frame['Status_Code'].astype(str).str.startswith('9').astype(int)



        rel_deviation_stats = data_frame.groupby(data_frame['Relative_Deviation'].astype(int) // 1 * 1).agg({
            '1xx': 'sum', '2xx': 'sum', '3xx': 'sum', '4xx': 'sum', '5xx': 'sum', '9xx': 'sum'
        })

        rel_deviation_stats['Count'] = rel_deviation_stats[['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']].sum(axis=1)

        for code in ['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']:
            rel_deviation_stats[code + '_Percentage'] = (rel_deviation_stats[code] / rel_deviation_stats['Count']) * 100

        # Calculate statistics for each Modification value
        modification_stats = data_frame.groupby('Modification_ID').agg({
            '1xx': 'sum', '2xx': 'sum', '3xx': 'sum', '4xx': 'sum', '5xx': 'sum', '9xx': 'sum'
        })
        modification_stats['Count'] = modification_stats[['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']].sum(axis=1)
        for code in ['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']:
            modification_stats[code + '_Percentage'] = (modification_stats[code] / modification_stats['Count']) * 100

        log_file_path = f"{self.log_folder}/rel_uri_statuscode_stats.csv"
        rel_deviation_stats.to_csv(log_file_path)
        #log_file_path = f"{self.log_folder}/rel_uri_statuscode_freq_stats.csv"
        #rel_freq_stats_percentage.to_csv(log_file_path)
        log_file_path = f"{self.log_folder}/rel_uri_modification_type_stats.csv"
        modification_stats.to_csv(log_file_path)

        header = ['Host'] + [i for i in range(101)]
        percentage_dict = {key: 0 for key in header}
        # Set the 'Host' value
        percentage_dict['Host'] = self.target_host
       
        for index, row in rel_deviation_stats.iterrows():
            percentage_dict[index] = row['2xx_Percentage']
        file_path = f"{self.experiment_folder}/rel_uri_host_2xx.csv"
        exists = os.path.exists(file_path)

        with open(file_path, "a+", newline="") as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=percentage_dict.keys())
            if not exists:
                csv_writer.writeheader()
            row = percentage_dict.copy()
            csv_writer.writerow(row)
        

        header_mod = ['Host'] + ['0','1','10','11','100','101','110','111','1000','1001','1010','1011','1100','1101','1110','1111','10000', '10001','10010','10011','10100','10101','10110','10111','11000','11001','11010','11011','11100','11101','11110','11111']
        percentage_dict_mod = {key: 0 for key in header_mod}
         # Set the 'Host' value
        percentage_dict_mod['Host'] = self.target_host
        
        for index, row in modification_stats.iterrows():
            percentage_dict_mod[index] = row['2xx_Percentage']
        file_path = f"{self.experiment_folder}/rel_mod_uri_host_2xx.csv"
        exists = os.path.exists(file_path)

        with open(file_path, "a+", newline="") as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=percentage_dict_mod.keys())
            if not exists:
                csv_writer.writeheader()
            row = percentage_dict_mod.copy()
            csv_writer.writerow(row)

        return
    

        
        return data_frame,rel_deviation_stats, modification_stats

    
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
            "paths": self.target_paths,
            "covertchannel_request_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_request_number"]]),
            "covertchannel_connection_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_connection_number"]]),
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
        self.save_rel_uri_status_code(self.rel_uri_stats)
        statistics= self.calculate_statistics(data_frame)
        self.save_run_metadata(self.result_variables, statistics)
        self.update_entry_to_experiment_list(statistics)
        self.create_wireshark_script()
        self.save_request_data(self.request_data_list)
        self.save_request_response_data(self.request_response_data_list)
        
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
    def __init__(self, experiment_configuration, global_log_folder):
        self.experiment_configuration = experiment_configuration
        self.experiment_folder = self.create_experiment_folder(experiment_configuration["experiment_no"], global_log_folder)
        self.experiment_stats={}
        self.exp_logging=logging.getLogger("main.runner.exp_log")
        self.global_log_folder=global_log_folder
       
    
    def get_experiment_folder(self):
        return self.experiment_folder

    def create_experiment_folder(self, exp_number, global_log_folder):
        '''Create an experiment folder, if not already exist '''
       
        exp_folder = f"{global_log_folder}/experiment_{exp_number}"
        os.makedirs(exp_folder, exist_ok=True) #If it already exists, doesn't care
        os.makedirs(exp_folder+"/base_request", exist_ok=True)
        return exp_folder

    def get_directory_size_mb(self,path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        return total_size/(1024*1024)

    def add_global_entry_to_experiment_list(self, exp_no):
        """Adds an entry describing the experiment and the outcome into a list"""
        #TODO update header line when new keys are added to experiment konfiguration

        file_path = self.global_log_folder+"/experiment_list.csv"
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

    def save_target_list(self,target_list):
        file_path = f"{self.experiment_folder}/target_list.csv"
        with open(file_path, "a+", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            for entry in target_list:
                csv_writer.writerow([entry])
        print("Target List Saved")
        return

    def save_pdmatrix(self, pd_matrix):
        file_path = f"{self.experiment_folder}/pd_matrix.csv"            
        pd_matrix.to_csv(file_path, index=False)
        print("Prerequest - Domain Matrix saved")
        return


    def save_base_checks_fails(self, base_check_fails):
        """Adds an entry describing the experiment and the outcome into a list"""
        file_path = f"{self.experiment_folder}/base_check_fails.csv"            
        with open(file_path, "a+", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            for entry in base_check_fails:
                csv_writer.writerow([entry])
        print("Base Check Fails saved")
        return

    def prerequest_statisics(self, prerequest, message_count):
        data_frame=pandas.DataFrame(prerequest)
        result_stats={
            "1xx(%)": data_frame["1xx"].sum()/message_count*100,
            "2xx(%)": data_frame["2xx"].sum()/message_count*100,
            "3xx(%)": data_frame["3xx"].sum()/message_count*100,
            "4xx(%)": data_frame["4xx"].sum()/message_count*100,
            "5xx(%)": data_frame["5xx"].sum()/message_count*100,
            "9xx(%)": data_frame["9xx"].sum()/message_count*100,
            
        }
        self.experiment_stats["Outcome"]=result_stats
        return

    def uri_deviation_table(self,uri_dev_table, rel_uri_dev_table):
        uri_dev_table['Sum'] = uri_dev_table.iloc[:, 1:].sum(axis=1)
        file_path = f"{self.experiment_folder}/uri_dev_statuscode.csv"            
        uri_dev_table.to_csv(file_path, index=False)
        rel_uri_dev_table['Sum'] = rel_uri_dev_table.iloc[:, 1:].sum(axis=1)
        file_path = f"{self.experiment_folder}/rel_uri_dev_statuscode.csv"            
        rel_uri_dev_table.to_csv(file_path, index=False)
        
        print("Prerequest - Domain Matrix saved")
        return

    def save_prerequests(self, prerequests):
        """Saves the prerequest list"""
        file_path = f"{self.experiment_folder}/prerequests.csv"
        with open(file_path, "w", newline="") as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=prerequests[0].keys())
            csv_writer.writeheader()
            for prerequest in prerequests:
                csv_writer.writerow(prerequest)
        print("prerequest.csv saved")
        return
    
    def save_exp_stats(self, run_time, messages, invalid_entries):
        self.experiment_stats["Experiment_Configuration"]=self.experiment_configuration
        self.experiment_stats["Experiment_Duration(s)"]=run_time
        self.experiment_stats["Experiment_Duration(h)"]=run_time/3600
        self.experiment_stats["Packets_per_second"]=self.experiment_stats["captured_packages"]/run_time
        self.experiment_stats["Messages"]=messages
        self.experiment_stats["Messages_per_second"]=messages/run_time
        active_workers=math.ceil(self.experiment_configuration["max_targets"]/self.experiment_configuration["target_subset_size"])
        if active_workers>self.experiment_configuration["max_workers"]: active_workers=self.experiment_configuration["max_workers"]
        self.experiment_stats["Active_Workers"]=active_workers
        self.experiment_stats["Folder_Size im MB"]=self.get_directory_size_mb(self.experiment_folder)
        self.experiment_stats["Invalid Target Entries"]=invalid_entries
        
        file_path = f"{self.experiment_folder}/experiment_outcome.json"
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(self.experiment_stats, file, indent=4)
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

    def copy_log_file(self):
        # Move the log file to a different folder using os.rename
        new_file_path = f"{self.experiment_folder}/debug.log"
        old_file_path= f"{self.global_log_folder}/debug.log"
        shutil.copy(old_file_path, new_file_path)
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
            
            #dumpcap_process=subprocess.Popen(dumpcap_cmd)
            dumpcap_process=subprocess.Popen(dumpcap_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

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
            try:
                output = dumpcap_process.stderr.read()
                print(output)
                lines = output.split('\n')
                packets_captured = None
                for line in lines:
                    if "Packets captured:" in line:
                        packets_captured = int(line.split(":")[1].strip())
                        break
            except Exception as e:
                self.exp_logging.error("Error capturing packets: %s",e)
                packets_captured = None
            self.experiment_stats["captured_packages"]=packets_captured
        except subprocess.TimeoutExpired:
            # If a timeout occurs, terminate the dumpcap process
            print("Timeout limit reached. Capturing terminated.")
            subprocess.run(["pkill", "dumpcap"], check=False)  # Terminate dumpcap process
            print("Process 'dumpcap' was successfully terminated.")
            
        
        except subprocess.CalledProcessError as e:
            self.exp_logging.error("Error capturing packets subprocess: %s",e)
            
        return True
    def extract_packets_per_host(host_list):
        return 0