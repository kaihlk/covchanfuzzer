# runner.py
# runs a http fuzzing experiment


import threading
import time
import http1_covered_channels
from logger import ExperimentLogger , TestRunLogger
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
                sub_set_dns.append({"host":entry, "socket_info":socket_info, "ip_address":ip_address, "port":port })
            else:
                self.dns_error.append(entry)
        return sub_set_dns


    def forge_requests(self, host_data):
        '''Build a HTTP Request Package and sends it and processes the response'''
        #Build HTTP Request after the selected covered channel
        selected_covered_channel = class_mapping.requests_builders[self.experiment_configuration["covertchannel_request_number"]]()
        #TODO Change of PORT due to Upgrade
        
        request, deviation_count = selected_covered_channel.generate_request(self.experiment_configuration, host_data)

        #Send request and get response
        if self.experiment_configuration["verbose"]==True:
            print(request)

        return request, deviation_count

    def check_content(self, body):
        #TODO add hash function and standard body
        return True
    
    def send_and_receive_request(self, attempt_number, request, deviation_count, host_data, logger):    
        response_line, response_header_fields, body, response_time, error_message  = CustomHTTP().http_request(
            host=host_data["host"],
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=host_data["port"],
            host_ip_info=host_data["socket_info"],
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
        )
        self.check_content(body)
        logger.add_request_response_data(attempt_number, request, deviation_count, response_line, response_header_fields, body, response_time, error_message)

      
       
        return request


    def run_experiment(self, logger_list, sub_set_dns):

        '''Run the experiment'''
     
        for i in range(self.experiment_configuration["num_attempts"]):
            for host_data,logger in zip(sub_set_dns, logger_list):
            #Round Robin one Host after each other
                if self.baseline_check() is False:
                    #TODO
                    print("Baseline Check Failure, Connection maybe blocked")
                else:     
                    # Send the HTTP request and get the response in the main thread
                    request, deviation_count=self.forge_requests(host_data)
                    self.send_and_receive_request(i, request, deviation_count, host_data, logger)
                    
                   
                    
                    """                 if self.experiment_configuration["verbose"]==True:
                    # Print the response status code and deviation count
                    print(f"Results:")
                    print(f"Host: {self.experiment_configuration['target_host']}")
                    print(f"Port: {self.target_port}")
                    print(f"Status Code: {request_data['status_code']}")
                    print(f"Deviation Count: {request_data['deviation_count']}")
                    print(f"Error Message: {request_data['error_message']}\n") """
                    
        return  

    def setup_and_start_experiment(self):
        '''Setups the Experiment, creates an experiment logger, and starts the experiment run'''
        

        #Create Folder for the experiment and save the path
        exp_log=ExperimentLogger(self.experiment_configuration)
        
        #Loop over List
        sub_set_no=1
        start_position=1
        while start_position <= 20: #len(self.target_list):
            #Get target subset
            subset=self.get_target_subset(start_position,self.experiment_configuration["target_subset_size"])
            
            #Get DNS Infomation 
            subset_dns=self.add_dns_info(subset)
            stop_capture_flag = threading.Event()
            #Start Capturing SubProcess
            #TODO change name of the file per run. Add to one bigfile
            
            capture_thread = threading.Thread(
                    target=exp_log.capture_packets_dumpcap,
                    args=(

                        stop_capture_flag,
                        self.experiment_configuration["nw_interface"],
                        
                    )
            ) 
            capture_thread.start()    
            #Create logger object for each target #Iterate over List
            time.sleep(1)
           
            logger_list=[]
            for entry in subset_dns:    
                print(entry)
                logger=TestRunLogger(self.experiment_configuration, exp_log.get_experiment_folder(), entry["host"], entry["ip_address"], entry["port"])
                logger_list.append(logger)

            #Start sending packages
            self.run_experiment(logger_list, subset_dns)
            for logger in logger_list:
                logger.save_logfiles()

            #End Capturing

            #Filter packets and save them to subfolders
            
            #Save OutCome to experiment Folder csv.
            
            #End capture thread
            start_position += self.experiment_configuration["target_subset_size"] 
            stop_capture_flag.set()
            # Wait for the capture thread to finish
            capture_thread.join()
             #This should be done in the end, added with some sttistics
            exp_log.add_global_entry_to_experiment_list(self.experiment_configuration["experiment_no"])
        
            
        
            
            """capture_threads=[] 

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

            start_position += self.experiment_configuration["target_sub_setsize"] """

         #Take  Subset
        # Create an Experiment Folder
        # Create Subfolders for each target
        # start parallel capturing processes
        # loop over the list
        # save meta data for each target.
        """
        """
        
       
        
        # Time to let the packet dumper work
        time.sleep(1)

        stop_capture_flag.set()
        # Wait for the capture thread to finish
        capture_thread.join()
        

        

        # Save Experiment Metadata

        #logger.save_logfiles(request_data_list, result_variables)
   

    #TODO
    def calculate_statistics():
        return 0
    #TODO
    def make_entry_to_experiment_list():
        return 0