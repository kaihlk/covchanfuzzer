"""Target_List_Preparator"""

import concurrent.futures
from concurrent.futures import FIRST_COMPLETED
import time
import logging
import hashlib
import threading
import pandas
import csv
import random
import http1_request_builder as request_builder
from custom_http_client import CustomHTTP
from host_crawler import host_crawler

class Target_List_Preperator:
    def __init__(self, experiment_configuration, exp_logger):
        self.experiment_configuration = experiment_configuration
        self.exp_log_folder=exp_logger.get_experiment_folder()+"/base_request"
        self.target_list=self.load_target_list_df(experiment_configuration["target_list"])
        self.target_prep_logger = logging.getLogger('main.runner')
        self.dns_fails=[]
        self.lock_df = threading.Lock()
        self.request_response_data_list=[]
        self.lock_rrd = threading.Lock()
        self.base_check_fails = []
        self.lock_bcf = threading.Lock()
        

    def save_df(self, dataframe, filename):
        file_path = f"{self.exp_log_folder}/{filename}"            
        dataframe.to_csv(file_path, index=False)
        print("CSV Saved: ", file_path)
        return
    def save_df_json(self, dataframe, filename):
        file_path = f"{self.exp_log_folder}/{filename}"            
        dataframe.to_json(file_path, index=False)
        print("JSON Saved: ", file_path)
        return

    def save_dict_list(self, dict_list, filename):
        '''Save the recorded requests'''
        file_path = f"{self.exp_log_folder}/{filename}"  
        with open(file_path, "w", newline="") as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=dict_list[0].keys())
            csv_writer.writeheader()
            for dictionary in dict_list:
                csv_writer.writerow(dictionary)
        print("CSV Saved: ", file_path)
        return   
    
    def save_list(self, list_to_save, filename):
        """Adds an entry describing the experiment and the outcome into a list"""
        file_path = f"{self.exp_log_folder}/{filename}"            
        with open(file_path, "a+", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            for entry in list_to_save:
                csv_writer.writerow([entry])
        print("CSV Saved: ", file_path)
        return
        
    def prepare_data_frame(self, target_sub_list):
        """Builds a dataframe with validated target information"""
        port=self.verify_port(self.experiment_configuration["target_port"])
        #df_target_list=target_sub_list
        df_target_list= self.target_list
        df_target_data = pandas.DataFrame()
        
        
        for index,row in df_target_list.iterrows():
            target_data, errors=self.prepare_target(row['Rank'] , row['Domain'] )
            if target_data!=None:
                row = pandas.DataFrame.from_dict(target_data, orient="index").T
                df_target_data = pandas.concat([df_target_data, row], ignore_index=True)
            else:
                print("Errors:", errors)
            
        self.save_df(df_target_data, filename="target_list.csv")
        self.save_dict_list(self.request_response_data_list, filename="request_response.csv")
        self.save_df_json(df_target_data, filename="target_list.json")
        return df_target_data

    
    def prepare_target_list(self):
        """Builds a list from the provided target list, check DNS Looḱupg/Socket Info and http_options"""
        target_list=self.target_list
        max_targets=self.experiment_configuration["max_targets"]
        max_workers=self.experiment_configuration["max_workers"]
        
        #Initialise Variables
        start_position=0
        invalid_entry_counts=0
        end_of_list=False
        subsets_tasks=[]
        df_checked_targets=pandas.DataFrame()#checked_target_list=[]
        active_workers=0

        if max_workers>=10: max_workers=10

        subset_length=max(int(max_targets/max_workers),1)    
        #Make sure if that the target list has enough entries --Maybe drop
        ##if max_targets>len(target_list):
        ##    max_targets=len(target_list)
        if max_targets>target_list.shape[0]:
            max_targets=target_list.shape[0]
        #Build futures to look up DNS until enough target are collected or end of target list is reached
        with concurrent.futures.ThreadPoolExecutor(max_workers) as subset_executor:
            while df_checked_targets.shape[0]<max_targets or end_of_list is True:
                while active_workers<max_workers:
                    # If target_list limit is reached, break
                    if  start_position>target_list.shape[0]:
                        print("End of list reached")
                        #    #Raise Error?
                        end_of_list=True
                        break
                    #Get DNS Infomation for the subset, if the lookup fails for an entry the subset will be shortened
                    subset_task = subset_executor.submit(self.check_target_list_subset, target_list, start_position, subset_length)
                    # Shift the start position for next iteration
                    start_position += subset_length
                    # Submit the subset for processing to executor
                    subsets_tasks.append(subset_task)
                    active_workers+=1
                    #InnerLoop End
                #Wait for a completed task
                completed_tasks, _ = concurrent.futures.wait(subsets_tasks, return_when=concurrent.futures.FIRST_COMPLETED)
                for completed_task in completed_tasks:
                    try:
                        # Save the results
                        new_targets, invalid_entries = completed_task.result()
                        # Make sure that no double entries are created, due to manipulationg the subdomain
                        df_checked_targets = pandas.concat([df_checked_targets, new_targets])
                        # Remove duplicates based on the "uri" column
                        df_checked_targets = df_checked_targets.drop_duplicates(subset="uri", keep="first")

                        # Reset the index
                        df_checked_targets = df_checked_targets.reset_index(drop=True)
                        invalid_entry_counts+=invalid_entries
                        """  for index, target in new_targets.iterrows():
                            host = target.get("uri")
                            double_entry = False
                            for index, entry in df_checked_targets.iterrows():
                                if host == entry.get("uri"):
                                    invalid_entries += 1
                                    double_entry = True
                                    break
                            if not double_entry:
                                df_checked_targets = pandas.concat([df_checked_targets, target], axis=0, ignore_index=True)
                        invalid_entry_counts+=invalid_entries """
                       
                    except Exception as e:
                        self.target_prep_logger.error("Error while processing completed task: %s", e)
                    finally:
                        # Remove the task from the list
                        subsets_tasks.remove(completed_task)
                        active_workers -= 1
        #Limit list if paralallel processing returned more targets than needed
        if df_checked_targets.shape[0] > max_targets:
            df_checked_targets = df_checked_targets[:max_targets]


        print("Invalid Entries:", invalid_entry_counts) 
      
      
        
        self.save_dict_list(self.base_check_fails, "base_check_fails.csv")
        if len(self.dns_fails)>0:
            self.save_dict_list(self.dns_fails, "dns_fails.csv")     
        self.save_df(df_checked_targets, filename="target_list.csv")
        self.save_df_json(df_checked_targets, filename="target_list.json")
        self.save_dict_list(self.request_response_data_list, filename="request_response.csv")

        return df_checked_targets, invalid_entry_counts 
    

    def load_target_list(self, target_list_csv):
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
        
    
    
    
    
    
    def load_target_list_df(self,target_list_csv):
        """Load the list back from the CSV file, considering only the first two columns."""
        df = pandas.read_csv(target_list_csv, usecols=[0, 1])

        print("DataFrame loaded from:", target_list_csv)
        print("DataFrame Shape:", df.shape)
        print("Column Names (Headers):", df.columns)
        return df

    
    def prepare_target(self, index, uri, max_redirect=2):
        """Processes a target, get DNS info, follows redirects and and check answers of basic requests"""
        target_data= {
            "rank": index,
            "tranco_domain": uri,
        }

        standard_subdomain=self.experiment_configuration["standard_subdomain"]
        target_port=self.experiment_configuration["target_port"]
        use_ipv4=self.experiment_configuration["use_ipv4"]       
        include_subdomain_host_header=self.experiment_configuration["include_subdomain_host_header"]
        followed_redirects=0
        passed_checks=0
        redirect_location=""
        errors=""
        #look for DNS; Follow Redirects
        while passed_checks<self.experiment_configuration["check_basic_request"]:
            #Try to get DNS Info for a Socket
            
            socket_dns_info, socket_errors = self.get_dns_info(uri, standard_subdomain, target_port, use_ipv4)
            if socket_errors!="":
                errors+=f"{uri}: Socket Errors: {socket_errors} "
            if socket_dns_info is None: #End if DNS can't be found
                return None, errors
                break
            #Build the request    
            request_string, _deviation_count, _new_uri = request_builder.HTTP1_Request_Builder().generate_request(self.experiment_configuration, target_port)
            #Replace Placeholders
            request, _deviation_count, _new_uri = request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, uri, standard_subdomain, socket_dns_info["host"], include_subdomain_host_header, path="/")
            #Send request
          
            response_line, response_header_fields, _body, _measured_times, error_messages  = CustomHTTP().http_request(
            host=socket_dns_info["host"],
            use_ipv4=use_ipv4,
            port=target_port,
            host_ip_info=socket_dns_info["socket_info"],
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path=self.exp_log_folder,    #Transfer to save TLS Keys
            )

            if len(error_messages)>1:
                errors+=f"{uri}: HTTP Errors: {error_messages} "
            request_response_data={
                    "tranco_ranc": index,
                    "uri": uri,
                    "followed_redirect": followed_redirects,
                    "passed_checks": passed_checks,
                    "request": request,
                    "response_line": response_line,
                    "response_header":response_header_fields,
                     }
            with self.lock_rrd:
                self.request_response_data_list.append(request_response_data)            
            if response_line is not None:
                response_status_code = response_line["status_code"]
                first_digit=int(str(response_status_code)[0])
                if first_digit==2: 
                    passed_checks+=1 
                    print("passed checks: ",passed_checks)
                    continue                   
                if first_digit==3:
                    if followed_redirects>max_redirect:
                        return None, errors
                    followed_redirects+=1
                    redirect_location=response_header_fields.get('location') # Returns none if not pressent
                    #Check if newlocation is relative or absolute
                    if redirect_location is not None:
                        if not redirect_location.startswith(('http:', 'https:')):
                            uri = socket_dns_info["host"]+ redirect_location
                        else:
                            #Sometimes location header is 2not processed properly in from scapy, it comes doubled
                            parts=redirect_location.split("://")
                            if len(parts)>2:
                                uri = parts[0] + "://" + parts[-1]
                            else:
                                uri=redirect_location
                    else:
                        errors+=f"{uri}: Redirect Location not found"       
                else:
                    with self.lock_bcf:
                        base_check_fail={
                            "uri": uri,
                            "socket_info": socket_dns_info,
                            "status-code": response_status_code,
                            "errors": errors
                            }
                        self.base_check_fails.append(base_check_fail)
                    return None, errors
            else:  # No valid answer
                return None, errors
        
        target_data["uri"]=uri
        target_data["socket_dns_info"]=socket_dns_info
        
        #target_data["errors"]=errors
        return target_data, errors
    

    def verify_port(self, target_port=None):
        target_port=int(self.experiment_configuration["target_port"])
        if target_port is not None:
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
        self.experiment_configuration["target_port"]=target_port      
        return target_port


    def get_dns_info(self, uri, standard_subdomain, target_port, use_ipv4):
        """Adds DNS Information to host, after fails, it stepwise reduces subdomains and tries standard_subdomain"""
        dns_info=None
        errors=""
        _scheme, subdomains, hostname, tldomain, _port, _path= request_builder.HTTP1_Request_Builder().parse_host(uri)
        if subdomains!="":
            subdomains+="."
        target_host=subdomains+hostname+"."+tldomain
        try:
            
            last_try=False
            errors=""
            while True:
                time.sleep(0.2)  # Just for DNS r
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
                    target_host = standard_subdomain+"."+parts[0]+"."+parts[1]
                    last_try=True
        except Exception as e:
                self.target_prep_logger.error(f"An error occurred during DNS Lookup: {e}")
                with self.lock_df:
                    dns_fail={
                        "uri":uri,
                        "errors":errors,
                    }
                    self.dns_fails.append(dns_fail)    
        finally: 
            if socket_info is not None:
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
                
                dns_info={
                    "host":target_host,
                    "socket_info":socket_info, 
                    "ip_address":ip_address, 
                    "port":port }                
        return dns_info, errors


    def check_target_list_subset(self, target_list, start_position=0, length=10 ):
        """Checks a subset from the target list, returns the validated entries"""
        #Check Inputs
        
        print(start_position)
        if start_position < 0 or start_position+length > len(target_list):
            raise ValueError("Invalid start_position")
        #initalize counter for failed DNS LookUp http_options
        invalid_entries_count=0
        df_checked_targets=pandas.DataFrame()
        subset=target_list[start_position:start_position+length]
        #Build sub_set List with valid targets
        for index,row in subset.iterrows():
            target_data, errors=self.prepare_target(row['Rank'] , row['Domain'] )
            if target_data!=None:
                if self.experiment_configuration["crawl_paths"]>0:
                    try:
                        crawl_uri=target_data["uri"]
                        print("Crawling:", crawl_uri)
                        host_crawler_instance = host_crawler(self.experiment_configuration, self.exp_log_folder)
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(host_crawler_instance.get_paths, crawl_uri, self.experiment_configuration["target_port"], self.experiment_configuration["crawl_paths"], max_attempts=5, timeout=self.experiment_configuration["conn_timeout"])
                            paths = future.result(self.experiment_configuration["crawl_paths"]+self.experiment_configuration["conn_timeout"])
                    except concurrent.futures.TimeoutError:
                        print("The crawling operation exceeded the specified timeout.")
                        paths = ["/"]
                    except Exception as e:
                        print(f"An error occurred during crawling: {e}")
                        paths = ["/"]
                else:
                    paths=["/"]
                target_data["paths"] = paths
                row = pandas.DataFrame.from_dict(target_data, orient="index").T
                df_checked_targets = pandas.concat([df_checked_targets, row], ignore_index=True)    
            else:
                print("Errors:", errors)
                invalid_entries_count+=1 

         
        return df_checked_targets, invalid_entries_count


    """ 


    def check_entry_http_options(self, entry_dns, follow_redirect=0): 
        Perform n basic requests if option is set.
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




    def basic_request(self, hostname, socket_info, location):
        Performs as basic request with the selected options to check, if they match the host configuration
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
        return response_status_code, redirect_location,

        """

