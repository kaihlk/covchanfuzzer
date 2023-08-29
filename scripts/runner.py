# runner.py
# runs a http fuzzing experiment


import concurrent.futures
import time
import threading
import http1_covered_channels
from logger import ExperimentLogger , TestRunLogger
from custom_http_client import CustomHTTP
import class_mapping
import http1_request_builder as request_builder


class ExperimentRunner:
    '''Runs the experiment itself'''
    def __init__(self, experiment_configuration, target_list):
        self.experiment_configuration = experiment_configuration
        self.target_list=target_list
        self.dns_fails=[]
        self.message_count=0
        self.prerequest_list=[]
        self.exp_log=None

    def get_target_subset(self, start_position=0, length=10)-> list:
        """Takes a subset from the target list to reduce the traffic to one target, in order to """
        
        if start_position <0 or start_position > len(self.target_list):
            raise ValueError("Invalid start_position")
        sub_set=self.target_list[start_position:]
        if length > len(sub_set):
            length = len(sub_set)
        
        sub_set=sub_set[:length]
        return sub_set

 


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
        print(sub_set)
        #Lookup DNS for each entry
        #TODO Catch the case that IPv4 or IPv6 is not provided, some sites sends more than one IP/Port set per protocoll version,  example macromedia.com and criteo.com
        for entry in sub_set:
            
            subdomains, hostname, tldomain= request_builder.HTTP1_Request_Builder().parse_host(entry)
            if self.experiment_configuration["target_add_www"]==True:
                if subdomains=="":
                    subdomains="www"
            if subdomains!="":
                subdomains=subdomains+"."        
            uri=subdomains+hostname+"."+tldomain
            print("DNS Lookup for: "+uri)
            socket_info = CustomHTTP().lookup_dns(uri, self.target_port, self.experiment_configuration["use_ipv4"])
            if socket_info:
                
                if self.experiment_configuration["use_ipv4"]:
                    ip_address, port=  socket_info[0][4]
                else:#IPv6
                    ip_address=  socket_info[0][4][0]
                    port = socket_info[0][4][1]
                if port!=self.target_port:
                    print("Warning: Retrieved port doesn't match configured port (r. Port/c.Port"+str(port)+"/"+str(self.target_port))
                sub_set_dns.append({"host":uri, "socket_info":socket_info, "ip_address":ip_address, "port":port })
            else:
                self.dns_fails.append(uri)
        return sub_set_dns


    def pregenerate_request(self):
        '''Build a HTTP Request Package and sends it and processes the response'''
        #Build HTTP Request after the selected covered channel
        selected_covered_channel = class_mapping.requests_builders[self.experiment_configuration["covertchannel_request_number"]]()
        try:
            request, deviation_count, uri = selected_covered_channel.generate_request(self.experiment_configuration, self.target_port)
        except Exception as e:
            print("Error CC Generate Request", e) 
        if self.experiment_configuration["verbose"]==True:
            print(request)
        prerequest= {
            "Nr":0,
            "request":request,
            "deviation_count":deviation_count,
            "uri":uri,
            "1xx":0,
            "2xx":0,
            "3xx":0,
            "4xx":0,
            "5xx":0,
            "9xx":0,
        }

        return prerequest


    def get_next_prerequest(self, attempt_number):
        if attempt_number>=len(self.prerequest_list):
            prerequest = self.pregenerate_request()
            self.prerequest_list.append(prerequest)
        else: 
            prerequest=self.prerequest_list[attempt_number]
            
        return prerequest

    def add_nr_and_status_code_to_request_list(self, attempt_no, response_line):
        self.prerequest_list[attempt_no]["Nr"]=attempt_no
        response_status_code = response_line["status_code"]    
        first_digit = str(response_status_code)[0]
        if first_digit == "1":
            self.prerequest_list[attempt_no]["1xx"]+=1
        elif first_digit == "2":
            self.prerequest_list[attempt_no]["2xx"]+=1
        elif first_digit == "3":
            self.prerequest_list[attempt_no]["3xx"]+=1
        elif first_digit == "4":
            self.prerequest_list[attempt_no]["4xx"]+=1
        elif first_digit == "5":
            self.prerequest_list[attempt_no]["5xx"]+=1
        elif first_digit== "9":
            self.prerequest_list[attempt_no]["9xx"]+=1
        
        return
        
    def check_content(self, body):
        #TODO add hash function and standard body
        return True
    
    def send_and_receive_request(self, attempt_number, request, deviation_count, uri, host_data, logger):    
        response_line, response_header_fields, body, measured_times, error_message  = CustomHTTP().http_request(
            host=host_data["host"],
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=host_data["port"],
            host_ip_info=host_data["socket_info"],
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path=logger.get_logging_folder()
        )
        if self.experiment_configuration["verbose"]==True:
            print("Response:",response_line)
        try:
            self.add_nr_and_status_code_to_request_list(attempt_number,response_line)
        except Exception as e:
            print("Exception during updating request_list",e)
        self.check_content(body)
        logger.add_request_response_data(attempt_number, request, deviation_count, uri, response_line, response_header_fields, body, measured_times, error_message)
      
        return 


    def run_experiment_subset(self, logger_list, sub_set_dns):

        '''Run the experiment'''
     
        for i in range(self.experiment_configuration["num_attempts"]):
            
            try:
                prerequest=self.get_next_prerequest(i)
            except Exception as e:
                print("Error while pregenerating requests", e)  
            
            

            for host_data,logger in zip(sub_set_dns, logger_list):
            #Round Robin one Host after each other
                if self.baseline_check() is False:
                    #TODO
                    print("Baseline Check Failure, Connection maybe blocked")
                else:     
                    # Send the HTTP request and get the response in the main threads
                    try:
                        request=request_builder.HTTP1_Request_Builder().replace_host_and_domain(prerequest["request"],host_data["host"], self.experiment_configuration["standard_subdomain"])
                        deviation_count=prerequest["deviation_count"]
                        uri=prerequest["uri"]
                    except Exception as e:
                        print("Error building the request",e)
                    try:
                        start_time=time.time()
                        self.send_and_receive_request(i, request, deviation_count, uri, host_data, logger)
                        self.message_count+=1
                        end_time=time.time()
                        response_time=end_time-start_time
                        print("Message No: " + str(self.message_count)+" Host: "+str(host_data["host"])+"Complete Message Time: " + str(response_time))
                    except Exception as e:
                        print("Error sending/receiving request",e)
                    
                    """                 if self.experiment_configuration["verbose"]==True:
                    # Print the response status code and deviation count
                    print(f"Results:")
                    print(f"Host: {self.experiment_configuration['target_host']}")
                    print(f"Port: {self.target_port}")
                    print(f"Status Code: {request_data['status_code']}")
                    print(f"Deviation Count: {request_data['deviation_count']}")
                    print(f"Error Message: {request_data['error_message']}\n") """
                    
        return  

    def fuzz_subset(self, subset):
        start_time=time.time()
        #Get DNS Infomation 
        subset_dns=self.add_dns_info(subset)
        #Prepare Threading
        capture_threads=[]
        logger_list=[]
        stop_events=[]
                    

        #Create logger object for each target #Iterate over Li
        for entry in subset_dns: 
            try:   
                logger=TestRunLogger(self.experiment_configuration, self.exp_log.get_experiment_folder(), entry, entry["host"], entry["ip_address"], entry["port"])
                logger_list.append(logger)           
                #Start capturing threads
                stop_event=threading.Event()
                stop_events.append(stop_event)
                #capture_thread = threading.Thread(target=logger.capture_packets, args=(stop_event,))
                #capture_thread.start()
                #capture_threads.append(capture_thread)
            except Exception as e:
                print("Error while creating logger objects:", e)    
        #Start sending packages after ensuring each capturing process is ready
        time.sleep(1)
        try:
            self.run_experiment_subset(logger_list, subset_dns)
        except Exception as e:
            print("Exception during run_experiment_subset: ", e)
        time.sleep(1)
        # Save Log fileds
        for logger in logger_list:
            logger.save_logfiles()
          
        #End capturing
        for stop_event in stop_events:
                stop_event.set()       
        # Wait for all capturing threads to complete
        for capture_thread in capture_threads:
            capture_thread.join()
        



        end_time=time.time()
        excecution_time=end_time-start_time    
        return excecution_time


    """def fuzz_subset(self, subset):
        #Get DNS Infomation 
        subset_dns=self.add_dns_info(subset)
        #Prepare Threading
        capture_threads=[]
        logger_list=[]
        stop_events=[]
                    
              with concurrent.futures.ThreadPoolExecutor() as executor:
            #Create logger object for each target #Iterate over Li
            for entry in subset_dns: 
                try:   
                    logger=TestRunLogger(self.experiment_configuration, self.exp_log.get_experiment_folder(), entry, entry["host"], entry["ip_address"], entry["port"])
                    logger_list.append(logger)           
                    stop_event=threading.Event()
                    stop_events.append(stop_event)
                    #Start capturing threads
                    capture_thread = executor.submit(logger.capture_packets, stop_event)
                    capture_threads.append(capture_thread)
                except Exception as e:
                    print("Error while creating logger objects:", e)    
            #Start sending packages after ensuring each capturing process is ready
            time.sleep(1)
            self.run_experiment_subset(logger_list, subset_dns)
        #End capturing
        for stop_event in stop_events:
                stop_event.set()       
        # Wait for all capturing threads to complete
        for capture_thread in capture_threads:
            capture_thread.join()
        
        # Save Log fileds
        for logger in logger_list:
            logger.save_logfiles()
        return True
        """

    def setup_and_start_experiment(self):
        '''Setups the Experiment, creates an experiment logger, and starts the experiment run'''
        
        try:
            #Create Folder for the experiment and save the path
            self.exp_log=ExperimentLogger(self.experiment_configuration)

            #Start Global Capturing Process

            global_stop_event = threading.Event()
            global_capture_thread = threading.Thread(target=self.exp_log.capture_packets_dumpcap, args=(global_stop_event,))
            global_capture_thread.start()
            time.sleep(1)
            #Loop over List

            start_position=0
            subset_length=self.experiment_configuration["target_subset_size"]
            max_targets=self.experiment_configuration["max_targets"]
            if max_targets>len(self.target_list): max_targets=len(self.target_list)

            subsets_tasks=[]


            with concurrent.futures.ThreadPoolExecutor(max_workers=self.experiment_configuration["max_workers"]) as subset_executor:
                
                try:
                
                    'Iterate through target list'
                    while start_position < max_targets: 
                        
                        #Get target subset
                        
                        subset=self.get_target_subset(start_position, subset_length)
                        
                        subset_task=subset_executor.submit(self.fuzz_subset, subset)
                        subsets_tasks.append(subset_task)
                        start_position += len(subset)
                except Exception as e:
                    print("An exception occurred:", e)
                

           
        except Exception as e:
            print("During the experiment an error occured", e)
        finally:
             # Wait for the global capture thread to finish
            global_stop_event.set() 
        
            global_capture_thread.join()   
            

            #Save OutCome to experiment Folder csv.
            self.exp_log.add_global_entry_to_experiment_list(self.experiment_configuration["experiment_no"])
            self.exp_log.save_dns_fails(self.dns_fails)
            self.exp_log.save_prerequests(self.prerequest_list)   
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

  
        return