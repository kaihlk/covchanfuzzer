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
        ubdomains=subdomains+"."        
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
        if not socket_info or isinstance(socket_info, str):
            return 0
        local_configuration=self.experiment_configuration
        local_configuration["path"]="/"
        request_string, deviation_count, new_uri=request_builder.HTTP1_Request_Builder().generate_request(self.experiment_configuration, 80)
        subdomain=""
        request=request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, domain, subdomain)
        print(request)
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
        print(response_line)
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
        
        subdomains, hostname, tldomain= request_builder.HTTP1_Request_Builder().parse_host(domain)
        
        subdomains=subdomains+"."        
        uri=subdomains+hostname+"."+tldomain

       
        
        request_string, deviation_count, new_uri=request_builder.HTTP1_Request_Builder().generate_request(self.experiment_configuration, 443)
        
        request=request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, domain, subdomains) #Carefull some hosts expect more
        print(request)
        response_line, response_header_fields, body, measured_times, error_message  = CustomHTTP().http_request(
            host=domain,
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=443,
            host_ip_info=socket_info,
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path=".tranco",    #Transfer to save TLS Keys
        )
        print(response_line)
        
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
        local_configuration["target_add_www"]==True

        subdomains, hostname, tldomain= request_builder.HTTP1_Request_Builder().parse_host(domain)
        if subdomains=="":
            subdomains="www"
        
        request_string, deviation_count, new_uri=request_builder.HTTP1_Request_Builder().generate_request(self.experiment_configuration, 443)
        
        request=request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, domain, subdomains, host=subdomains+"."+domain) #Carefull some hosts expect more
        print(request)
        response_line, response_header_fields, body, measured_times, error_message  = CustomHTTP().http_request(
            host=domain,
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=443,
            host_ip_info=socket_info,
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path=".tranco",    #Transfer to save TLS Keys
        )
        print(response_line)
        
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
        local_configuration["target_add_www"]==False

        subdomains, hostname, tldomain= request_builder.HTTP1_Request_Builder().parse_host(domain)
        
        
        request_string, deviation_count, new_uri=request_builder.HTTP1_Request_Builder().generate_request(self.experiment_configuration, 443)
        
        request=request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, domain, subdomains) #Carefull some hosts expect more
        print(request)
        response_line, response_header_fields, body, measured_times, error_message  = CustomHTTP().http_request(
            host=domain,
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=443,
            host_ip_info=socket_info,
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path=".tranco",    #Transfer to save TLS Keys
        )
        print(response_line)
        
        if response_line!=None:
            response_status_code = response_line["status_code"]
            location=response_header_fields.get('location')
            return response_status_code, location
        else:
            return 999, ""

    def add_https_relative_uri_www_subdomain(self, domain, socket_info):
        if not socket_info or isinstance(socket_info, str):
            return 999, ""
        local_configuration=self.experiment_configuration
        local_configuration["path"]="/"
        local_configuration["use_TLS"]=True
        local_configuration["relative_uri"]=True
        local_configuration["include_subdomain"]=True
        local_configuration["include_port"]=False
        local_configuration["target_add_www"]==True

        subdomains, hostname, tldomain= request_builder.HTTP1_Request_Builder().parse_host(domain)
        
        if subdomains=="":
            subdomains="www"

        request_string, deviation_count, new_uri=request_builder.HTTP1_Request_Builder().generate_request(self.experiment_configuration, 443)
        
        request=request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, domain, subdomains, host=subdomains+"."+domain) #Carefull some hosts expect more
        print(request)
        response_line, response_header_fields, body, measured_times, error_message  = CustomHTTP().http_request(
            host=domain,
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=443,
            host_ip_info=socket_info,
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path=".tranco",    #Transfer to save TLS Keys
        )
        print(response_line)
        
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
        
        #self.data_frame['Socket Info 80'] = self.data_frame['Domain'].apply(self.add_dns_with_standard_subdomain_80)
        self.data_frame['Socket Info 443'] = self.data_frame['Domain'].apply(self.add_dns_with_standard_subdomain_443)
        
       

        #self.data_frame['Socket Info www 80'] = self.data_frame['Domain'].apply(self.add_dns_with_www_subdomain_80)
       # self.data_frame['Socket Info www 443'] = self.data_frame['Domain'].apply(self.add_dns_with_www_subdomain_443)
        
        #self.data_frame['HTTP (TCP, Port 80) leads to 3xx redirect']= self.data_frame.apply(lambda row: self.add_tcp_3xx_redirect(row['Domain'], row['Socket Info 80']),axis=1)
        self.data_frame['HTTPS absolute URI, no or standard subdomain']= self.data_frame.apply(lambda row: self.add_https_absolute_uri_without_subdomain(row['Domain'], row['Socket Info 443']),axis=1)
        self.data_frame['HTTPS absolute URI, www or standard subdomain']= self.data_frame.apply(lambda row: self.add_https_absolute_uri_www_subdomain(row['Domain'], row['Socket Info 443']),axis=1)
        self.data_frame['HTTPS relative URI, no or standard subdomain']= self.data_frame.apply(lambda row: self.add_https_relative_uri_without_subdomain(row['Domain'], row['Socket Info 443']),axis=1)
        self.data_frame['HTTPS relative URI, www or standard subdomain']= self.data_frame.apply(lambda row: self.add_https_relative_uri_www_subdomain(row['Domain'], row['Socket Info 443']),axis=1)
 

        #self.data_frame['Socket Info 80'] = self.data_frame['Socket Info 80'].apply(json.dumps)
        self.data_frame['Socket Info 443'] = self.data_frame['Socket Info 443'].apply(json.dumps)
        self.data_frame['HTTPS absolute URI, no or standard subdomain'] = self.data_frame['HTTPS absolute URI, no or standard subdomain'].apply(json.dumps)
        self.data_frame['HTTPS absolute URI, www or standard subdomain'] = self.data_frame['HTTPS absolute URI, www or standard subdomain'].apply(json.dumps)
        self.data_frame['HTTPS relative URI, no or standard subdomain'] = self.data_frame['HTTPS relative URI, no or standard subdomain'].apply(json.dumps)
        self.data_frame['HTTPS relative URI, www or standard subdomain'] = self.data_frame['HTTPS relative URI, www or standard subdomain'].apply(json.dumps)
      #  self.data_frame['Socket Info www 80'] = self.data_frame['Socket Info www 80'].apply(json.dumps)
      #  self.data_frame['Socket Info www 443'] = self.data_frame['Socket Info www 443'].apply(json.dumps)

        self.save_data_frame_to_upgraded_list(self.new_path) 