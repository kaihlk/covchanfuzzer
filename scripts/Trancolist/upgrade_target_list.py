import pandas
import json
from runner import ExperimentRunner
from custom_http_client import CustomHTTP
import http1_request_builder as request_builder

class Target_List_Upgrader():


    def __init__(self, experiment_configuration, new_path):
        self.experiment_configuration = experiment_configuration
        self.data_frame=self.read_host_list_to_dataframe(experiment_configuration["target_list"])
        self.new_path=new_path

    def read_host_list_to_dataframe(self,path):
        data_frame= pandas.read_csv(path)
        return data_frame

    def save_data_frame_to_upgraded_list(self, new_path):
        self.data_frame.to_csv(new_path,index=False)
        return

    def add_dns_with_standard_subdomain_80(self, domain):
        socket_info, ex = CustomHTTP().lookup_dns(domain, 80, self.experiment_configuration["use_ipv4"])
        print(socket_info, ex)
        if socket_info:
            return socket_info
        else:
            return ex

    def add_dns_with_standard_subdomain_443(self, domain):
        socket_info, ex = CustomHTTP().lookup_dns(domain, 443, self.experiment_configuration["use_ipv4"])
        print(socket_info, ex)
        if socket_info:
            return socket_info
        else:
            return ex
        

    def add_dns_with_www_subdomain_80(self, domain):
        subdomains, hostname, tldomain= request_builder.HTTP1_Request_Builder().parse_host(domain)
        if subdomains=="":
                subdomains="www"
        subdomains=subdomains+"."        
        uri=subdomains+hostname+"."+tldomain
        

        socket_info, ex = CustomHTTP().lookup_dns(uri, 80, self.experiment_configuration["use_ipv4"])
        if socket_info:
            return socket_info
        else:
            return ex

    def add_dns_with_www_subdomain_443(self, domain):
        subdomains, hostname, tldomain= request_builder.HTTP1_Request_Builder().parse_host(domain)
        if subdomains=="":
                subdomains="www"
        subdomains=subdomains+"."        
        uri=subdomains+hostname+"."+tldomain
        
        socket_info, ex = CustomHTTP().lookup_dns(uri, 443, self.experiment_configuration["use_ipv4"])
        if socket_info:
            return socket_info
        else:
            return ex

    def add_tcp_3xx_redirect(self, domain, socket_info):      
       
        host=None
        if not socket_info or isinstance(socket_info, str):
            return 999, ""
        local_configuration=self.experiment_configuration
        local_configuration["path"]="/"
        local_configuration["use_TLS"]=False
        local_configuration["relative_uri"]=True
        local_configuration["include_subdomain"]=True
        local_configuration["include_port"]=False
        local_configuration["include_subdomain_host_header"]=True
        local_configuration["standard_subdomain"]="www"

        subdomains, hostname, tldomain= request_builder.HTTP1_Request_Builder().parse_host(domain)
        if subdomains!="":
                subdomains=subdomains+"."        
        uri=subdomains+hostname+"."+tldomain
        host=None
        request_string, deviation_count, new_uri=request_builder.HTTP1_Request_Builder().generate_request(local_configuration, 80) 
        
        request=request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, domain, local_configuration["standard_subdomain"], host, local_configuration["include_subdomain_host_header"]) #Carefull some hosts expect more
        response_line, response_header_fields, body, measured_times, error_message  = CustomHTTP().http_request(
            host=domain,
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=80,
            host_ip_info=socket_info,
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path="TLS_Keys_Upgrade_List.txt",    #Transfer to save TLS Keys
        )
        if local_configuration["verbose"]:
            print(request)
            print(response_line)
            print(response_header_fields)
            print()
        first_digit=9
        if response_line!=None:
            response_status_code = response_line["status_code"] 
            return response_status_code
        else:
            return 999

    def add_https_absolute_uri_without_subdomain(self, domain, socket_info):
        if not socket_info or isinstance(socket_info, str):
            return 999, ""
        local_configuration=self.experiment_configuration
        local_configuration["path"]="/"
        local_configuration["use_TLS"]=True
        local_configuration["relative_uri"]=False
        local_configuration["include_subdomain"]=False
        local_configuration["include_port"]=False
        local_configuration["include_subdomain_host_header"]=False
        local_configuration["standard_subdomain"]=""

        subdomains, hostname, tldomain= request_builder.HTTP1_Request_Builder().parse_host(domain)
        if subdomains!="":
                subdomains=subdomains+"."        
        uri=subdomains+hostname+"."+tldomain
        

        host=None
        request_string, deviation_count, new_uri=request_builder.HTTP1_Request_Builder().generate_request(local_configuration, 443)
    
        request=request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, domain, local_configuration["standard_subdomain"], host, local_configuration["include_subdomain_host_header"]) #Carefull some hosts expect more
        response_line, response_header_fields, body, measured_times, error_message  = CustomHTTP().http_request(
            host=uri,
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=443,
            host_ip_info=socket_info,
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path=".tranco",    #Transfer to save TLS Keys
        )
        if local_configuration["verbose"]:
            print(request)
            print(response_line)
            print(response_header_fields)
            print()
        if response_line!=None:
            response_status_code = response_line["status_code"]
            location=response_header_fields.get('location')
            return response_status_code, location
        else:
            return 999, ""

    def add_https_absolute_uri_www_subdomain(self, domain, socket_info):
        if not socket_info or isinstance(socket_info, str):
            return 999, ""
        local_configuration=self.experiment_configuration
        local_configuration["path"]="/"
        local_configuration["use_TLS"]=True
        local_configuration["relative_uri"]=False
        local_configuration["include_subdomain"]=True
        local_configuration["include_port"]=False
        local_configuration["include_subdomain_host_header"]=False
        local_configuration["standard_subdomain"]="www"
        subdomains, hostname, tldomain= request_builder.HTTP1_Request_Builder().parse_host(domain)
        if subdomains=="":
                subdomains="www"
        subdomains=subdomains+"."        
        uri=subdomains+hostname+"."+tldomain
        
        host=None
        request_string, deviation_count, new_uri=request_builder.HTTP1_Request_Builder().generate_request(local_configuration, 443)
        request=request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, domain, local_configuration["standard_subdomain"], host, local_configuration["include_subdomain_host_header"]) #Carefull some hosts expect more
        response_line, response_header_fields, body, measured_times, error_message  = CustomHTTP().http_request(
            host=uri,
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=443,
            host_ip_info=socket_info,
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path=".tranco",    #Transfer to save TLS Keys
        )
        if local_configuration["verbose"]:
            print(request)
            print(response_line)
            print(response_header_fields)
            print()
        
        if response_line!=None:
            response_status_code = response_line["status_code"]
            location=response_header_fields.get('location')
            return response_status_code, location
        else:
            return 999, ""
    
    def add_https_absolute_uri_www_subdomain_incl_host(self, domain, socket_info):
        if not socket_info or isinstance(socket_info, str):
            return 999, ""
        local_configuration=self.experiment_configuration
        local_configuration["path"]="/"
        local_configuration["use_TLS"]=True
        local_configuration["relative_uri"]=False
        local_configuration["include_subdomain"]=True
        local_configuration["include_port"]=False
        local_configuration["include_subdomain_host_header"]=True
        local_configuration["standard_subdomain"]="www"
        subdomains, hostname, tldomain= request_builder.HTTP1_Request_Builder().parse_host(domain)
        if subdomains=="":
                subdomains="www"
        subdomains=subdomains+"."        
        uri=subdomains+hostname+"."+tldomain
        
        host=None
        request_string, deviation_count, new_uri=request_builder.HTTP1_Request_Builder().generate_request(local_configuration, 443)
        request=request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, domain, local_configuration["standard_subdomain"], host, local_configuration["include_subdomain_host_header"]) #Carefull some hosts expect more
        response_line, response_header_fields, body, measured_times, error_message  = CustomHTTP().http_request(
            host=uri,
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=443,
            host_ip_info=socket_info,
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path=".tranco",    #Transfer to save TLS Keys
        )
        if local_configuration["verbose"]:
            print(request)
            print(response_line)
            print(response_header_fields)
            print()
        
        if response_line!=None:
            response_status_code = response_line["status_code"]
            location=response_header_fields.get('location')
            return response_status_code, location
        else:
            return 999, ""


    def add_https_relative_uri_without_subdomain(self, domain, socket_info):
        if not socket_info or isinstance(socket_info, str):
            return 999, ""
        local_configuration=self.experiment_configuration
        local_configuration["path"]="/"
        local_configuration["use_TLS"]=True
        local_configuration["relative_uri"]=True
        local_configuration["include_subdomain"]=True
        local_configuration["include_port"]=False
        local_configuration["include_subdomain_host_header"]=False
        local_configuration["standard_subdomain"]="www"
        subdomains, hostname, tldomain= request_builder.HTTP1_Request_Builder().parse_host(domain)
        if subdomains!="":
                subdomains=subdomains+"."        
        uri=subdomains+hostname+"."+tldomain
        
        host=None
        request_string, deviation_count, new_uri=request_builder.HTTP1_Request_Builder().generate_request(local_configuration, 443)
        request=request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, domain, local_configuration["standard_subdomain"], host, local_configuration["include_subdomain_host_header"]) #Carefull some hosts expect more
        
        response_line, response_header_fields, body, measured_times, error_message  = CustomHTTP().http_request(
            host=uri,
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=443,
            host_ip_info=socket_info,
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path=".tranco",    #Transfer to save TLS Keys
        )
        if local_configuration["verbose"]:
            print(request)
            print(response_line)
            print(response_header_fields)
            print()
        
        if response_line!=None:
            response_status_code = response_line["status_code"]
            location=response_header_fields.get('location')
            return response_status_code, location
        else:
            return 999, ""

    def add_https_relative_uri_www_subdomain_incl_host(self, domain, socket_info):
        if not socket_info or isinstance(socket_info, str):
            return 999, ""
        local_configuration=self.experiment_configuration
        local_configuration["path"]="/"
        local_configuration["use_TLS"]=True
        local_configuration["relative_uri"]=True
        local_configuration["include_subdomain"]=True
        local_configuration["include_port"]=False
        local_configuration["include_subdomain_host_header"]=True
        local_configuration["standard_subdomain"]="www"
        subdomains, hostname, tldomain= request_builder.HTTP1_Request_Builder().parse_host(domain)
        if subdomains=="":
                subdomains="www"
        subdomains=subdomains+"."        
        uri=subdomains+hostname+"."+tldomain
        
        
        host=None
        request_string, deviation_count, new_uri=request_builder.HTTP1_Request_Builder().generate_request(local_configuration, 443)
        request=request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, domain, local_configuration["standard_subdomain"], host, local_configuration["include_subdomain_host_header"]) #Carefull some hosts expect more
        response_line, response_header_fields, body, measured_times, error_message  = CustomHTTP().http_request(
            host=uri,

            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=443,
            host_ip_info=socket_info,
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path=".tranco",    #Transfer to save TLS Keys
        )
        if local_configuration["verbose"]:
            print(request)
            print(response_line)
            #print(response_header_fields)
            print()
        
        if response_line!=None:
            response_status_code = response_line["status_code"]
            location=response_header_fields.get('location')
            return response_status_code, location
        else:
            return 999, ""

    
    def add_new_location(self, domain, new_location, socket_info):
        if not socket_info or isinstance(socket_info, str):
            return 999, ""
        local_configuration=self.experiment_configuration
        local_configuration["path"]=""
        local_configuration["use_TLS"]=True
        local_configuration["relative_uri"]=False
        local_configuration["include_subdomain"]=False
        local_configuration["include_port"]=False
        local_configuration["include_subdomain_host_header"]=False
        local_configuration["standard_subdomain"]=""
        subdomains, hostname, tldomain= request_builder.HTTP1_Request_Builder().parse_host(domain)
        if subdomains=="":
                subdomains="www"
        subdomains=subdomains+"."        
        uri=subdomains+hostname+"."+tldomain
        
        host=uri
        request_string, deviation_count, alt_uri=request_builder.HTTP1_Request_Builder().generate_request(local_configuration, 443)
        request=request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, new_location, local_configuration["standard_subdomain"], host, local_configuration["include_subdomain_host_header"], override_uri=new_location) #Carefull some hosts expect more
        response_line, response_header_fields, body, measured_times, error_message  = CustomHTTP().http_request(
            host=uri,    
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=443,
            host_ip_info=socket_info,
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path=".tranco",    #Transfer to save TLS Keys
        )
        if local_configuration["verbose"]:
            print(request)
            print(response_line)
            #print(response_header_fields)
            print()
        
        if response_line!=None:
            response_status_code = response_line["status_code"]
            location=response_header_fields.get('location')
            return response_status_code, location
        else:
            return 999, ""

    
    
    def add_sub_domain_host(self):
        return 1
    def add_matching_subdomain_host(self):
        return 1

    def upgrade_list(self):
        
        self.data_frame['Socket Info 80'] = self.data_frame['Domain'].apply(self.add_dns_with_standard_subdomain_80)
        self.data_frame['Socket Info 443'] = self.data_frame['Domain'].apply(self.add_dns_with_standard_subdomain_443)
        
       

        self.data_frame['Socket Info WWW 80'] = self.data_frame['Domain'].apply(self.add_dns_with_www_subdomain_80)
        self.data_frame['Socket Info WWW 443'] = self.data_frame['Domain'].apply(self.add_dns_with_www_subdomain_443)
        #print("Test 1")
        self.data_frame['HTTP (TCP, Port 80) leads to 3xx redirect']= self.data_frame.apply(lambda row: self.add_tcp_3xx_redirect(row['Domain'], row['Socket Info 80']),axis=1)
        self.data_frame['HTTP (TCP, Port 80, www) leads to 3xx redirect']= self.data_frame.apply(lambda row: self.add_tcp_3xx_redirect(row['Domain'], row['Socket Info WWW 80']),axis=1)
        
        #print("Test 2") 
        #self.experiment_configuration["verbose"]=True
        #self.data_frame['HTTPS absolute URI, no or given subdomain']= self.data_frame.apply(lambda row: self.add_https_absolute_uri_without_subdomain(row['Domain'], row['Socket Info 443']),axis=1)
        self.data_frame[['HTTPS absolute URI, no or given subdomain, Statuscode', 'HTTPS absolute URI, no or given subdomain, new Location']] = self.data_frame.apply(
            lambda row: self.add_https_absolute_uri_without_subdomain(row['Domain'], row['Socket Info 443']),
            axis=1,
            result_type='expand'
        )
        
        #print("Test 3")
        #self.experiment_configuration["verbose"]=True
        #self.data_frame['HTTPS absolute URI, www or given subdomain']= self.data_frame.apply(lambda row: self.add_https_absolute_uri_www_subdomain(row['Domain'], row['Socket Info WWW 443']),axis=1)
        self.data_frame[['HTTPS absolute URI, www or given subdomain, Statuscode', 'HTTPS absolute URI, www or given subdomain, new Location']] = self.data_frame.apply(
            lambda row: self.add_https_absolute_uri_www_subdomain(row['Domain'], row['Socket Info WWW 443']),
            axis=1,
            result_type='expand'
        )
     
       # self.experiment_configuration["verbose"]=True
        #self.data_frame['HTTPS absolute URI, www or given subdomain, host incl subdomain']= self.data_frame.apply(lambda row: self.add_https_absolute_uri_www_subdomain_incl_host(row['Domain'], row['Socket Info WWW 443']),axis=1)
        self.data_frame[['HTTPS absolute URI, www or given subdomain, host incl subdomain', 'HTTPS absolute URI, www or given subdomain, host incl subdomain, new Location']] = self.data_frame.apply(
            lambda row: self.add_https_absolute_uri_www_subdomain_incl_host(row['Domain'], row['Socket Info WWW 443']),
            axis=1,
            result_type='expand'
        )
        self.data_frame['Try new Location absolute'] = self.data_frame.apply(
            lambda row: self.add_new_location(row['Domain'], row['HTTPS absolute URI, www or given subdomain, host incl subdomain, new Location'], row['Socket Info WWW 443']) if pandas.notna(row['HTTPS absolute URI, www or given subdomain, host incl subdomain, new Location']) else '',
            axis=1
            )  
        
       # self.experiment_configuration["verbose"]=True
        #self.data_frame['HTTPS relative URI, no or standard subdomain']= self.data_frame.apply(lambda row: self.add_https_relative_uri_without_subdomain(row['Domain'], row['Socket Info WWW 443']),axis=1)
        self.data_frame[['HTTPS relative URI, no or standard subdomain, host excl subdomain, statuscode', 'HTTPS relative URI, no or standard subdomain, host excl subdomain, new Location']] = self.data_frame.apply(
            lambda row: self.add_https_relative_uri_without_subdomain(row['Domain'], row['Socket Info WWW 443']),
            axis=1,
            result_type='expand'
            )
     
      #  self.experiment_configuration["verbose"]=True      
        #self.data_frame['HTTPS relative URI, www or standard subdomain, host incl subdomain']= self.data_frame.apply(lambda row: self.add_https_relative_uri_www_subdomain_incl_host(row['Domain'], row['Socket Info WWW 443']),axis=1)
        self.data_frame[['HTTPS relative URI, www or standard subdomain, host incl subdomain, statuscode', 'HTTPS relative URI, www or standard subdomain, host incl subdomain, new Location']] = self.data_frame.apply(
            lambda row: self.add_https_relative_uri_www_subdomain_incl_host(row['Domain'], row['Socket Info WWW 443']),
            axis=1,
            result_type='expand'
            )
        self.data_frame['Try new Location relative'] = self.data_frame.apply(
            lambda row: self.add_new_location(row['Domain'], row['HTTPS relative URI, www or standard subdomain, host incl subdomain, new Location'], row['Socket Info WWW 443']) if pandas.notna(row['HTTPS relative URI, www or standard subdomain, host incl subdomain, new Location']) else '',
        axis=1)  
        
 


        self.data_frame['Socket Info 80'] = self.data_frame['Socket Info 80'].apply(json.dumps)
        self.data_frame['Socket Info 443'] = self.data_frame['Socket Info 443'].apply(json.dumps) 
        self.data_frame['Socket Info WWW 80'] = self.data_frame['Socket Info WWW 80'].apply(json.dumps)
        self.data_frame['Socket Info WWW 443'] = self.data_frame['Socket Info WWW 443'].apply(json.dumps)
        self.data_frame['HTTP (TCP, Port 80) leads to 3xx redirect']= self.data_frame['HTTP (TCP, Port 80) leads to 3xx redirect'].apply(json.dumps)
        self.data_frame['HTTP (TCP, Port 80, www) leads to 3xx redirect']= self.data_frame['HTTP (TCP, Port 80, www) leads to 3xx redirect'].apply(json.dumps)
        #self.data_frame['HTTPS absolute URI, no or given subdomain'] = self.data_frame['HTTPS absolute URI, no or given subdomain'].apply(json.dumps)
        #self.data_frame['HTTPS absolute URI, www or given subdomain'] = self.data_frame['HTTPS absolute URI, www or given subdomain'].apply(json.dumps)
        #self.data_frame['HTTPS absolute URI, www or given subdomain, host incl subdomain'] = self.data_frame['HTTPS absolute URI, www or given subdomain, host incl subdomain'].apply(json.dumps)
        #self.data_frame['HTTPS relative URI, no or standard subdomain'] = self.data_frame['HTTPS relative URI, no or standard subdomain'].apply(json.dumps)
        #self.data_frame['HTTPS relative URI, www or standard subdomain, host incl subdomain'] = self.data_frame['HTTPS relative URI, www or standard subdomain, host incl subdomain'].apply(json.dumps)
       
        self.data_frame['Try new Location absolute'] = self.data_frame['Try new Location relative'].apply(json.dumps)
        self.data_frame['Try new Location relative'] = self.data_frame['Try new Location absolute'].apply(json.dumps)
    
        self.save_data_frame_to_upgraded_list(self.new_path) 

class Target_List_Analyzer(): 
    def __init__(self, old_path, new_path, experiment_configuration):
        self.experiment_configuration = experiment_configuration
        self.data_frame=self.read_host_list_to_dataframe(old_path)
        self.total_requests=len(self.data_frame)
        self.new_path=new_path

    
    def read_host_list_to_dataframe(self, path):
        # Function to parse JSON strings
        def parse_json(json_str):
            try:
                return json.loads(json_str)
            except (json.JSONDecodeError, TypeError):
                return None

        # Read the CSV file with the 'Socket Info' column parsed as JSON
        data_frame = pandas.read_csv(path)#, converters={'Socket Info WWW 443': parse_json})
      #  data_frame['Socket Info WWW 443'] = data_frame['Socket Info WWW 443'].apply(
       #     lambda x: [tuple(sublist) if isinstance(sublist, list) else sublist for sublist in x]
       # )
        return data_frame
        #data_frame['Socket Info WWW 443'] = data_frame['Socket Info WWW 443'].apply(lambda x: tuple(x) if isinstance(x, list) else x)
        #data_frame['Socket Info WWW 443'] = data_frame['Socket Info WWW 443'].apply(lambda x: x if isinstance(x, tuple) else None)


    def save_data_frame_to_upgraded_list(self, new_path, data_frame):
        data_frame.to_csv(new_path,index=False)
        return

    def count_socket_errors(self, data_frame):
        #Returns the count of error per row
        #Assume the Socket Data in the third columne and the next thre following
        
        error_counts = {}
        for column in data_frame.columns[2:6]:  # Column index starts with
            error_per_column = data_frame[column].apply(lambda x: 1 if isinstance(x, str) and 'Errno' in x else 0).sum()
            error_counts[f"{column}"] = error_per_column
        return error_counts

    def count_errors_per_row(self, data_frame):
        error_counts_per_row = data_frame.apply(lambda row: sum(1 for column in row[1:] if isinstance(column, str) and 'Errno' in column), axis=1)
        
        # Initialize a dictionary to count the error occurrences
        error_count_dict = {'0 errors': 0, '1 error': 0, '2 errors': 0, '3 errors': 0, '4 or more errors': 0}
        
        # Count the occurrences based on the error counts
        for count in error_counts_per_row:
            if count == 0:
                error_count_dict['0 errors'] += 1
            elif count == 1:
                error_count_dict['1 error'] += 1
            elif count == 2:
                error_count_dict['2 errors'] += 1
            elif count == 3:
                error_count_dict['3 errors'] += 1
            else:
                error_count_dict['4 or more errors'] += 1
        return error_count_dict

    def count_error_combination(self, data_frame):
        error_counts = {
        'Errors no extra subdomain': data_frame.apply(lambda row: all(isinstance(col, str) and 'Errno' in col for col in [row.iloc[2], row.iloc[3]]), axis=1).sum(),
        'Errors www': data_frame.apply(lambda row: all(isinstance(col, str) and 'Errno' in col for col in [row.iloc[4], row.iloc[5]]), axis=1).sum(),
        'Errors 80': data_frame.apply(lambda row: all(isinstance(col, str) and 'Errno' in col for col in [row.iloc[2], row.iloc[4]]), axis=1).sum(),
        'Errors 443': data_frame.apply(lambda row: all(isinstance(col, str) and 'Errno' in col for col in [row.iloc[3], row.iloc[5]]), axis=1).sum(),
        }
 
        return error_counts

    def analyze_column_statuscode_counts(self, data_frame, column_name):
        if column_name not in data_frame.columns:
            return None
        value_counts = data_frame[column_name].value_counts().to_dict()
        
        return value_counts
 
    def analyze_column_statuscode_by_indexes(self, data_frame, column_indexes):
        results = pandas.DataFrame()
        
        for index in column_indexes:
            if index < len(data_frame.columns):
                column_name = data_frame.columns[index]
                column_counts = self.analyze_column_statuscode_counts(data_frame, column_name)
                if column_counts is not None:
                    # Create a DataFrame with the counts and use the original column name as the header
                    counts_df = pandas.DataFrame({column_name: column_counts})
                    
                    # Concatenate the counts DataFrame with the results DataFrame
                    results = pandas.concat([results, counts_df], axis=1)
                    
        
        results.reset_index(inplace=True)
        results = results.rename(columns = {'index':'Status Code'})
        results.sort_values(by='Status Code', ascending=True, inplace=True) 
        results.reset_index()
        return results

    def group_statuscodes(self, data_frame):
        data_frame.insert(1, 'Leading_Digit', data_frame['Status Code']//100)
        grouped = data_frame.groupby('Leading_Digit')
        result = grouped[data_frame.columns[2:]].agg('sum')
        result.reset_index(inplace=True)
        
        
        return result
    
    
    def filter_dataframe_remove_4_errors(self, data_frame):
        
        error_counts_per_row = data_frame.apply(lambda row: sum(1 for column in row[1:] if isinstance(column, str) and 'Errno' in column), axis=1)
        
        
        filtered_df = data_frame[error_counts_per_row < 4]
        
        return filtered_df

    def filter_dataframe_remove_all459(self, data_frame, columns_to_check):
        # Function to check if a number has a leading digit of 4, 5, or 9
        def has_leading_digit_4_5_9(number):
            if isinstance(number, int):
                first_digit = number//100
                return first_digit in [4, 5, 9]
            return False
        print(data_frame.columns)
        mask = data_frame.iloc[:, columns_to_check].apply(lambda x: x.map(has_leading_digit_4_5_9)).all(axis=1)

        
        filtered_df = data_frame[~mask]

        return filtered_df
    


    def clean_up_column(self, data_frame, column_indices):
   
        
        def convert_to_int(value):
            try:
                # If the value is already an integer, return it as is
                if isinstance(value, int):
                    return value
                
                # If the value is a float or a string representation of a float, convert it to an integer
                if isinstance(value, float) or (isinstance(value, str) and value.replace('.', '', 1).isdigit()):
                    return int(float(value))
                
                # If the value is a list represented as a string, parse it and convert its first element to an integer
                if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
                    try:

                        value_list = eval(value)  # Safely evaluate the string as a Python expression
                        if isinstance(value_list, list) and len(value_list) > 0:
                            return convert_to_int(value_list[0])
                    except (SyntaxError, ValueError):
                        pass

                # If the value is a string that represents an integer, convert it to an integer
                if isinstance(value, str) and value.isdigit():
                    return int(value)
                
                # If none of the above conditions match, return None
                print("Other Type", type(value))
                return None
            
            except (ValueError, TypeError):
                return None

    
        for index in column_indices:
            if index < len(data_frame.columns):
                column_name = data_frame.columns[index]
                data_frame[column_name] = data_frame[column_name].apply(lambda x: convert_to_int(x))
        
        return data_frame
    
    
    def add_use_www_column(self,data_frame):
        
        data_frame=data_frame.copy()
        no_sub_error = data_frame.apply(lambda row: all(isinstance(col, str) and 'Errno' in col for col in [row.iloc[2], row.iloc[3]]), axis=1)

        
        www_error= data_frame.apply(lambda row: all(isinstance(col, str) and 'Errno' in col for col in [row.iloc[4], row.iloc[5]]), axis=1)

        data_frame.loc[:, 'use_www'] = "indifferent"

        # Update "use_www" column based on the conditions
        data_frame.loc[no_sub_error, 'use_www'] = True
        data_frame.loc[www_error, 'use_www'] = False

        return data_frame


        """  def analyze_dns_data(self, data_frame):
        total_entries=len(data_frame)
        error_count = data_frame[data_frame['Socket Info WWW 443'].astype(str).str.contains('Errno')].shape[0]
        error_codes = data_frame[data_frame['Socket Info WWW 443'].astype(str).str.contains('Errno')]['Socket Info WWW 443'].astype(str).str.extract(r'\[Errno (-\d+)\]')
        error_share = (error_count / total_entries) * 100
        print()
        print(f"Failed Requests: {error_count}")
        print(f"Failure Share (%): {error_share:.1f}%")
        print("Error Codes and Their Counts:")
        print(error_codes[0].value_counts())
        return data_frame[~data_frame['Socket Info WWW 443'].astype(str).str.contains('Errno')] """

        """     def analyze_http_response(self, data_frame, column_name):
        data_frame['Status_Code'] = data_frame[column_name].str.extract(r'\[(\d+),')[0]
        data_frame['Location'] = data_frame[column_name].str.extract(r'"(https?://[^"]+)"')
        # Count status code and print the counts
        status_counts = data_frame['Status_Code'].value_counts()
        print("Status Code Counts:")
        print(status_counts)

        # Remove the 'Status_Code' column
        data_frame.drop(columns=['Status_Code'], inplace=True)
        return data_frame """
    def compare_columns_and_create_new(self, data_frame, true_column_index, false_column_index, new_column_name, insert_index, leading_digit):
        # Function to compare values in the specified columns
        def compare_values(row):
            true_value = row.iloc[true_column_index]
            false_value = row.iloc[false_column_index]

            if true_value//100 == leading_digit and false_value//100 == leading_digit:
                return 'indifferent'
            elif true_value//100 == leading_digit:
                return True
            elif false_value//100 == leading_digit:
                return False
            else:
                return 'unknown'

        # Apply the comparison function to each row
        data_frame[new_column_name] = data_frame.apply(compare_values, axis=1)

       
        # Return the DataFrame with the new column
        return data_frame
    
    def check_columns_for_leading_digit(self, data_frame, column_indexes, new_column_name, leading_digit):
     
        def has_leading_digit(value):
            if isinstance(value, int) and value // 100 == leading_digit:
                return True
            return False

       
        result = data_frame.iloc[:, column_indexes].apply(lambda column: column.apply(has_leading_digit).any(), axis=1)


        data_frame[new_column_name] = result

        return data_frame
    
    
    def compare_columns_and_create_new_true_false(self, data_frame, true_column_index, false_column_index, new_column_name, insert_index):
        # Function to compare values in the specified columns
        def compare_values(row):
            true_value = row.iloc[true_column_index]
            false_value = row.iloc[false_column_index]

            if true_value == True and false_value == True:
                return 'indifferent'
            elif true_value == True:
                return 'relative'
            elif false_value == True:
                return 'absolute'
            else:
                return 'unknown'

        # Apply the comparison function to each row
        data_frame[new_column_name] = data_frame.apply(compare_values, axis=1)
        #data_frame.insert(insert_index, new_column_name, data_frame.apply(compare_values, axis=1))

        return data_frame
    
    
    
    
    def count_occurrences_per_column(self, data_frame, column_indices):
        # Create an empty DataFrame with rows for each result
        result_df = pandas.DataFrame(columns=['Result'], data=['True', 'False', 'Indifferent', 'Unknown', 'Relative', 'Absolute'])

        # Iterate through the specified columns
        for index in column_indices:
            column_name = data_frame.columns[index]
            counts = data_frame[column_name].value_counts()

            # Create a DataFrame with counts for each unique value
            counts_df = pandas.DataFrame(columns=[column_name], data=[counts.get(True, 0), counts.get(False, 0), counts.get('indifferent', 0), counts.get('unknown', 0), counts.get('relative', 0), counts.get('absolute', 0)])

            # Append the counts to the result DataFrame
            result_df = pandas.concat([result_df, counts_df], axis=1)

        return result_df
    
    def extract_sublist(self,data_frame, column_indices, condition_column, condition, n):
        # Filter rows where the specified condition_column matches the condition value
        filtered_rows = data_frame[data_frame.iloc[:, condition_column].isin([condition])]#, 'indifferent'

        # Extract the first 'n' entries from the specified column indices in the filtered rows
        extracted_data = {}
        for column_index in column_indices:
            column_name = data_frame.columns[column_index]
            extracted_values = filtered_rows.iloc[:n, column_index].tolist()
            extracted_data[column_name] = extracted_values

        # Create a DataFrame from the extracted data
        result_df = pandas.DataFrame(extracted_data)

        return result_df


    def analyze_data(self):
        
        print("Total number of Entries: ", self.total_requests)       
        #Analyze DNS/Socket Data
        print("DNS/Socket Errors per Options")
        socket_errors=self.count_socket_errors(self.data_frame)
        print(socket_errors)
        print("DNS Errors per Host")
        socket_errors_per_host=self.count_errors_per_row(self.data_frame)
        print(socket_errors_per_host)
        print("Filtered all 4 errors:")
        filtered_data_frame=self.filter_dataframe_remove_4_errors(self.data_frame)
        len_filtered_data_frame=len(filtered_data_frame)
        print("Old Length", self.total_requests)
        print("New Length", len_filtered_data_frame)
        print("DNS/Socket Errors per Options")
        socket_errors=self.count_socket_errors(filtered_data_frame)
        print(socket_errors)
        print("DNS Errors per Host")
        socket_errors_per_host=self.count_errors_per_row(filtered_data_frame)
        print(socket_errors_per_host)
        socket_error_combination=self.count_error_combination(filtered_data_frame)
        print(socket_error_combination)
        
        ##Analyze the http probes
        print("Status Code Statistcs")
         #Try to reach redirect value
        
        column_indexes=[6, 7, 8, 10 ,12,15,17]
        cleaned_df=self.clean_up_column(filtered_data_frame, column_indexes)
        status_code_df=self.analyze_column_statuscode_by_indexes(cleaned_df,column_indexes)
        print(status_code_df)
        status_code_statitics=self.group_statuscodes(status_code_df)
        print(status_code_statitics)
        #Delete all entries which cause a 4,5 or 9 code on all columns
        df459=self.filter_dataframe_remove_all459(cleaned_df, column_indexes)
        len_df459=len(df459)
        print("Old Length", len_filtered_data_frame)
        print("New Length", len_df459)

        status_code_df2=self.analyze_column_statuscode_by_indexes(df459,column_indexes)
        print(status_code_df2)
        status_code_statitics2=self.group_statuscodes(status_code_df2)
        print(status_code_statitics2)

        
        df_responses=self.add_use_www_column(df459)
        
        df_rel_sub=self.compare_columns_and_create_new(df_responses,10,8,"Use_Sub_www(Rel)",3,2)
        df_rel_host=self.compare_columns_and_create_new(df_rel_sub, 12, 10, "Use_Host_Sub(Rel)", 4, 2)
        #df_abs_sub=self.compare_columns_and_create_new(df_rel_host, true_column_index, false_column_index, new_column_name, insert_index, leading_digit)
        df_abs_host=self.compare_columns_and_create_new(df_rel_host, 17, 15, "Use_Host_Sub(Abs)", 5, 2)
        df_rel=self.check_columns_for_leading_digit(df_abs_host, [8,10,12], "Relative URI", 2)
        df_abs=self.check_columns_for_leading_digit(df_rel, [15,17], "Absolute URI", 2)
        df_uri=self.compare_columns_and_create_new_true_false(df_abs, 24, 25, "URI_Option", 6)
        column_indexes=[20, 21, 22, 23 , 24, 25, 26]
        state_statistics=self.count_occurrences_per_column(df_uri, column_indexes)
        self.save_data_frame_to_upgraded_list("State_Statistics.csv", state_statistics)
        self.save_data_frame_to_upgraded_list("new.csv", df_uri)

        self.save_data_frame_to_upgraded_list("status_code_statistics.csv", status_code_statitics)
        self.save_data_frame_to_upgraded_list("status_codes.csv", status_code_df)
        self.save_data_frame_to_upgraded_list("status_code_statistics2.csv", status_code_statitics2)
        self.save_data_frame_to_upgraded_list("status_codes2.csv", status_code_df2)
        self.save_data_frame_to_upgraded_list(self.new_path, df_responses)
        column_indexes=[0, 1, 21, 22, 23 , 24, 25, 26]
        new_list=self.extract_sublist(df_uri, column_indexes, 17, 200, 1000)
        self.save_data_frame_to_upgraded_list("target_list_tls_rel_sub_subhost.csv", new_list)
        return 


    def filter_data(self):
        df_filtered_errors=self.analyze_dns_data(self.data_frame)
        print("Entries with succesful DNS Lookup: ", len(df_filtered_errors))
        df_responses=self.analyze_http_response(df_filtered_errors.copy(), 'HTTPS relative URI, www or standard subdomain, host incl subdomain')
        self.experiment_configuration["verbose"]=True   
       
        df_responses['Try new Location'] = df_responses.apply(
        lambda row: self.add_https_relative_uri_www_subdomain_incl_host(row['Location'], row['Socket Info WWW 443']) if pandas.notna(row['Location']) else '',
        axis=1)  
        df_responses['Try new Location'] = df_responses['Try new Location'].apply(json.dumps)
    


        self.save_data_frame_to_upgraded_list(self.new_path, df_responses)
        return