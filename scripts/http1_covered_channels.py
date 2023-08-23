# http1_covered_channels.py

# Definition of functions to generate cover channels in http/1.1 requests
# TODO HTTP/2 request generation, with method:
import string
import random
import mutators
from urllib.parse import quote
from http1_request_builder import HTTP1_Request_Builder


def random_switch_case_of_char_in_string(original_string, fuzzvalue):
    modified_string = ""
    deviation_count = 0
    # Randomly change the case of the field name
    for c in original_string:
        # The value of the probabiltiy to change a char is defined by the fuzzvalue
        # the char functions doesn't affect signs and symbols
        if random.random() < fuzzvalue:
            if c.isupper():
                modified_string = modified_string + c.lower()
                deviation_count += 1
            elif c.islower:
                modified_string = modified_string + c.upper()
                deviation_count += 1
            else:
                modified_string = modified_string + c
        else:
            modified_string = modified_string + c
    return modified_string, deviation_count


def generate_standard_request(
     port, url="/", method="GET", headers=None, fuzzvalue=None
):
    '''Generation of request package without insertion of a covert channel'''
    # Check if headers are provided elsewise take default headers
    if headers is None:
        headers = default_headers.copy()
    else:
        # Create a copy to avoid modifying the original list
        headers = headers.copy()

    # Insert the Host header at the beginning of the list
    headers.insert(0, ("Host", self.host_placeholder))

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
    return request_string, deviation_count, url

class HTTP1_Request_CC_Case_Insensitivity(HTTP1_Request_Builder):
    def generate_cc_request(self,  port, url="/", method="GET", headers=None, content=None, fuzzvalue=None):

        '''Covertchannel suggested by Kwecka et al: Case-insensitivity of header key names, fuzzvalue defines the probability that a character of a header field is changed'''

        # Check fuzzvalue
        if fuzzvalue < 0 or fuzzvalue > 1:
            raise ValueError("fuzzvalue must be between 0 and 1.")

        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()

        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))

        # Build the request_line from the provided arguments
        request_line = f"{method} {url} HTTP/1.1\r\n"

        # Define Request first line
        request_string = request_line
        deviation_count = 0
        # Iterate over the header fields
        for header in headers:
            field_name, field_value = header
            modified_field_name, deviation = random_switch_case_of_char_in_string(original_string=field_name, fuzzvalue=fuzzvalue
            )
            # Build request string from modified field name, :, and field value
            request_string += f"{modified_field_name}: {field_value}\r\n"
            deviation_count += deviation

        # Add ending of request
        request_string += "\r\n"

        return request_string, deviation_count, url



class HTTP1_Request_CC_Random_Whitespace(HTTP1_Request_Builder):
# Covertchannel suggested by Kwecka et al: Linear whitespacing
# fuzzvalue defines the propability whether a value is changed and how many whitespaces/tabs/newlines are added
# Possible endless Loop, here is CC to learn something about the maximum size of the Request size
    def generate_cc_request(self, port, url="/", method="GET", headers=None, content=None, fuzzvalue=None):
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()

        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))
        print(fuzzvalue)
        # Build the request_line from the provided arguments
        request_line = f"{method} {url} HTTP/1.1\r\n"
        deviation_count = 0
        request_string = request_line
        # Iterate over header fields(HTTP1_Request_Builder):
        for header in headers:
            field_name, field_value = header
            # Random choice if value is changed
            if random.random() < fuzzvalue:
                # Create a string with random number of Whitespaces and Tabulators, third possible char?  ????
                whitespace = ""
                while random.random() < fuzzvalue:
                    # Random Choice from Tabulator, Whitespace, carriage retrun + newline + Whitespace
                    random_string = random.choice(["\t", " ", "\r\n "])
                    whitespace += random_string
                    deviation_count += 1
                # Add the whitespace string at the end of the value
                field_value += whitespace
            # Build the line of the request string
            request_string += f"{field_name}: {field_value}\r\n"

        # End the request Sclass HTTP1_Request_CC_tring
        request_string += "\r\n"

        return request_string, deviation_count, url

# Covertchannel suggested by Kwecka et al: Reordering ofHeaderfields#
# Fuzz Parameter no effect, due to Implementation of Shuffle

class HTTP1_Request_CC_Reordering_Header_Fields(HTTP1_Request_Builder):
    def generate_cc_request(self,
         port, url="/", method="GET", headers=None, content=None, fuzzvalue=0.5
        ):
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = self.default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()

        # Build the request_line from the provided arguments
        request_line = f"{method} {url} HTTP/1.1\r\n"

        deviation_count = 0
        headers.insert(0, ("Host", self.host_placeholder))

        # Shuffle the header fields randomly
        # Reorder the header fields, Note: the RandomValue random.shuffle(List, RandomValue[0,1]) is deprecated (Python 3.9)
        shuffled_headers = headers[:]
        random.shuffle(shuffled_headers)

        request_string = request_line
       
        # Iterate over the shuffled headers and compare with the original order
        for shuffled_header, original_header in zip(shuffled_headers, headers):
            # Check if the header is not 'Host' and the order has deviated and increment the deviation count
            if shuffled_header != original_header and original_header[0] != host:
                deviation_count += 1
            # Build the request_string with the shuffeled_header
            request_string += f"{shuffled_header[0]}: {shuffled_header[1]}\r\n"
        # Add the final line break to the request string
        request_string += "\r\n"

        # Return the request string and deviation count
        return request_string, deviation_count, url

class HTTP1_Request_CC_URI_Represenation(HTTP1_Request_Builder):
    def generate_cc_request(self,
         port, url="/", method="GET", headers=None, content=None, fuzzvalue=0.5
    ):
        '''URI in the request line
        Covertchannel suggested by Kwecka et al: Uniform Ressource Identifiers
        Divide in 3 cover channels due to difference of technique
        Change the part of the path to make an absolute URI, may include scheme, port or
        Empty or not given port assune 80
        http as scheme name and host name case insenitivity'''
        
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        
        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))

        # Parse the given host
        #TODO
        #scheme, subdomain, self.host_placeholder, domain, hostport, path = self.parse_host(url,host)

        # Build a new URL from the given host
        deviation_count = 0
        
        if scheme == "":
            scheme = "https"
        new_scheme = random.choice([scheme + "://", "", "http://", scheme, "https://"])
        if new_scheme != scheme:
            deviation_count += 1

        if subdomain == "":
            subdomain = "www"
        new_subdomain = random.choice([subdomain, subdomain + ".", "", "www."])
        if new_subdomain != subdomain:
            deviation_count += 1

        new_hostname = random.choice([hostname, hostname + "." + domain, domain, "", "." + domain])
        if new_hostname != hostname + "." + domain:
            deviation_count += 1

        if hostport == "":
            hostport = port
        new_port = random.choice(
            [
                "",
                ":" + str(hostport),
                ":" + str(port),
                #":" + "80",
                #":" + "443",
                #":" + str(random.randint(0, 65535)),  #Hard to analyze
            ]
        )
        if new_port != hostport:
            deviation_count += 1

        new_path = random.choice(["", "/", "/" + path])
        if new_path != path:
            deviation_count += 1

        new_url = new_scheme + new_subdomain + new_hostname + new_port + new_path

        request_line = f"{method} {new_url} HTTP/1.1\r\n"

        request_string = request_line
        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        request_string += "\r\n"

        return request_string, deviation_count, new_url

class HTTP1_Request_CC_URI_Represenation_Apache_Localhost(HTTP1_Request_Builder):
    def generate_cc_request(self,
         port, url="/", method="GET", headers=None, content=None, fuzzvalue=0.5
    ):
        '''URI in the request line
        Covertchannel suggested by Kwecka et al: Uniform Ressource Identifiers
        Divide in 3 cover channels due to difference of technique
        Change the part of the path to make an absolute URI, may include scheme, port or
        Empty or not given port assune 80
        http as scheme name and host name case insenitivity'''
        
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        
        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))

        # Parse the given host
        #TODO
        #scheme, subdomain, self.host_placeholder hostport, path = self.parse_host(url,host)

        # Build a new URL from the given host
        deviation_count = 0
        
        if scheme == "":
            scheme = "http"
        new_scheme = random.choice([scheme + "://"])#, "", "http://"])#, scheme, "https://"])
        if new_scheme != scheme:
            deviation_count += 1

        if subdomain == "":
            subdomain = "www"
        new_subdomain = random.choice([subdomain, subdomain + ".", "", "www."])
        if new_subdomain != subdomain:
            deviation_count += 1

        new_hostname = random.choice([hostname, hostname + "." + domain, domain, "",])# "." + domain])
        if new_hostname != hostname + "." + domain:
            deviation_count += 1

        if hostport == "":
            hostport = port
        new_port = random.choice(
            [
                "",
                ":" + str(hostport),
                ":" + str(port),
                #":" + "80",
                #":" + "443",
                #":" + str(random.randint(0, 65535)),  #Hard to analyze
            ]
        )
        if new_port != hostport:
            deviation_count += 1

        new_path = random.choice(["", "/", "/" + path])
        if new_path != path:
            deviation_count += 1

        new_url = new_scheme + new_subdomain + new_hostname + new_port + new_path

        request_line = f"{method} {new_url} HTTP/1.1\r\n"

        request_string = request_line
        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        request_string += "\r\n"

        return request_string, deviation_count, new_url



class HTTP1_Request_CC_URI_Case_Insentivity(HTTP1_Request_Builder):
    def generate_cc_request(self,
        host, port, url="/", method="GET", headers=None, fuzzvalue=0.5
    ):
        '''CC URI  with addional changes in Case insensitvity'''
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()

        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))

        # Parse the given host
        #TODO
        scheme, subdomain, hostname, domain, hostport, path = self.parse_host(url,host)

        # Build a new URL from the given host, add some deviation if not all fields are provided

        if scheme == "":
            scheme = random.choice(["http://", "https://"])
        if subdomain == "":
            subdomain = "www"
        new_hostname = subdomain + "." + hostname + "." + domain
        if hostport == "":
            hostport = random.choice(["", ":" + str(port)])

        new_url, deviation_count = random_switch_case_of_char_in_string(
            scheme + new_hostname + hostport + path, fuzzvalue
        )

        request_line = f"{method} {new_url} HTTP/1.1\r\n"
        request_string = request_line

        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        request_string += "\r\n"

        return request_string, deviation_count, new_url

class HTTP1_Request_CC_URI_Hex_Hex(HTTP1_Request_Builder):
    # CC with addional changes in the URL,  HEX Representation of the URL
    # empty absolute path interpreta as "/"
    #  Hex representation can  7e or 7E
    
    
    
    def generate_cc_request(self,
         port, url="/", method="GET", headers=None, fuzzvalue=0.5
    ):
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()

        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))

        # Parse the given host
        scheme, subdomain, hostname, domain, hostport, path = self.parse_host(url,host)

        # Build a new URL from the given host, add some deviation if not all fields are provided

        if scheme == "":
            scheme = random.choice(["http://", "https://"])

        if subdomain == "":
            subdomain = "www"

        new_hostname = subdomain + "." + hostname + "." + domain

        if hostport == "":
            hostport = random.choice(["", ":" + str(port)])

        # Add some spezial Stuff to the path like HEX value? Maybe change it should work over the whole string?
        if random.random() < fuzzvalue and path == "":
            new_path = random.choice(["/?", "/%3F", "/%3f"])

        else:
            new_path = path

        new_url = scheme + new_hostname + hostport + new_path

        if random.random() < fuzzvalue:
            # Convert the URL using parse lib quote (recommended for handling URLs in Python)
            new_url = quote(new_url)

        # Convert other characters in the URL to HEXHEX
        new_url_temp = ""
        for char in new_url:
            if random.random() < fuzzvalue:
                # find unicode point of the char, convert it to hex string
                hex_code = hex(ord(char))
                # slice string to remove leading "0x"
                hex_code = hex_code[2:]
                # randomly make chars of the Hex value upper or lower case
                if random.random() < fuzzvalue:
                    hex_code = hex_code.upper()
                else:
                    hex_code = hex_code.lower()
                new_url_temp += "%" + hex_code
            else:
                new_url_temp += char

        new_url = new_url_temp

        # Compare strings to count deviation, this is not perfect, maybe find a better way
        deviation_count = 0
        min_len = min(len(url), len(new_url))
        for i in range(min_len):
            if url[i] != new_url[i]:
                deviation_count += 1
        # Account for any remaining characters in the longer string
        deviation_count += abs(len(url) - len(new_url))

        request_line = f"{method} {new_url} HTTP/1.1\r\n"

        request_string = request_line
        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        request_string += "\r\n"

        return request_string, deviation_count, new_url


class HTTP1_Request_CC_Random_Content(HTTP1_Request_Builder):
    # CC which adds header fields from the common and uncommon header list
 
    
    
    def generate_cc_request(self,
         port, url="/", method="GET", headers=None, content=None, fuzzvalue=0.5
    ):
        '''Generation of request package '''



        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))

        # Build the request_line from the provided arguments
        request_line = f"{method} {url} HTTP/1.1\r\n"

        # Add Content more randomness, content length field yes, no, wrong value, other position
        if content is not None:
            if content=="random":
                "Generate Random Content"
                length=random.randint(0, 10)
                content = mutators.generate_random_string(string.printable, length)     
            if random.random()<fuzzvalue:
                if random.random()<fuzzvalue:
                    headers.append(("Content-Length", len(content)))
                else:
                    headers.insert(random.randint(0, len(headers)-1),("Content-Length", len(content)))                
            
        
        # Build the request from request line and headers

        request_string = request_line
        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        # Add the ending of the request
        request_string += "\r\n"

        # Add Content
        if content is not None:
            request_string += content
    


        # No deviation
        deviation_count = len(content)
        return request_string, deviation_count, new_url


class HTTP1_Request_CC_Random_Content_No_Lenght_Field(HTTP1_Request_Builder):
    # CC which adds header fields from the common and uncommon header list
  
    def generate_cc_request(self,
         port, url="/", method="GET", headers=None, content=None, fuzzvalue=0.5
    ):
        '''Generation of request package '''



        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))

        # Build the request_line from the provided arguments
        request_line = f"{method} {url} HTTP/1.1\r\n"

        # Add Content more randomness, content length field yes, no, wrong value, other position
        if content is not None:
            if content=="random":
                "Generate Random Content"
                length=random.randint(0, 100000)
                content = mutators.generate_random_string(string.printable, length)                    
            
        
        # Build the request from request line and headers

        request_string = request_line
        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        # Add the ending of the request
        request_string += "\r\n"

        # Add Content
        if content is not None:
            request_string += content
    #new_path = random.choice(["", "/", "/" + path])
        deviation_count = len(content)
        return request_string, deviation_count, new_url

class HTTP1_Request_CC_URI_Common_Addresses(HTTP1_Request_Builder):
    
    def generate_cc_request(self,
         port, method="GET", path="/", headers=None, content=None, fuzzvalue=0.5, relative_uri=True, include_subdomain=True):
        '''URI in the request line
        Covertchannel suggested by Kwecka et al: Uniform Ressource Identifiers
        Divide in 3 cover channels due to difference of technique
        Change the part of the path to make an absolute URI, may include scheme, port or
        Empty or not given port assune 80
        http as scheme name and host name case insenitivity'''
        
        print("METHODE::")
        print(method)
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        
        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", "www."+self.host_placeholder))


        # Build a new URL from the given host
        deviation_count = 0
        

        standard_paths = [
            "/",
            "/index.html",
            "/index.php",
            "/about",
            "/contact",
            "/services",
            "/support",
            "/blog",
            "/favicon.ico",
        ]
        
        if path!="":
            standard_paths.append(path)

        new_path= random.choice(standard_paths)
        if new_path != path:
            deviation_count += 1
        
        if relative_uri==False:        
            #Scheme:
            if port==443:
                scheme="https://"
            else:
                scheme="http://"
            #subdomains                      
            if include_subdomain:
               subdomain=self.subdomain_placeholder+"."
            else:
               subdomain="" 
            #absolute uri
            new_url =scheme + subdomain + self.domain_placeholder + new_path
        else:
            new_url=new_path

        request_line = f"{method} {new_url} HTTP/1.1\r\n"

        request_string = request_line
        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        request_string += "\r\n"
          
        return request_string, deviation_count, new_url


    # CC Absence or PResense of a header field

    # CC with uncommon header
    # CC with self defined headers (size limit?)
    # CC with host and port
    # CC with Data send While establishing TCP and upgrade to TLS
    # CC With Data while Client Hello at http2


    # Todo:at
    #   Optional pass headers fields hy function call
    #   Pass a value from the fuzzer to the functions
    #   Try catch blocks?


    