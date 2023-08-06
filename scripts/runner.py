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
        #Build HTTP Request after the selected covered channel
        selected_covered_channel = class_mapping.requests_builders[self.experiment_configuration["covertchannel_request_number"]]()
        #TODO Change of PORT due to Upgrade
        
        request, deviation_count = selected_covered_channel.generate_request(self.experiment_configuration)

        #Send request and get response
        if self.experiment_configuration["verbose"]==True:
            print(request)
        
        response_line, response_header_fields, body, response_time, error_message  = CustomHTTP().http_request(
            host=self.experiment_configuration["target_host"],
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=self.target_port,
            host_ip_info=self.target_ip_info,
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
        )
   
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
                if self.experiment_configuration["verbose"]==True:
                    # Print the response status code and deviation count
                    print(f"Results:")
                    print(f"Host: {self.experiment_configuration['target_host']}")
                    print(f"Port: {self.target_port}")
                    print(f"Status Code: {request_data['status_code']}")
                    print(f"Deviation Count: {request_data['deviation_count']}")
                    print(f"Error Message: {request_data['error_message']}\n")
                
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
            "covertchannel_request_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_request_number"]]),
            "covertchannel_request_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_connection_number"]]),
            "covertchannel_timing_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_timing_number"]]),
            "Received_Status_Codes": status_code_count,
            #Here maybe more information would be nice, successful attempts/failures, count of successfull baseline checks, statistical data? medium response time?
        }
        logger.save_logfiles(request_data_list, result_variables)

