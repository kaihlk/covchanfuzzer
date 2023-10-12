# http1_covered_channels.py

# Definition of functions to generate cover channels in http/1.1 requests
# TODO HTTP/2 request generation, with method:

import random

from urllib.parse import quote



class HTTP1_Request_Builder:
    def __init__(self): 
        self.host_placeholder= ">>HOST_PLACEHOLDER<<"
        self.domain_placeholder=">>DOMAIN_PLACEHOLDER<<"
        self.subdomain_placeholder=">>SUDBDOMAIN_PLACEHOLDER<<"
        self.generated_request=""
        self.cc_uri_post_generation=False
        self.default_headers_sets = {
            # The request line and the host and the url field must be generated and inserted in the functions
            "curl_HTTP/1.1(TLS)": [
                ("User-Agent", "curl/7.87.0",),
                ("Accept", "*/*",),
            ],
            "firefox_HTTP/1.1": [
                # The field with the Host and the url must be generated and inserted in the functions
                (
                    "User-Agent",
                    "Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0",
                ),
                (
                    "Accept",
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                ),
                ("Accept-Encoding", "gzip, deflate"),
                ("Accept-Language", "en-US,en;q=0.5"),
                ("DNT", "1"), #Do not track 1 or 0
                ("Connection", "keep-alive"),
                #("Upgrade-Insecure-Requests", "1"), # Request the server to upgrade to https if possible, this may affect the servers response, so by now it is deactivated
            ],
            "firefox_HTTP/1.1_TLS": [
                # The field with the Host and the url must be generated and inserted in the functions
                (
                    "User-Agent",
                    "Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0",
                ),
                (
                    "Accept",
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                ),
                ("Accept-Encoding", "gzip, deflate, br"),
                ("Accept-Language", "en-US,en;q=0.5"),
                ("DNT", "1"), #Do not track 1 or 0
                ("Connection", "keep-alive"),
                ("Upgrade-Insecure-Requests", "1"), # Request the server to upgrade to https if possible, at TLS Mode should be no problem
                ("Sec-Fetch-Dest", "document"), #destination of the fetch request type document
                ("Sec-Fetch-Mode", "navigate"), # naviagion request, typically by user action
                ("Sec-Fetch-Site", "cross-site"), # Context of the request, origin from another site
            ],
            "chromium_HTTP/1.1":  [
                # The field with the Host and the url must be generated and inserted in the functions
                ("Connection", "keep-alive"),
                (
                    "User-Agent",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36", #Linux OP
                ),
                (
                    "Accept",
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                ),
                ("Accept-Encoding", "gzip, deflate"),
                ("Accept-Language", "en-US,en;q=0.9"),
            ],
            "chromium_HTTP/1.1_TLS":  [
                # The field with the Host and the url must be generated and inserted in the functions
                ("sec-ch-ua", '"Chromium";v="115", "Not/A)Brand";v="99"'),  #hint to provide information about user-agent without exposing it, carefull with the " "
                ("sec-ch-ua-mobile:", "?0"), # no information if the user-agent is a mobile device
                ("sec-ch-ua-platform", "Linux"), # Hint to the OS
                ("Upgrade-Insecure-Requests", "1"), # Request the server to upgrade to https if possible, at TLS Mode should be no problem
                (
                    "User-Agent",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36", #Linux OP
                ),
                (
                    "Accept",
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                ),
                ("Sec-Fetch-Site", "none"), # Context of the request, same origin 
                ("Sec-Fetch-Mode", "navigate"), # naviagion request, typically by user action
                ("Sec-Fetch-User", "?1"), # indicates that the user is activly browsing
                ("Sec-Fetch-Dest", "document"), #destination of the fetch request type document
                ("Accept-Encoding", "gzip, deflate"),
                ("Accept-Language", "en-US,en;q=0.9"),

            ],
        }


    def get_cc_uri_post_generation(self):
        return self.cc_uri_post_generation


    def extract_new_uri(self, request):
        parts = request.split(' ')

        # The URI is the second part after the first space
        if len(parts) >= 2:
            new_uri = parts[1]
        else:
            print("URI not found in the request.")
        return new_uri

    def parse_host(self,host):
        #Initialize variables
        subdomains = ""
        hostname = ""
        domain = ""
        
        parts = host.split(".")

        if len(parts) >= 2:
            tldomain = parts[-1]
            hostname = parts[-2]
            subdomains=".".join(parts[:-2])  #Multiple Subodmains possible

        else: 
            print("Unable to parse host")
            raise ValueError("Unable to parse host")
  

        return subdomains, hostname, tldomain

        #host may be part of the uri
    def parse_uri(self, uri, host):
        '''Parse host uris'''
        # Initialize variables
        scheme = ""
        subdomain = ""
        hostname = ""
        domain = ""
        port = ""
        path = ""
        
        # Check if the host contains a scheme
        if "://" in uri:
            # Split the host into scheme and the rest of the URL
            parts = host.split("://", 1)
            scheme = parts[0]
            remaining = parts[1]
        else:
            remaining = uri

        # Split the remaining URL into subdomain, hostname, domain, and port (if present)
        parts = remaining.split("/", 1)
        if len(parts) == 2:
            remaining, path = parts

        subdomain_parts = remaining.split(".", 1)
        if len(subdomain_parts) == 2:
            subdomain = subdomain_parts[0]
            remaining = subdomain_parts[1]

        hostname_parts = remaining.split(".", 1)
        if len(hostname_parts) == 2:
            hostname = hostname_parts[0]
            domain_port = hostname_parts[1].split(":", 1)
            domain = domain_port[0]
            if len(domain_port) == 2:
                port = domain_port[1]
        if host.lower()=="localhost":
            hostname = host
        # Return the extracted parts as a tuple
     
        return scheme, subdomain, hostname, domain, port, path

    def build_request_line(self, port, method, path, headers, scheme, fuzzvalue, relative_uri=True, include_subdomain=False, include_port=False, protocol="HTTP/1.1"):
                # Build the request_line from the provided arguments
        if relative_uri==False:        
            #Scheme:
            if scheme=="":
                if port==443:
                    scheme="https://"
                else:
                    scheme="http://"
                #subdomains                      
            if include_subdomain:
               subdomain=self.subdomain_placeholder+"."
            else:
               subdomain="" 
            #Port
            if include_port==True:
                new_port=":"+str(port)
            else:
                new_port=""
            #absolute uri
            new_uri =scheme + subdomain + self.domain_placeholder + new_port + path
        else:
            new_uri=path

        request_line = f"{method} {new_uri} {protocol}\r\n"

        return request_line, new_uri   

    
    
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        '''Generation of request package, CCs mut implement this '''

        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))
        # Build the request from request line and headersport
        scheme=""
        request_line, new_uri = self.build_request_line(port, method, path, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)
        request_string = request_line
        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        request_string += "\r\n"
        deviation_count=0     
        return request_string, deviation_count, new_uri

    def generate_request(self, experiment_configuration, selected_port, new_fuzz_value=0):
        
        #host=host_data["host"]
        port=selected_port
        path=experiment_configuration["path"]
        method=experiment_configuration["method"]
        headers=experiment_configuration["headers"]
        standard_headers=experiment_configuration["standard_headers"]
        content=experiment_configuration["content"]
        #Allow more flexibility in the fuzzing
        if new_fuzz_value==0:
            fuzz_value=experiment_configuration["min_fuzz_value"]
        else: fuzz_value=new_fuzz_value
        
        relative_uri=experiment_configuration["relative_uri"]
        include_subdomain=experiment_configuration["include_subdomain"]
        include_port=experiment_configuration["include_port"]
        protocol=experiment_configuration["HTTP_version"]
  
         # Check if headers are provided elsewise take default headers
        if headers is None: 
            if standard_headers in self.default_headers_sets:
                headers= self.default_headers_sets[standard_headers].copy()       
            else:
                headers = self.default_headers_sets["curl_HTTP/1.1(TLS)"].copy()
            # Create a copy to avoid modifying the original list


        return self.generate_cc_request(port, method, path, headers, content, fuzz_value, relative_uri, include_subdomain, include_port, protocol)

    def replace_host_and_domain(self, prerequest, domain, standard_subdomain="", host=None, include_subdomain_host_header=False, override_uri=""):
            try:
                subdomains, hostname, tldomain =self.parse_host(domain)
                if subdomains=="":
                    subdomains=standard_subdomain            
                
                new_domain=hostname+"."+tldomain
                if host==None:
                    if include_subdomain_host_header==True:
                        host=subdomains+"."+new_domain
                    else: 
                        host=domain
                if override_uri!="":
                    new_domain=override_uri
                    prerequest=prerequest.replace('https://', '',1)
                #This inserts the sudomain in the uri    
                request=prerequest.replace(self.subdomain_placeholder,subdomains)
                request=request.replace(self.domain_placeholder, new_domain)
                #The Subdomain inclusion for the host header field takes places here, 
                request=request.replace(self.host_placeholder, host)

                deviation_count=0

                new_uri=self.extract_new_uri(request)
                return request, deviation_count, new_uri
            except Exception as ex:
                print(ex)



###Domain Handling
#CC builds complete Request,
#CC defines 3 Placeholders,uri_subdomain, hostname(host+topleveldomain), host (may include subdomain)
#CC defines port, path and schemme, here is the checked if relative or absolute uri should be used
#RB take URI and parse it, extract subdomain, hostname, 
# replaces them
