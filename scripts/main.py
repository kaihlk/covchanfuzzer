
import http1_covered_channels
import threading
import subprocess
import time
import os
import json
import re
from queue import Queue
from custom_http_client import CustomHTTP

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
        #TODO Check if destination port is need or if it is a problem when the connection is updated to TLS

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
            time.sleep(0.1)
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


class ExperimentRunnter:
    '''Runs the experiment itself'''
    def __init__(self, experiment_configuration, target_ip_info):
        self.experiment_configuration = experiment_configuration
        self.target_ip_info = target_ip_info
        self.target_port = experiment_configuration["target_port"]
    
    def baseline_check(self):
        #Todo
        return True

    def forge_and_send_requests(self, number):
        '''Build a HTTP Request Package and sends it and processes the response'''
        #Build HTTP Request
        request, deviation_count = http1_covered_channels.forge_http_request(
                    cc_number=self.experiment_configuration["covertchannel_number"],
                    host=self.experiment_configuration["target_host"],
                    port=self.target_port,
                    url="/",
                    method="GET",
                    headers=None,
                    fuzzvalue=self.experiment_configuration["fuzz_value"],
                )
        #Send request and get response
        print(request)
        #
        response, response_time = CustomHTTP().http_request(
            host=self.experiment_configuration["target_host"],
            port=self.target_port,
            host_ip_info=self.target_ip_info,
            custom_request=request,
        )
       #except Exception as ex:
       #     print("An error occurred during the HTTP request:", ex)
       #     response = None
         #   response_time = None
        response_status_code = response.Status_Code.decode("utf-8")
        
        request_data = {
            "number": number,
            "request": request,
            "deviation_count": deviation_count,
            "request_length": len(request),
            "status_code": response_status_code,
            "response_time": response_time,
        }
       
        return request, request_data


    def run_experiment(self):
        '''Run the experiment'''
        status_code_count = {}
        request_data_list = []
        for i in range(self.experiment_configuration["num_attempts"]):
            if self.baseline_check() is False:
                print("Baseline Check Failure, Connection maybe blocked")
            else:     
                # Send the HTTP request and get the response in the main thread
                response, request_data=self.forge_and_send_requests(i)
                status_code_count[request_data["status_code"]] = (status_code_count.get(request_data["status_code"], 0) + 1)
                request_data_list.append(request_data)
                # Print the response status code and deviation count
                print("Host: {}".format(self.experiment_configuration["target_host"]))
                print("Port: {}".format(self.target_port))
                print("Status Code: {}".format(request_data["status_code"]))
                print("Deviation Count: {}\n".format(request_data["deviation_count"]))

        return status_code_count, request_data_list   



def main():
    '''Function that runs the connection, selection of the CC and the fuzzer, should be cleaned up and externalised'''
    # TODO
    # host and channelselction, number of attempts as arguments?

    # Add a cautios mode that leaves some time between requests to the same adress (Not getting caught by Denial of service counter measures)
    # Add a mode that sends a well formed request every x attempts to verify not being blocked

    # Control the body of the response as well (?)

    # Experiment Configuration Values
    experiment_configuration = {
        "comment": "Some text describing the Testrun",
        "covertchannel_number": 3,
        "num_attempts": 100,
        "conn_timeout": 20.0,
        "nw_interface": "lo",
        "fuzz_value": 0.5,
        "use_ipv4": True,
        "target_host": "localhost",
        "target_port": 8080,
    }

    # Dns Lookup has to be done here  to get thark parameters 
    target_ip_info = CustomHTTP().lookup_dns(experiment_configuration["target_host"], experiment_configuration["target_port"])
    if experiment_configuration["use_ipv4"]:
        target_ip, target_port = target_ip_info[0][4]
    else:
        target_ip, target_port = target_ip_info[1][4]

    logger=ExperimentLogger(experiment_configuration, target_ip, target_port)

    # Inititialise dictionaries and lists for logging created packets
    status_code_count = {}
    request_data_list = []

    # Create a flag to stop the capturing process when the response is received
    stop_capture_flag = threading.Event()

    # Create an start thread for the packet capture
    capture_thread = threading.Thread(
        target=logger.capture_packets_dumpcap,
        args=(
            stop_capture_flag,
            experiment_configuration["nw_interface"],
        )
    )
    capture_thread.start()
    time.sleep(1)
    status_code_count, request_data_list = ExperimentRunnter(experiment_configuration, target_ip_info).run_experiment()
    # Time to let the packet dumper work
    time.sleep(1)

    stop_capture_flag.set()
    # Wait for the capture thread to finish
    capture_thread.join()
    

    print("Status Code Counts:")
    for status_code, count in status_code_count.items():
        print(f"{status_code}: {count}")

    # Save Experiment Metadata
    result_variables = {
        "Received_Status_Codes": status_code_count,
        #Here maybe more information would be nice, successful attempts/failures, count of successfull baseline checks, statistical data? medium response time?
    }
    logger.save_logfiles(request_data_list, result_variables)


if __name__ == "__main__":
    main()
