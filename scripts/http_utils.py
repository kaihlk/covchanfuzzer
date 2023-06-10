# http_utils.py
# Definition of functions to generate cover channels in http/1.1 requests
#TODO HTTP/2 request generation, with method:

import random
from urllib.parse import quote

def _init_(self):
        #Definition of standard HTTP request like a Chrome Browser on a Windows OS would send
        self.default_headers = [
            #The field with the Host and the url must be generated and inserted in the functions
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
            ('Accept-Encoding', 'gzip, deflate, br'),
            ('Accept-Language', 'en-US,en;q=0.9'),
            ('Connection', 'keep-alive')
        ]



def parse_host(host):
    # Initialize variables
    scheme = ''
    subdomain = ''
    hostname = ''
    domain = ''
    port = ''
    path = ''

    # Check if the host contains a scheme
    if "://" in host:
        # Split the host into scheme and the rest of the URL
        parts = host.split("://", 1)
        scheme = parts[0]
        remaining = parts[1]
    else:
        remaining = host

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

    # Return the extracted parts as a tuple
    return scheme, subdomain, hostname, domain, port, path

def random_switch_case_of_char_in_string(self, original_string, fuzzvalue):
    modified_string=''
    deviation_count=0
    # Randomly change the case of the field name
    for c in original_string:
        #The value of the probabiltiy to change a char is defined by the fuzzvalue
        #the char functions doesn't affect signs and symbols
        if random()<fuzzvalue:
            if c.isupper():
                modified_string.join(c.lower())
                deviation_count=+1
            elif c.islower:
                modified_string.join(c.upper())
                deviation_count=+1
            else:
                modified_string.join(c)
    return modified_string, deviation_count

#Generation of request package without insertion of a covert channel 
def generate_standard_request(self, host, url='/', method="GET", headers=None, fuzzvalue=None):
    
    # Check if headers are provided elsewise take default headers
    if headers is None:
        headers = self.default_headers
    else:
        # Create a copy to avoid modifying the original list
        headers = headers.copy()  
    
    # Insert the Host header at the beginning of the list
    headers.insert(0, ('Host', host))  
    
    # Build the request_line from the provided arguments
    request_line = f"{method} {url} HTTP/1.1\r\n"

    # Build the request from request line and headers
    request_string = request_line
    for header in headers:
        request_string += f"{header[0]}: {header[1]}\r\n"
    
    # Add the ending of the request
    request_string += "\r\n"
    
    # No deviation
    deviation_count = 0
    return request_string, deviation_count


#Covertchannel suggested by Kwecka et al: Case-insensitivity of header key names
#fuzzvalue defines the probability that a character of a header field is changed
def generate_request_CC_case_insensitivity(self, host, url='/', method="GET", headers=None, fuzzvalue=0.5):
    
    # Check fuzzvalue
    if fuzzvalue < 0 or fuzzvalue > 1:
        raise ValueError("fuzzvalue must be between 0 and 1.")

    # Check if headers are provided elsewise take default headers
    if headers is None:
        headers = self.default_headers
    else:
        # Create a copy to avoid modifying the original list
        headers = headers.copy()

    
    # Insert the Host header at the beginning of the list
    headers.insert(0, ('Host', host))  

    # Build the request_line from the provided arguments
    request_line = f"{method} {url} HTTP/1.1\r\n"

    #Define Request first line
    request_string = request_line

    #Iterate over the header fields
    for header in headers:
        field_name, field_value = header
        modified_field_name, deviation_count=self.random_switch_case_of_char_in_string(field_name, fuzzvalue)
        #Build request string from modified field name, :, and field value
        request_string += f"{modified_field_name}: {field_value}\r\n"

    #Add ending of request
    request_string += "\r\n"

    return request_string, deviation_count


#Covertchannel suggested by Kwecka et al: Linear whitespacing
#fuzzvalue defines the propability whether a value is changed and how many whitespaces/tabs/newlines are added 
#Possible endless Loop, here is CC to learn something about the maximum size of the Request size
def generate_request_CC_random_whitespace(self, host, url='/', method="GET", headers=None, fuzzvalue=0.9):
    
    # Check if headers are provided elsewise take default headers
    if headers is None:
        headers = self.default_headers
    else:
        # Create a copy to avoid modifying the original list
        headers = headers.copy()  
    
    # Insert the Host header at the beginning of the list
    headers.insert(0, ('Host', host))  
    
    # Build the request_line from the provided arguments
    request_line = f"{method} {url} HTTP/1.1\r\n"
    deviation_count = 0
    request_string=request_line
    #Iterate over header fields
    for header in headers: 
        field_name, field_value = header
        #Random choice if value is changed
        if random()<fuzzvalue:
            #Create a string with random number of Whitespaces and Tabulators, third possible char?  ????
            whitespace=''
            while random()<fuzzvalue:
                 #Random Choice from Tabulator, Whitespace, Newline+Whitespace
                random_string=random.choice(['\t', ' ', '/r/n '])
                whitespace+=random_string
                deviation_count+=1
            #Add the whitespace string at the end of the value
            field_value += whitespace     
        #Build the line of the request string
        request_string += f"{field_name}: {field_value}\r\n"
    
    #End the request String
    request_string += "\r\n"

    return request_string, deviation_count


#Covertchannel suggested by Kwecka et al: Reordering of Headerfields#
# Fuzz Parameter no effect, due to Implementation of Shuffle

def generate_request_CC_reordering_headerfields(self, host, url='/', method="GET", headers=None, fuzzvalue=None):
    
    # Check if headers are provided elsewise take default headers
    if headers is None:
        headers = self.default_headers
    else:
        # Create a copy to avoid modifying the original list
        headers = headers.copy()  
    
    # Insert the Host header at the beginning of the list
    headers.insert(0, ('Host', host))  
    
    # Build the request_line from the provided arguments
    request_line = f"{method} {url} HTTP/1.1\r\n"
    
    deviation_count = 0

    # Shuffle the header fields randomly
    # Reorder the header fields, Note: the RandomValue random.shuffle(List, RandomValue[0,1]) is deprecated (Python 3.9)
    shuffled_headers = headers[:]
    random.shuffle(shuffled_headers)
    
    # Iterate over the shuffled headers and compare with the original order
    for shuffled_header, original_header in zip(shuffled_headers, headers):
        # Check if the header is not 'Host' and the order has deviated and increment the deviation count    
        if shuffled_header != original_header:
            deviation_count += 1
        # Build the request_string with the shuffeled_header  
        request_string += f"{shuffled_header[0]}: {shuffled_header[1]}\r\n"
    # Add the final line break to the request string    
    request_string += "\r\n"

    # Return the request string and deviation count
    return request_string, deviation_count




#URI in the request line!!!!!!!!!!
#Covertchannel suggested by Kwecka et al: Uniform Ressource Identifiers
# Empty or not given port assune 80
# http as scheme name and host name case insenitivity
# empty absolute path interpreta as "/"
# Ascci Hex Hex Representation  ---> This is not working like suggested!!!!
#  Hex representation can  7e or 7E 
###Not working properly
### need testing
### add fuzzing value
def generate_request_CC_change_uri_representation(self, host, port=80, url='', method="GET", headers=None, fuzzvalue=None):
    # Check if headers are provided elsewise take default headers
    if headers is None:
        headers = self.default_headers
    else:
        # Create a copy to avoid modifying the original list
        headers = headers.copy()  
    
    # Insert the Host header at the beginning of the list
    headers.insert(0, ('Host', host)) 

    # Parse the given host
    scheme, subdomain, hostname, domain, hostport, path = parse_host(host)

    #Build a new URL from the given host
    deviation_count = 0

    if scheme=='':
        scheme='http'
    new_scheme=random.choice(scheme+'://', '', 'http://', 'https://')
    if new_scheme!=scheme:
        deviation_count+=1

    if subdomain=='':
        subdomain='www'
    new_subdomain=random.choice(subdomain+'.', '', 'www.')
    if new_subdomain!=subdomain:
        deviation_count+=1

    new_hostname=random.choice(hostname+'.'+domain,'')
    if new_hostname!=hostname+'.'+subdomain:
        deviation_count+=1

    if hostport=='':
        hostport=port
    new_port=random.choice('',':'+hostport,':'+port, ':'+'80', ':'+'443', ':'+random.randint(0, 65535))
    if new_port!=hostport:
        deviation_count+=1

    new_path=random.choice('','/','/'+path)
    if new_path!=path:
        deviation_count+=1
    
    new_url=new_scheme+new_subdomain+new_hostname+new_port+new_path 

    request_line = f"{method} {new_url} HTTP/1.1\r\n"


    for header in headers:
        request_string += f"{header[0]}: {header[1]}\r\n"

    request_string += "\r\n"

    return request_string, deviation_count


#CC with addional changes in the URL Case insensitvity 
def generate_request_CC_change_uri_case_insensitivity(self, host, port=80, url='', method="GET", headers=None, fuzzvalue=None):
    # Check if headers are provided elsewise take default headers
    if headers is None:
        headers = self.default_headers
    else:
        # Create a copy to avoid modifying the original list
        headers = headers.copy()  
    
    # Insert the Host header at the beginning of the list
    headers.insert(0, ('Host', host)) 

    # Parse the given host
    scheme, subdomain, hostname, domain, hostport, path = parse_host(host)

    #Build a new URL from the given host, add some deviation if not all fields are provided

    if scheme=='':
        scheme=random.choice('http://', 'https://')
    if subdomain=='':
        subdomain='www'
    new_hostname=hostname+'.'+domain
    if hostport=='':
        hostport=random.choice('',':'+port)
     
    new_url, deviation_count=random_switch_case_of_char_in_string(scheme+subdomain+new_hostname+port+path, fuzzvalue) 
    
    request_line = f"{method} {new_url} HTTP/1.1\r\n"
    request_string = request_line

    for header in headers:
        request_string += f"{header[0]}: {header[1]}\r\n"

    request_string += "\r\n"

    return request_string, deviation_count

#CC with addional changes in the URL,  HEX Representation of the URL
def generate_request_CC_change_uri_HEXHEX(self, host, port=80, url='', method="GET", headers=None, fuzzvalue=None):
    # Check if headers are provided elsewise take default headers
    if headers is None:
        headers = self.default_headers
    else:
        # Create a copy to avoid modifying the original list
        headers = headers.copy()  
    
    # Insert the Host header at the beginning of the list
    headers.insert(0, ('Host', host)) 

    # Parse the given host
    scheme, subdomain, hostname, domain, hostport, path = parse_host(host)

    #Build a new URL from the given host, add some deviation if not all fields are provided

    if scheme=='':
        scheme=random.choice('http://', 'https://')
    if subdomain=='':
        subdomain='www'
    new_hostname=hostname+'.'+domain
    if hostport=='':
        hostport=random.choice('',':'+port)

    #Add some spezial Stuff to the path like HEX value? Maybe change it should work over the whole string?
    if random.random()<fuzzvalue and path=='':
        new_path+=random.choice('/?','/%3F','/%3f')

    new_url=scheme+subdomain+new_hostname+port+new_path
    
    if random.random()<fuzzvalue:
        #Convert the URL using parse lib quote (recommended for handling URLs in Python)
        new_url=quote(new_url)

     #Convert other characters in the URL to HEXHEX 

    
    for char in new_url:
        if random.random()<fuzzvalue:
            #find unicode point of the char, convert it to hex string
            hex_code = hex(ord(char))
            #slice string to remove leading "0x"
            hex_code=hex_code[2:]
            #randomly make chars of the Hex value upper or lower case
            if random.random()<fuzzvalue:  
                hex_code=hex_code.upper()
            else:
                hex_code=hex_code.lower()
            result += "%" + hex_code
        else:
            result += char
                
    new_url=result

    #Compare strings to count deviation
    deviation_count = 0
    min_len = min(len(url), len(new_url))
    for i in range(min_len):
        if url[i] != new_url[i]:
            deviation_count += 1
    # Account for any remaining characters in the longer string
    deviation_count += abs(len(url) - len(new_url)) 

    request_line = f"{method} {new_url} HTTP/1.1\r\n"

    for header in headers:
        request_string += f"{header[0]}: {header[1]}\r\n"

    request_string += "\r\n"

    return request_string, deviation_count



    

# CC with uncommon header
# CC with self defined headers (size limit?)
# CC with host and port
# CC with Data send While establishing TCP and upgrade to TLS
# CC With Data while Client Hllot at http2



# Todo:at 
#   Optional pass headers fields hy function call
#   Pass a value from the fuzzer to the functions
#   Try catch blocks?


def forge_http_request(host, port, url='/', method="GET", headers=None, fuzzvalue=0.5):
    if method == 1:
        return generate_standard_request(host, port, url='/', method="GET", headers=None, fuzzvalue=0.5)
    elif method == 2:
         return generate_request_CC_case_insensitivity(host, port, url='/', method="GET", headers=None, fuzzvalue=0.5)
    elif method == 3:
        return generate_request_CC_random_whitespace(host, port, url='/', method="GET", headers=None, fuzzvalue=0.5)
    elif method == 4:
        return generate_request_CC_reordering_headerfields(host, port, url='/', method="GET", headers=None, fuzzvalue=0.5)
    elif method == 5:
        return generate_request_CC_change_uri_representation(host, port, url='/', method="GET", headers=None, fuzzvalue=0.5)
    elif method == 6:
        return generate_request_CC_change_uri_case_insensitivity(host, port, url='/', method="GET", headers=None, fuzzvalue=0.5)
    elif method == 7:
        return generate_request_CC_change_uri_HEXHEX(host, port, url='/', method="GET", headers=None, fuzzvalue=0.5)
    else:
        raise ValueError("Invalid method number. Supported methods are 1, 2, 3, 4 , 5, 6 and 7.")
