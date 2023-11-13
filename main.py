# main


import csv
import requests
import time
import os
import logging
import scapy.all as scapy
from runner import ExperimentRunner
from upgrade_target_list import Target_List_Upgrader
#from upgrade_target_list import Target_List_Analyzer

# For Information
""" class_mapping_requests ={
    0: HTTP1_Request_from_CSV
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




def is_network_adapter_present(adapter_name):
    # Get a list of available network interfaces using Scapy's conf.ifaces dictionary.
    network_interfaces = scapy.get_if_list()
    print("Network Adapters:", network_interfaces)
    if adapter_name in network_interfaces:
        print("Configured Network Adapter is ok")
    else:
        raise ValueError(f"Network adapter '{adapter_name}' is not present.") 
    return 


def get_logs_directory():
    """Get or create local log directory"""
    script_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(script_directory)

    # Check if directory for experiment_logs exist
    logs_directory = os.path.join(parent_directory, "logs")
    # Check if logs directory exists, elsewise create it
    if not os.path.exists(logs_directory):
        os.makedirs(logs_directory)

    return logs_directory


def configure_logger(log_path):
    """Configure the logger for exceptions and debugging"""

    # Configure the logging settings
    logging.basicConfig(
        level=logging.DEBUG,  # Set the desired log level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=f'{log_path}/debug.log',
        filemode='w'  # 'w' for overwrite, 'a' for append
    )

    # Create a logger instance for your main script
    main_logger = logging.getLogger('main')

    # Optionally, configure a console handler to print log messages to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    main_logger.addHandler(console_handler)

    return main_logger


def get_last_experiment_number(log_path):
    """Get or create Folder for experiment log files"""
    file_path = f"{log_path}/experiment_list.csv"
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return 0  # First Experiment
    with open(file_path, "r") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        last_row = None
        for row in csv_reader:
            last_row = row
    return int(last_row["experiment_no"])

def get_public_ips():
        try:
            ip_info = {}
            
            # Get IPv4 address
            response_ipv4 = requests.get("http://httpbin.org/ip")
            if response_ipv4.status_code == 200:
                data_ipv4 = response_ipv4.json()
                return data_ipv4.get("origin")
            else:
                ip_info = "Unable to retrieve IPv4 address."

            return ip_info

        except requests.RequestException as e:
            return {"error": str(e)}

def load_target_list(target_list_csv):
    """Load the list back from the CSV file, considering only the first two colum"""
    loaded_list = []
    with open(target_list_csv, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)
        for row in csv_reader:
            # Append the first two columns of each row to the loaded_list
            loaded_list.append(row[1])

    print("List loaded from: " + target_list_csv)
    print("List Length: ", len(loaded_list))
    return loaded_list

def main():
    '''Function that runs the connection, selection of the CC and the fuzzer'''

    log_path = get_logs_directory()
    print("Logpath: ", log_path)

    main_logger = configure_logger(log_path)

    # Experiment Configuration Values
    description = input("Input Experiment Description:")
    exp_no = get_last_experiment_number(log_path)+1

    experiment_configuration = {
        "experiment_no": exp_no,
        "comment": description,
        "verbose": False,
        "timestamp": time.strftime("%Y%m%d_%H%M%S"),
        # Covert Channel Option
        "covertchannel_request_number": 8,
        "covertchannel_connection_number": 1,
        "covertchannel_timing_number": 1,
        "min_fuzz_value": 0.01,
        "spread_deviation": 0.9,
        # Target Selection Options
        "num_attempts": 250,
        "max_targets": 1000,  # len(self.target_list):
        "max_workers": 25,  # Parallel Processing of subsets,
        "wait_between_request": 0,
        "base_line_check_frequency": 0,
        "check_basic_request": 2,

        # "target_list_subdomain_10000.csv",#"new_target_list.csv",
        "target_list": "target_list_subdomain_10000.csv",

        "target_subset_size": 40,
        "target_add_www": True,  # Add www if no other subdomain is known
        # "target_host": "www.example.com",  #Just for special useipvstt
        "target_port": 443,  # 443, 8080 Apache
        # Connection Options
        "conn_timeout": 5,  # seconds
        #"nw_interface": "enp0s3", # lappy
        #"nw_interface": "enp0s31f6",#attic
        "nw_interface": "enp6s0", #EOW #1f6",#"enp0s3",#s31f6#0s3",#31f6",#1s6",  # lo, docker, enp0s3
        
        "use_ipv4": True,
        "use_TLS": True,
        "use_HTTP2": False,

        # HTTP Message Options
        "HTTP_version": "HTTP/1.1",
        "method": "GET",
        "url": "",  # Complete URl
        "follow_redirects": 1, #Follow the first redirect if provided
        "path": "/",  # Dynamic, List, ?s
        "crawl_paths": 0, #(dafault 0 )

        "standard_subdomain": "www",  # use www if not provided
        # build a relative uri without the host in the requestline: /index.html
        "relative_uri": False,
        # include the subdomain, when building requestline, if none given use <standard_subdomain>
        "include_subdomain": True,  #Check maybe drop
        "include_port": False,
        "include_subdomain_host_header": True,
        "headers": None,
        # curl_HTTP/1.1(TLS), firefox_HTTP/1.1, firefox_HTTP/1.1_TLS, chromium_HTTP/1.1, chromium_HTTP/1.1_TLS"
        "standard_headers": "firefox_HTTP/1.1_TLS",
        "content": "random",  # "random", "some_text""fuzz_value": 0.9,
        "ip":get_public_ips()
     
    }


    run_exp = True
    if run_exp is True:
        try:
            is_network_adapter_present(experiment_configuration["nw_interface"])
            target_list = load_target_list(experiment_configuration["target_list"])
            experiment = ExperimentRunner(
                experiment_configuration, target_list, log_path)
            experiment.setup_and_start_experiment()
        except Exception as e:
            main_logger.error("Experiment run failed: %s", e)

    print("Done")


if __name__ == "__main__":
    main()
