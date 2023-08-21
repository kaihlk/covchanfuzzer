#main

from runner import ExperimentRunner
from logger import ExperimentLogger, TestRunLogger
import class_mapping
import csv
import time
import os
##For Infoe
""" class_mapping_requests ={
    1: HTTP1_Request_Builder,
    2: HTTP1_Request_CC_Case_Insensitivity,
    3: HTTP1_Request_CC_Random_Whitespace,
    4: HTTP1_Request_CC_Reordering_Header_Fields,
    5: HTTP1_Reqeust_CC_URI_Representation,
    6: HTTP1_Request_CC_URI_Case_Insentivity,
    7: HTTP1_Reqeust_CC_URI_Hex_Hex,
    8: HTTP1_Request_CC_Random_Content,
    9: HTTP1_Request_CC_Random_Content_No_Lenght_Field,
    10: HTTP1_Request_CC_URI_Common_Addresses
}

class_mapping_connection = {
    1: HTTP1_TCP_Connection,
    2: HTTP1_TLS_Connection,
    3: HTTP1_CC_TCP2TLS_Upgrade,
    4: HTTP2_TLS_Connection
    }

class_mapping_timing  = {
    1: Standard,
    2: Frequency_Modulation,
    3: Amplitude_Modulation,
} """
def get_last_experiment_number():
    file_path = "logs/experiment_list.csv"
    
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return 0 # First Experiment
    
    with open(file_path, "r") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        last_row = None
        for row in csv_reader:
            last_row = row
    return int(last_row["experiment_no"])

def load_target_list(target_list_csv):
     # Load the list back from the CSV file
    loaded_list = []
    with open(target_list_csv, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            rank, domain = row
            loaded_list.append(domain)

    print("List loaded from: " + target_list_csv)            
    return loaded_list     
        
def main():
    '''Function that runs the connection, selection of the CC and the fuzzer'''
    # TODO
  

    # Control the body of the response as well (?)
    #Add Verbose mode

    # Experiment Configuration Values
   # try:
    description= input("Input Experiment Description:")
    exp_no=get_last_experiment_number()+1


    experiment_configuration = {
        "experiment_no": exp_no,
        "comment": description,
        "verbose": False,
        "timestamp": time.strftime("%Y%m%d_%H%M%S"),
        #Covert Channel Option
        "covertchannel_request_number": 10,
        "covertchannel_connection_number": 1,
        "covertchannel_timing_number": 1,
        "fuzz_value":0.5,
        #Target Selection Options  
        "num_attempts": 10,
        "wait_between_request": 0,
        "base_line_check_frequency": 0,
        "target_list": "target_list_subdomain.csv",
        "target_subset_size": 33,
        #"target_host": "www.example.com",  #Just for special useipvstt
        "target_port": None, #443, 8080 Apache

        #Connection Options
        "conn_timeout": 2, #seconds 
        "nw_interface": "enp0s3",  #lo, docker, enp0s3     
        "use_ipv4": True,
        "use_TLS": False,
        "use_HTTP2": False,

        #HTTP Message Optionsa
        "method" : "GET",
        "url": "",
        "standard_subdomain": "www",
        "headers": None,
        "standard_headers": "firefox_HTTP/1.1",  #curl_HTTP/1.1(TLS), firefox_HTTP/1.1, firefox_HTTP/1.1_TLS, chromium_HTTP/1.1, chromium_HTTP/1.1_TLS"
        "content": "random",  #"random", "some_text""fuzz_value": 0.9,
            


    }

    



    experiment=ExperimentRunner(experiment_configuration, load_target_list(experiment_configuration["target_list"])).setup_and_start_experiment()
  
    
    

if __name__ == "__main__":
    main()