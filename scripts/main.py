#main

from upgrade_target_list import Target_List_Upgrader, Target_List_Analyzer
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
    # Load the list back from the CSV file, considering only the first two columns
    loaded_list = []
    with open(target_list_csv, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader) 
        for row in csv_reader:
            # Append the first two columns of each row to the loaded_list
            loaded_list.append(row[1])

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
        "covertchannel_request_number": 3,
        "covertchannel_connection_number": 1,
        "covertchannel_timing_number": 1,
        "fuzz_value":0.7,
        #Target Selection Options  
        "num_attempts": 1000,
        "max_targets": 1000, #len(self.target_list):
        "max_workers": 20,  # Parallel Processing of subsets,
        "wait_between_request": 0,
        "base_line_check_frequency": 0,
        "check_basic_request": 3,
        "target_list": "target_list_tls_abs_sub_subhost.csv",#"target_list_subdomain_10000.csv",#"new_target_list.csv",
        "target_subset_size": 50,
        "target_add_www": True,  #Add www if no other subdomain is known
        #"target_host": "www.example.com",  #Just for special useipvstt
        "target_port": 443, #443, 8080 Apache
 
        #Connection Options
        "conn_timeout": 5, #seconds 
        "nw_interface": "enp0s3",  #lo, docker, enp0s3     
        "use_ipv4": True,
        "use_TLS": True,
        "use_HTTP2": False,

        #HTTP Message Options
        "HTTP_version": "HTTP/1.1",
        "method" : "GET",
        "url": "",   #Complete URl
        "path": "/", #Dynamic, List, ?
        "standard_subdomain": "www", #use www if not provided
        "relative_uri": False, # build a relative uri without the host in the requestline: /index.html
        "include_subdomain": True, #include the subdomain, when building requestline, if none given use <standard_subdomain>
        "include_port":False,
        "include_subdomain_host_header": True,
        "headers": None,
        "standard_headers": "firefox_HTTP/1.1_TLS",  #curl_HTTP/1.1(TLS), firefox_HTTP/1.1, firefox_HTTP/1.1_TLS, chromium_HTTP/1.1, chromium_HTTP/1.1_TLS"
        "content": "random",  #"random", "some_text""fuzz_value": 0.9,
            


    }

    analyze_list=False
    upgrade_list=False
    run_exp=True
    if run_exp==True:
        try:
            
            experiment=ExperimentRunner(experiment_configuration, load_target_list(experiment_configuration["target_list"])).setup_and_start_experiment()
            
        except Exception as e:
            print("Experiment run failed: ", e)
    if upgrade_list==True:
        upgrade_path="upgraded_"+experiment_configuration["target_list"]
        #new_path2="upgraded_and_cleaned"+experiment_configuration["target_list"]
        upgrader=Target_List_Analyzer(new_path, new_path2, experiment_configuration)
        #upgrader=Target_List_Upgrader(experiment_configuration,upgrade_path).upgrade_list(
        upgrader.analyze_data()

    if analyze_list==True:
        analyze_path="analysed_"+experiment_configuration["target_list"]
        target_analizer=Target_List_Analyzer(upgrade_path, analyze_path, experiment_configuration)
        target_analizer.analyze_data()
        print("Data Check Complete")
    
    print("Done")

if __name__ == "__main__":
    main()