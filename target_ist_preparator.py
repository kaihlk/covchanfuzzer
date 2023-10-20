"""Target_List_Preparator"""

import concurrent.futures
from concurrent.futures import FIRST_COMPLETED
import time
import logging
import hashlib
import threading
import pandas
import random

import HTTP1_Request_Builder

class Target_List_Preperator:
    def __init__(self, experiment_configuration, log_folder):
        self.experiment_configuration = experiment_configuration
        self.log_folder=log_folder
        self.target_list=target_list

    def prepare_data_frame():
        target_list=self.load_target_list(self.experiment_configuration["target_list"])
        port=self.verify_port(self.experiment_configuration["target_port"])
        df=pandas.DataFrame()
    return df

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
    
    def get_target_subset(self, target_list, start_position=0, length=10)-> list:
        """Takes a subset from the target list to reduce the traffic to one target, in order to """
        #Check inputs
        if start_position <0 or start_position+length > len(target_list):
            raise ValueError("Invalid start_position")
        subset=target_list[start_position:]
        #Prevent length exeeding target_list
        if length > len(subset):
            length = len(subset)
        subset=subset[:length]
        return subset
    
    
    
    def prepare_target(self, index, start_hostname):
        """Processes a target and adds all data for use within the fuzzer"""
        df=pandas.DataFrame()
        df["Index"]=index
        df["Hostname_Tranco"]=start_hostname
        standard_subdomain=self.experiment_configuration["standard_subdomain"]
        target_port=self.experiment_configuration["target_port"]
        use_ipv4=self.experiment_configuration["use_ipv4"]
        use_tls=self.experiment_configuration["use_tls"]
        include_subdomain=self.experiment_configuration["include_subdomain"]
        valid_entry_found=False

        while not valid_entry_found:
            socket_dns_info= self.get_dns_info(start_hostname, target_port, standard_subdomain, use_ipv4)
            basic_request_status_code, new_location =self.basic_request(socket_dns_info["host"], socket_dns_info["socket_info"], include_subdomain)
            socket_dns_info= self.get_dns_info(start_hostname, target_port, standard_subdomain, use_ipv4, use_tls)
            if socket_dns_info==None:
                continue


             base_linechekc

    
    def verify_port(self, target_port):
        target_port=int(self.experiment_configuration["target_port"])
        if target_port= is not None:
            try:
                if not 0 <= target_port <= 65535:
                    raise(ValueError())
            except ValueError:
                self.target_prep_logger.error("Invalid Portnumber in Experiment Configuration: %s", target_port)
        else:
            if self.experiment_configuration["use_TLS"]:
                target_port=443
            else: 
                target_port=80
        return target_port

    def get_dns_info(self, uri, standard_subdomain, target_port, use_ipv4):
        """Adds DNS Information to host"""
        dns_info=None
        _scheme, subdomains, hostname, tldomain, _port, _path= request_builder.HTTP1_Request_Builder().parse_host(uri)
        target_host=subdomains+"."+hostname+"."+tldomain
        try:
            last_try=False
            errors=""
            while True:
                socket_info, error = CustomHTTP().lookup_dns(target_host, target_port, use_ipv4)    
                if socket_info is not None:
                    # Socket info found, exit the loop
                    break                
                #Reduce subdomains if present 
                errors += f"{target_host}: {error}    "
                parts = target_host.split('.')
                if len(parts) > 2:
                    target_host = '.'.join(parts[1:])
                else: 
                    # Try Standard Domain if no subdomain left
                    if last_try is True:
                        raise ValueError(f"Could not get DNS Info for: {uri} Error Messages: {errors}")
                    target_host = standard_subdomain+"."+parts[0]
                    last_try=True
        except Exception as e:
                self.target_prep_logger.error(f"An error occurred during DNS Lookup: {e}")
                with self.lock_df:
                    self.dns_fails.append([uri,errors])
            
        finally: 
            if socket_info!=None
            #TODO Catch the case that IPv4 or IPv6 is not provided, some sites sends more than one IP/Port set per protocoll version,  example macromedia.com and criteo.com  
            #IPv4 Socket_Info
            if use_ipv4:
                try: 
                    ip_address, port=  socket_info[0][4]
                except Exception as e:
                    self.target_prep_logger.error("Error getting Port and IP from Socket Info: %s", e)
            #IPv6 Socket_Info
            else:
                try:
                    ip_address=  socket_info[4][0]
                    port = socket_info[4][1]
                except Exception as e:
                    self.target_prep_logger.error("Error getting Port and IP from Socket Info: %s", e)
            
            dns_info={"host":target_host, "socket_info":socket_info, "ip_address":ip_address, "port":port }
                
        return dns_info


    def check_target_list_subset(self,target_list, start_position=0, length=10 ):
        """Checks a subset from the target list, returns the validated entries"""
        #Check Inputs
        if start_position <0 or start_position+length > len(target_list):
            raise ValueError("Invalid start_position")
        #initalize counter for failed DNS LookUp http_options
        invalid_entries_count=0
        checked_subset=[]
        subset=target_list[start_position:start_position+length]
        #Build sub_set List with valid targets
        for entry in subset:
            dns_entry, error = self.add_dns_info(entry)
            #Check Socket Info
            if dns_entry is not None:
                #Check http options, update dns entry if redirect is possible and selected
                if self.experiment_configuration["verbose"] is True:
                    print(dns_entry)
                check, dns_entry=self.check_entry_http_options(dns_entry, self.experiment_configuration["follow_redirect"])
                
                if check is True:
                    crawl_uri=dns_entry["host"]
                    paths=host_crawler().get_paths(crawl_uri, self.experiment_configuration["target_port"], self.experiment_configuration["crawl_paths"], max_attempts=5, time_out=self.experiment_configuration["conn_timeout"])
                    dns_entry["paths"]=paths
                    checked_subset.append(dns_entry)
                else:
                    invalid_entries_count+=1
            else:
                invalid_entries_count+=1
            # Repeat until sub_set has desired lenght
           
        return checked_subset, invalid_entries_count


    

    def basic_request(self, domain, socket_info, location):
        """Performs as basic request with the selected options to check, if they match the host configuration"""
        #Initialize Variables
        host=None
        response_line=None
        response_status_code=None
        redirect_location=None
        
        
        _scheme, subdomains, hostname, tldomain, _port, path= request_builder.HTTP1_Request_Builder().parse_host(domain)
        if local_configuration["target_add_www"] is True:
            if subdomains=="":
                subdomains="www"
        if subdomains!="":
            subdomains=subdomains+"."
        uri=subdomains+hostname+"."+tldomain
        request_string, _, _=request_builder.HTTP1_Request_Builder().generate_request(local_configuration, 443)
        #host deprecated?
        #Carefull some hosts expect more 
     
        request, _, _ =request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, uri, local_configuration["standard_subdomain"], host, local_configuration["include_subdomain_host_header"])       
        if local_configuration["include_subdomain_host_header"] is True:
            host=subdomains+hostname+"."+tldomain
        else:
            host=hostname+"."+tldomain
        # Perform Request
        response_line, response_header_fields, body, measured_times, error_message  = CustomHTTP().http_request(
            host=host,#host is important for building the TLS context
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=443,
            host_ip_info=socket_info,
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path=self.exp_log.get_experiment_folder()+"/base_request",    #Transfer to save TLS Keys
        )
        if response_line is not None:
            response_status_code = response_line["status_code"]
            if str(response_status_code)[0]=="3":
                redirect_location=response_header_fields.get('location') # Returns none if not pressent
        return response_status_code, redirect_location

    d


    def check_entry_http_options(self, entry_dns, follow_redirect=False): 
        """Perform n basic requests if option is set."""
        redirect_entry_dns=None
        check=False
        basic_request_status_code=0
        if self.experiment_configuration["check_basic_request"]!=0:
            for i in range(self.experiment_configuration["check_basic_request"]):
                #Check if basic request is answered with a 2xx or 3xx response
                print("Basic Check No. ",i," Target: ", entry_dns["host"])
                basic_request_status_code, new_location =self.basic_request(entry_dns["host"], entry_dns["socket_info"])
                first_digit = str(basic_request_status_code)[0]
                print("Result: ", first_digit)
                #Check first redirect
                if first_digit == "3" and follow_redirect is True:
                    #Check redirect location
                    print("Checking redirect location:", new_location)
                    #Check if it is relative redirect
                    if not new_location.startswith(('http:', 'https:')):
                        new_location = entry_dns["host"]+ new_location

                    #Overwrite entry DNS, Lookup new Location
                    entry_dns, error =self.add_dns_info(new_location)
                    second_request_status_code, second_location =self.basic_request(new_location, entry_dns["socket_info"])
                    #Overwrite śecond location
                    first_digit = str(second_request_status_code)[0]
                    print("Result: ", first_digit)
                if first_digit == "2":
                    check=True
                else:
                    check=False
                    break
        else:
            #Add Entry without Basic Check if option is 0
            check=True
        if check is False:
            #Extend List when Basic Check Fails
            with self.lock_bcf:
                self.base_check_fails.append([entry_dns["host"], basic_request_status_code])           
        print(entry_dns)
        return check, entry_dns