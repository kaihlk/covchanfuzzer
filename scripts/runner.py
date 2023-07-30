# runner.py
# runs a http fuzzing experiment


import threading
import time
import http1_covered_channels
from logger import ExperimentLogger
from custom_http_client import CustomHTTP
import class_mapping
import http1_request_builder


class ExperimentRunner:
    '''Runs the experiment itself'''
    def __init__(self, experiment_configuration):
        self.experiment_configuration = experiment_configuration
        # Dns Lookup has to be done here  to get thark parameters 
        self.target_ip_info = CustomHTTP().lookup_dns(experiment_configuration["target_host"], experiment_configuration["target_port"])
        if experiment_configuration["use_ipv4"]:
            self.target_ip, self.target_port = self.target_ip_info[0][4]
        else:
            self.target_ip, self.target_port = self.target_ip_info[1][4]
       
    def baseline_check(self):
        #Todo
        return True

    def forge_and_send_requests(self, attempt_number):
        '''Build a HTTP Request Package and sends it and processes the response'''
        #Build HTTP Request
        selected_covered_channel = class_mapping_requests[self.experiment_configuration["covertchannel_request_number"]]()
        request, deviation_count = selected_covered_channel.generate_request(
                    cc_number=self.experiment_configuration["covertchannel_number"],
                    host=self.experiment_configuration["target_host"],
                    port=self.target_port,
                    url="/",
                    method="GET",
                    headers=None,
                    fuzzvalue=self.experiment_configuration["fuzz_value"],
                )
        """ request, deviation_count = http1_covered_channels.forge_http_request(
                    cc_number=self.experiment_configuration["covertchannel_number"],
                    host=self.experiment_configuration["target_host"],
                    port=self.target_port,
                    url="/",
                    method="GET",
                    headers=None,
                    fuzzvalue=self.experiment_configuration["fuzz_value"],
                )
         """#Send request and get response
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
            "number": attempt_number,
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
                print(f"Host: {self.experiment_configuration['target_host']}")
                print(f"Port: {self.target_port}")
                print(f"Status Code: {request_data['status_code']}")
                print(f"Deviation Count: {request_data['deviation_count']}\n")
        return status_code_count, request_data_list  

    def setup_and_start_experiment(self):
        '''Setups the Experiment, creates an experiment logger, and starts the experiment run'''
        logger=ExperimentLogger(self.experiment_configuration, self.target_ip, self.target_port)

        # Create a flag to stop the capturing process when the response is received
        stop_capture_flag = threading.Event()

        # Create an start thread for the packet capture
        capture_thread = threading.Thread(
            target=logger.capture_packets_dumpcap,
            args=(
                stop_capture_flag,
                self.experiment_configuration["nw_interface"],
            )
        )
        capture_thread.start()
        time.sleep(1)
        status_code_count, request_data_list = self.run_experiment()
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

