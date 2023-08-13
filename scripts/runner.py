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
    def __init__(self, experiment_configuration, target_list):
        self.experiment_configuration = experiment_configuration
        # Dns Lookup has to be done here  to get thark parameters 
        self.target_ip_info = CustomHTTP().lookup_dns(experiment_configuration["target_host"], experiment_configuration["target_port"])
        self.target_list=target_list
        
        #TODO DELETE THIS PART IT SHOULD BE DONE SOMEWHERE ELSE
        
        
        if experiment_configuration["use_ipv4"]:
            self.target_ip, self.target_port = self.target_ip_info[0][4]
        else:
            self.target_ip, self.target_port = self.target_ip_info[1][4]
        self.dns_error=[]

    def get_target_subset(self, start_position=0, count=10)-> list:
        """Takes a subset from the target list to reduce the traffic to one target, in order to """
        
        if start_position <1 or start_position > len(self.target_list):
            raise ValueError("Invalid start_no")
        sub_set=self.target_list[start_position -1:]
        if count > len(sub_set):
            count = len(sub_set)
        
        sub_set=sub_set[:count]
        return sub_set

    def round_robin_target_selector():
        return 0


    def baseline_check(self):
        #Todo
        return True

    def add_dns_info(self, sub_set):
        """Adds DNS Information to each entry. Port and IP depending on Experiment_Configuration Options use_IPv4, use_TLS"""
        sub_set_dns=[]
        #Configure Port
        if self.experiment_configuration["target_port"] is not None:
            try:
                self.target_port=int(self.experiment_configuration["target_port"])
                if not 0 <= self.target_port <= 65535:
                    raise(ValueError())
            except ValueError:
                print("Invalid Portnumber in Experiment Configuratiion")
        else:
            if self.experiment_configuration["use_TLS"]:
                self.target_port=443
            else: 
                self.target_port=80

        #Lookup DNS for each entry
        #TODO Catch the case that IPv4 or IPv6 is not provided, some sites sends more than one IP/Port set per protocoll version,  example macromedia.com and criteo.com
        for entry in sub_set:
            print(entry)
            socket_info = CustomHTTP().lookup_dns(entry, self.target_port)
            if socket_info:
                print(socket_info)
                if self.experiment_configuration["use_ipv4"]:
                    ip_address, port=  socket_info[0][4]
                else:#IPv6
                    ip_address, port=  socket_info[1][4]     
                if port!=self.target_port:
                    print("Warning: Retrieved port doesn't match configured port (r. Port/c.Port"+str(port)+"/"+str(self.target_port))
                sub_set_dns.append({"Sub_set":sub_set, "socket_info":socket_info, "ip_address":ip_address, "port":port })
            else:
                self.dns_error.append(entry)
        return sub_set_dns


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
        capture_threads=[]

        #Create Log Folder and save the path
        
        #Loop over List
       
        start_position=1
        while start_position <= 100: #len(self.target_list):
            #Get target subset
            sub_set=self.get_target_subset(start_position,self.experiment_configuration["target_sub_setsize"])
            #Get DNS Infomation 
            sub_set_dns=self.add_dns_info(sub_set)
            for entry in sub_set_dns:
                #Create logger object for each target
                logger=ExperimentLogger(self.experiment_configuration, entry["ip_address"], entry["port"])
                # Create a flag to stop the capturing process
                stop_capture_flag = threading.Event()
                # Create an start thread for the packet capture
                capture_thread = threading.Thread(
                    target=logger.capture_packets_dumpcap,
                    args=(
                        stop_capture_flag,
                        self.experiment_configuration["nw_interface"],
                capture_thread.start() 
                    )
                )
                capture_threads.append(capture_thread)   

            start_position += self.experiment_configuration["target_sub_setsize"]

         #Take  Subset
        # Create an Experiment Folder
        # Create Subfolders for each target
        # start parallel capturing processes
        # loop over the list
        # save meta data for each target.
        result_variables = {
            "covertchannel_request_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_request_number"]]),
            "covertchannel_request_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_connection_number"]]),
            "covertchannel_timing_name": str(class_mapping.requests_builders[self.experiment_configuration["covertchannel_timing_number"]]),
            "Received_Status_Codes": status_code_count,
            "Message_Count": 1234,
            "Share_2xx": 100.0,
            "Response_2xx": 1200,
            "Response_4xx": 30,
            "Response_Error": 4,
            #Here maybe more information would be nice, successful attempts/failures, count of successfull baseline checks, statistical data? medium response time?
        }

        """
        
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

        logger.save_logfiles(request_data_list, result_variables)
 """

    #TODO
    def calculate_statistics():
        return 0
    #TODO
    def make_entry_to_experiment_list():
        return 0