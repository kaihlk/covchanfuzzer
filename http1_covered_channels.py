# http1_covered_channels.py

# Definition of functions to generate cover channels in http/1.1 requests
# TODO HTTP/2 request generation, with method:
import string
import random
import mutators
import numpy as np
import urllib.parse
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
            elif c.islower():
                modified_string = modified_string + c.upper()
                deviation_count += 1
            else:
                modified_string = modified_string + c
        else:
            modified_string = modified_string + c
    return modified_string, deviation_count


def generate_standard_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
    '''Generation of request package without insertion of a covert channel'''
     

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

class  HTTP1_Request_from_CSV(HTTP1_Request_Builder):
      def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):

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
        scheme=""
        request_line, new_uri = self.build_request_line(port, method, path, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)
       

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

        return request_string, deviation_count, new_uri


class HTTP1_Request_CC_Case_Insensitivity(HTTP1_Request_Builder):
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):

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
        scheme=""
        request_line, new_uri = self.build_request_line(port, method, path, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)
       

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

        return request_string, deviation_count, new_uri



class HTTP1_Request_CC_Random_Whitespace(HTTP1_Request_Builder):
# Covertchannel suggested by Kwecka et al: Linear whitespacing
# fuzzvalue defines the propability whether a value is changed and how many whitespaces/tabs/newlines are added
# Possible endless Loop, here is CC to learn something about the maximum size of the Request size
    
       
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        
        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))
        
        # Build the request_line from the provided arguments
        scheme=""
        request_line, new_uri = self.build_request_line(port, method, path, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)
       
        deviation_count = 0
        request_string = request_line
        # Iterate over header fields(HTTP1_Request_Builder):
        for header in headers:
            field_name, field_value = header
            # Random choice if value is changed
            if random.random() < fuzzvalue:
                # Create a string with random number of Whitespaces and Tabulators, third possible char?  ????
                whitespaces = ""
                while random.random() < fuzzvalue:
                    # Random Choice from Tabulator, Whitespace, carriage retrun + newline + Whitespace
                    random_linearwhithespace = random.choice(["\t", " ", "\r\n "])
                    whitespaces += random_linearwhithespace
                    deviation_count += 1
                # Add the whitespace string at the end of the value
                field_value += whitespaces
            # Build the line of the request string
            request_string += f"{field_name}: {field_value}\r\n"

        # End the request Sclass HTTP1_Request_CC_tring
        request_string += "\r\n"

        return request_string, deviation_count, new_uri


class HTTP1_Request_CC_Random_Whitespace_opt(HTTP1_Request_Builder):
    #Try to verify findings of first runn
    
       
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        
        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))
        
        # Build the request_line from the provided arguments
        scheme=""
        request_line, new_uri = self.build_request_line(port, method, path, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)
       
        deviation_count = 0
        request_string = request_line
        # Iterate over header fields(HTTP1_Request_Builder):
        for header in headers:
            field_name, field_value = header
            # Random choice if value is changed
            if random.random() < fuzzvalue:
                # Create a string with random number of Whitespaces and Tabulators, third possible char?  ????
                whitespaces = ""
                while random.random() < fuzzvalue:
                    # Random Choice from Tabulator, Whitespace, no carriage retrun + newline + Whitespace
                    if field_name!="Host":     #no tab at host
                        random_linearwhithespace = random.choice(["\t", " "])
                    else: 
                        random_linearwhithespace = " "
                    whitespaces += random_linearwhithespace
                    deviation_count += 1
                # Add the whitespace string at the end of the value
                field_value += whitespaces
            # Build the line of the request string
            request_string += f"{field_name}: {field_value}\r\n"

        # End the request Sclass HTTP1_Request_CC_tring
        request_string += "\r\n"

        return request_string, deviation_count, new_uri

class HTTP1_Request_CC_Random_Whitespace_opt2(HTTP1_Request_Builder):
    #Try to verify findings of first runn
    
       
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        
        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))
        
        # Build the request_line from the provided arguments
        scheme=""
        request_line, new_uri = self.build_request_line(port, method, path, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)
       
        deviation_count = 0
        request_string = request_line
        # Iterate over header fields(HTTP1_Request_Builder):
        for header in headers:
            field_name, field_value = header
            # Random choice if value is changed
            if random.random() < fuzzvalue:
                # Create a string with random number of Whitespaces and Tabulators, third possible char?  ????
                whitespaces = ""
                while random.random() < fuzzvalue:
                    # Random Choice from Tabulator, Whitespace, no carriage retrun + newline + Whitespace
                    if field_name!="Host":     #no tab at host
                        random_linearwhithespace = random.choice(["\t", " "])
                    else: 
                        random_linearwhithespace = ""
                    whitespaces += random_linearwhithespace
                    deviation_count += 1
                # Add the whitespace string at the end of the value
                field_value += whitespaces
            # Build the line of the request string
            request_string += f"{field_name}: {field_value}\r\n"

        # End the request Sclass HTTP1_Request_CC_tring
        request_string += "\r\n"

        return request_string, deviation_count, new_uri

class HTTP1_Request_CC_Random_Whitespace_opt3(HTTP1_Request_Builder):
    def __init__(self):
        super().__init__()  # Call the constructor of the base class first
        self.cc_uri_post_generation = True



    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        '''WHITESPACE Guided Modifications

        # Bit 0: Random Non-critical SP+HTAB
        # Bit 1: 2048 Non-critical
        # Bit 2: 20480 Non-critical
        # Bit 3: 40960 Non-critical 
        # Bit 4  61400 Non critical
        # Bit 5: 81920 Non critical
        # Bit 6: 1x +SP after Host
        # Bit 7: 1x +HTAB after Host
        # Bit 8: 1x +CRLN random position
        # Bit 9: 1x SP after host + 1x CRLN 
        # Bit 10: 1x HTAP after host +1 CRLN
        # Bit 11: +SP between key +value
        '''
       
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder)) 

        scheme=""
        # Build the request_line from the provided arguments
        request_line, new_uri = self.build_request_line(port, method, path, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)      
        request_string = request_line
        fuzzvalue=0.7
        deviation_count = 0
        target_deviation =0
        insertion_count=0
        newline=""
        keyspace=""
        bit_set = random.choice(range(12))  # Randomly choose one of the 8 bits
        
        
        

        # Iterate over header fields(HTTP1_Request_Builder):
        if bit_set==0: 
            target_deviation=1
            deviation_count += 1
        if bit_set==1: 
            target_deviation=2048
            deviation_count += 2
        if bit_set==2: 
            target_deviation=2024*10
            deviation_count += 4
        if bit_set==3: 
            target_deviation=2024*20
            deviation_count += 8
        if bit_set==4: 
            target_deviation=2024*30
            deviation_count += 16    
        if bit_set==5: 
            target_deviation=2024*40
            deviation_count += 32

        while insertion_count<target_deviation:
            for index, header in enumerate(headers):
                field_name, field_value = header
                # Random choice if value is changed
                if random.random() < fuzzvalue:
                    # Create a string with random number of Whitespaces and Tabulators, third possible char?  ????
                    whitespaces = ""
                    while random.random() < fuzzvalue:
                        # Random Choice from Tabulator, Whitespace, no carriage retrun + newline + Whitespace
                        if field_name!="Host":     #no tab at host
                            random_linearwhithespace = random.choice(["\t", " "])
                        else: 
                            random_linearwhithespace = ""
                        whitespaces += random_linearwhithespace
                        insertion_count += 1
                    # Add the whitespace string at the end of the value
                    field_value += whitespaces
                # Build the line of the request string
                headers[index]= (field_name, field_value)
        if bit_set==6: #SP
            key, value = headers[0]
            headers[0]=("Host", value+" ")
            target_deviation=0
            deviation_count += 64
        if bit_set==7: #TB
            key, value = headers[0]
            headers[0]=("Host", value+"\t")
            deviation_count += 128
        if bit_set==8: #CRLN
            newline="\r\n "
            deviation_count += 256
        if bit_set==9: #CRLN
            key, value = headers[0]
            headers[0]=("Host", value+" ")
            newline="\r\n "
            deviation_count += 512     
        if bit_set==10: 
            key, value = headers[0]
            headers[0]=("Host", value+"\t")
            newline="\r\n "
            deviation_count += 1024
        random_header = random.choice(headers)    
        modified_header = (random_header[0], random_header[1] + newline)
        index = headers.index(random_header)
        headers[index] = modified_header
        if bit_set==11:
            keyspace=" "
            deviation_count += 2048
            
       
        #Build header string

        for header in headers:
            request_string += f"{header[0]}: {keyspace}{header[1]}\r\n"

        request_string += "\r\n"    
                


        return request_string, deviation_count, new_uri


# Covertchannel suggested by Kwecka et al: Reordering ofHeaderfields#
# Fuzz Parameter no effect, due to Implementation of Shuffle

class HTTP1_Request_CC_Reordering_Header_Fields(HTTP1_Request_Builder):
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = self.default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        scheme=""
        # Build the request_line from the provided arguments
        request_line, new_uri = self.build_request_line(port, method, path, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)
       
        deviation_count = 0
        hostheader=self.host_placeholder
        headers.insert(0, ("Host", hostheader))

        # Shuffle the header fields randomly
        # Reorder the header fields, Note: the RandomValue random.shuffle(List, RandomValue[0,1]) is deprecated (Python 3.9)
        shuffled_headers = headers[:]
        random.shuffle(shuffled_headers)

        request_string = request_line
       
        # Iterate over the shuffled headers and compare with the original order
        for shuffled_header, original_header in zip(shuffled_headers, headers):
            # Check if the header is not 'Host' and the order has deviated and increment the deviation count
            if shuffled_header != original_header and original_header[0] != hostheader:
                deviation_count += 1
            # Build the request_string with the shuffeled_header
            request_string += f"{shuffled_header[0]}: {shuffled_header[1]}\r\n"
        # Add the final line break to the request string
        request_string += "\r\n"

        # Return the request string and deviation count
        return request_string, deviation_count, new_uri

class HTTP1_Request_CC_URI_Represenation(HTTP1_Request_Builder):
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        '''URI in the request line
        Covertchannel suggested by Kwecka et al: Uniform Ressource Identifiers
        Divide in 3 cover channels due to difference of technique
        Change the part of the path to make an absolute URI, may include scheme, port or
        Empty or not given port assune 80
        http as scheme name and host name case insenitivity'''
        
        #Relative URI does not make sense here
        relative_uri=False
        scheme=""

        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))        
        deviation_count = 0
        
        #Randomly include a scheme
        new_scheme = random.choice([scheme, "", "http://", "https://"])
        if new_scheme != scheme:
            deviation_count += 1
        #Randomly include a subdomain
        new_include_subdomain= random.choice([False, True])
        if new_include_subdomain!= include_subdomain:
            deviation_count+=1
        #Randomly include a port
        new_include_port=random.choice([False, True])
        if new_include_port!= include_port:
            deviation_count+=1
        #Randomly choose a port
        new_port = random.choice(
            [
                str(port),"80","443",str(random.randint(0, 65535)),  #Hard to analyze
            ]
        )
        if new_port !=port:
            deviation_count += 1

        new_path = random.choice(["", "/", path])
        if new_path != path:
            deviation_count += 1

        
        # Build a new URL from the input
        request_line, new_uri = self.build_request_line(new_port, method, new_path, headers, new_scheme, fuzzvalue, relative_uri, new_include_subdomain, new_include_port, protocol)
        
        request_line = f"{method} {new_uri} HTTP/1.1\r\n"

        request_string = request_line
        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        request_string += "\r\n"

        return request_string, deviation_count, new_uri


class HTTP1_Request_CC_URI_Represenation_opt2(HTTP1_Request_Builder):

    def __init__(self):
        super().__init__()  # Call the constructor of the base class first
        self.cc_uri_post_generation = True


    def build_request_line(self, port, method, path, headers, scheme, fuzzvalue, relative_uri=True, include_subdomain=False, include_port=False, protocol="HTTP/1.1"):
                # Build the request_line from the provided arguments, adjusted to be able to delte scheme and path
        if relative_uri==False:        
            #Scheme:
  
                #subdomains                      
            if include_subdomain:
               subdomain=self.subdomain_placeholder   ###SUBDOMAINS need to be ended with .
            else:
               subdomain="" 
            #Port
            if include_port==True:
                new_port=":"+str(port)
            else:
                new_port=""
            #absolute uri
            if path=="":
                local_path_placeholder=""
            else:
                local_path_placeholder=self.path_placeholder

            new_uri =scheme + subdomain + self.domain_placeholder + new_port + local_path_placeholder
        else:
            #relative uri
            new_uri=self.path_placeholder

        request_line = f"{method} {new_uri} {protocol}\r\n"

        return request_line, new_uri  


    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        '''URI in the request line
        Covertchannel suggested by Kwecka et al: Uniform Ressource Identifiers
        Divide in 3 cover channels due to difference of technique
        Change the part of the path to make an absolute URI, may include scheme, port or
        '''
        """Basic absolute request is build as following:
        scheme://subdomain.hostname.topleveldomain/
        for a HTTPS Request:
        https://www.example.com/
        Possible ways to add data:
        Scheme:
        scheme: https, http (+1), "" (+1)
        [subodmain] this may lead to other ressources than expected is excluded
        Port: "" "443" "80" (+1) "random int" (+1), random int bigger than portrange
        Path: No changes

        # Bit 0: Exclude Scheme
        # Bit 1: Switch Scheme
        # Bit 2: Exclude subdomain
        # Bit 3: Include fitting port
        # Bit 4: Counter Scheme fitting Port
        # Bit 5: Random Port in Port Range 65535 
        # Bit 6: Random Integer
        # Bit 7: Random String L=5
        # Bit 8: Random String L=6-100
        # Bit 9: Delete path if path is provided
        """
        #Relative URI does not make sense here
        relative_uri=False
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder)) 

        if port==443:
            scheme="https://"
        else:
            scheme="http://"       
        deviation_count = 0
        new_scheme=scheme
        new_include_subdomain=include_subdomain
        new_include_port=include_port
        new_port=port
        new_path=path


        bit_set = random.choice(range(11))  # Randomly choose one of the 10 bits

        # Bit 0: Exclude Scheme
        if bit_set == 0:
            new_scheme = ""
            deviation_count += 1
        elif bit_set == 1:
            # Bit 1: Switch Scheme
            if scheme=="http://": new_scheme="https://"
            else: new_scheme="http://"
            deviation_count += 2
        elif bit_set == 2:
            # Bit 2: Exclude subdomain
            new_include_subdomain = False
            deviation_count += 4
        elif bit_set == 3:
            # Bit 3: Include fitting port
            new_include_port=True
            if scheme=="https://":
                new_port="443"
            elif scheme=="http://":
                new_port="80"
            else: 
                new_port=port
            deviation_count += 8
        elif bit_set==4:
            #Bit 4: Counter Scheme fitting Port:
            new_include_port=True
            if scheme=="https://":
                new_port="80"
            elif scheme=="http://":
                new_port="443"
            else: 
                new_port=port
            deviation_count+=16
        elif bit_set==5:
            #Bit 5: Random Port in Port Range 65535 
            new_include_port=True
            new_port=random.randint(0, 65535)
            deviation_count+=32                 
        elif bit_set==6:
            #Bit 6: Random Integer
            new_include_port=True
            new_port = random.randint(-9223372036854775808, 9223372036854775807)
            deviation_count+=64            
        elif bit_set==7:
            #Bit 7: Random String L=5
            new_include_port=True
            new_port=mutators.generate_random_string(length=5)
            deviation_count+=128
        elif bit_set==8:
            #Bit 8: Random String L=6-100
            new_include_port=True
            length=random.randint(6, 100)
            new_port=mutators.generate_random_string(length=length)
            deviation_count+=256
        elif bit_set == 9:
            # Bit 9: Delete path if path is provided
            new_path = ""
            deviation_count += 512
        elif bit_set == 10:
            deviation_count += 1024
        
        # Build a new URL from the input
        request_line, new_uri = self.build_request_line(new_port, method, new_path, headers, new_scheme, fuzzvalue, relative_uri, new_include_subdomain, new_include_port, protocol)
        
        
        #Replace NEW_uri with new scheme
   
        request_string = request_line
        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"


        
        request_string += "\r\n"

        return request_string, deviation_count, new_uri

class HTTP1_Request_CC_URI_Represenation_opt1(HTTP1_Request_Builder):

    def build_request_line(self, port, method, path, headers, scheme, fuzzvalue, relative_uri=True, include_subdomain=False, include_port=False, protocol="HTTP/1.1"):
                # Build the request_line from the provided arguments, adjusted to be able to delte scheme and path
        if relative_uri==False:        
            #Scheme:
  
                #subdomains                      
            if include_subdomain:
               subdomain=self.subdomain_placeholder   ###SUBDOMAINS need to be ended with .
            else:
               subdomain="" 
            #Port
            if include_port==True:
                new_port=":"+str(port)
            else:
                new_port=""
            #absolute uri
            if path=="":
                local_path_placeholder=""
            else:
                local_path_placeholder=self.path_placeholder

            new_uri =scheme + subdomain + self.domain_placeholder + new_port + local_path_placeholder
        else:
            #relative uri
            new_uri=self.path_placeholder

        request_line = f"{method} {new_uri} {protocol}\r\n"

        return request_line, new_uri  


    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        '''URI in the request line
        Covertchannel suggested by Kwecka et al: Uniform Ressource Identifiers
        Divide in 3 cover channels due to difference of technique
        Change the part of the path to make an absolute URI, may include scheme, port or
        '''
        """Basic absolute request is build as following:
        scheme://subdomain.hostname.topleveldomain/
        for a HTTPS Request:
        https://www.example.com/
        Possible ways to add data:
        Scheme:
        scheme: https, http (+1), "" (+1)
        [subodmain] this may lead to other ressources than expected is excluded
        Port: "" "443" "80" (+1) "random int" (+1), random int bigger than portrange
        Path: No changes

        Bit 0: Include Scheme 0, Exclude Scheme 1
        Bit 1: Original Scheme 0, Flip Scheme 1
        Bit 2: Original Subdomain 0, No Subdomain 1
        Bit 3: No Port 0, Add Port: 1
        Bit 4: Scheme Fitting Port: 1, Other Scheme Port 0
        Bit 5: Random Port in 65535 Range 0, Random Port out of 65535 Range: 1
        Bit 6: No radom String for Port, Random String for Port 1
        Bit 7: Original Ṕath 0, empty Path="" 1
        Bit 8: Original Path, standard Path="" 1 

        """
        #Relative URI does not make sense here
        relative_uri=False
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder)) 

        if port==443:
            scheme="https://"
        else:
            scheme="http://"       
        deviation_count = 0

        #Bit0: include scheme
        new_include_scheme= random.choice([False, True])
        if new_include_scheme is False:
            new_scheme=""
            deviation_count+=1
        else:
            #Bit1: Original Scheme
            #Define Standard Value,  then randomly include a scheme
  
            new_scheme = random.choice(["http://", "https://"])
            if new_scheme != scheme:
                deviation_count += 2
        #Bit2 randomly include/exclude subdomain
        new_include_subdomain= random.choice([False, True])
        if new_include_subdomain is False:
            deviation_count+=4
        #Bit 3: Randomly include a port
        new_include_port=random.choice([False, True])
        new_port=port
        if new_include_port is True:
            deviation_count+=8
            #Create port stepwise
            #Bit 4: Scheme Fitting Port:
            protocol_associtated_port=random.choice([False, True])
            if protocol_associtated_port is True:
                if scheme=="https://":
                    new_port="443"
                    deviation_count+=16
                elif scheme=="http://":
                    new_port="80"
                    deviation_count+=16
                else: 
                    new_port=""
            else:
                #Bit 5: Counter HTTP/HTTPS Port
                http_or_https_port=random.choice([False, True])
                if http_or_https_port is True:
                    if scheme=="https://":
                        new_port="80"
                        deviation_count+=32
                    elif scheme=="http://":
                        new_port="443"
                        deviation_count+=32
                    else: 
                        new_port=""  #Just to prevent errors
                else:
                    #Bit 6: Random Port in 65535 
                    port_in_range=random.choice([False, True])
                    if port_in_range is True:
                        new_port=random.randint(0, 65535)
                        deviation_count+=64
                    else:
                        #Bit 7: Random Integer
                        port_as_random_int=random.choice([False, True])
                        if port_as_random_int is True:
                            new_port = random.randint(-9223372036854775808, 9223372036854775807)
                            deviation_count+=128
                        else: 
                            #Bit 8: 
                            port_as_random_str_l5=random.choice([False, True])
                            if port_as_random_str_l5 is True:
                                new_port=mutators.generate_random_string(length=5)
                                deviation_count+=256
                            #No new port found Zero Bit 3
                            else:
                                new_port=""
                                deviation_count-=8

        #Bit9 Delete path if path is provided  
        delete_path=random.choice([False, True])
        if delete_path is True:
            path=""
            deviation_count+=512
        new_path=path
        
        # Build a new URL from the input
        request_line, new_uri = self.build_request_line(new_port, method, new_path, headers, new_scheme, fuzzvalue, relative_uri, new_include_subdomain, new_include_port, protocol)

        
        request_string = request_line
        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"
 
        request_string += "\r\n"

        return request_string, deviation_count, new_uri



class HTTP1_Request_CC_URI_Represenation_Apache_Localhost(HTTP1_Request_Builder):
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        
        #Not longer used
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
    def __init__(self):
        super().__init__()  # Call the constructor of the base class first
        self.cc_uri_post_generation = True

    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        '''CC URI  with addional changes in Case insensitvity'''
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        scheme=""

        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))


          # Build a new URL from the given host
        request_line, new_uri = self.build_request_line(port, method, path, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)
        

        deviation_count=0
        if protocol=="":
            protocol="HTTP/1.1"
        request_line = f"{method} {new_uri} {protocol}\r\n"
        request_string = request_line

        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        request_string += "\r\n"

        return request_string, deviation_count, new_uri
    
    def replace_host_and_domain(self, prerequest, domain, standard_subdomain="", host=None, include_subdomain_host_header=False, path="",override_uri="", fuzzvalue=0.5):
        #CC specific
        
        fuzzvalue=0.3
        try:
            scheme, subdomains, hostname, tldomain, _port, _path =self.parse_host(domain)
            if subdomains=="":
                subdomains=standard_subdomain            
            if not subdomains=="" and not subdomains.endswith('.'):
                    subdomains += '.'
            new_domain=hostname+"."+tldomain
            if host==None:
                if include_subdomain_host_header==True:
                    host=subdomains+"."+new_domain
                else: 
                    host=domain
            if override_uri!="":
                new_domain=override_uri
                prerequest=prerequest.replace('https://', '',1)
            ##CC Change URI Case###
            #Change URI Case
            if scheme!="":
                new_scheme, deviation_count_scheme = random_switch_case_of_char_in_string(scheme, fuzzvalue)
                if new_scheme.lower()=="http":
                    request_sch=prerequest.replace("http", new_scheme)
                elif new_scheme.lower()=="https":
                    request_sch=prerequest.replace("https", new_scheme)
            else: 
                request_sch=prerequest
                deviation_count_scheme=0
            new_domain, deviation_count_domain = random_switch_case_of_char_in_string(new_domain, fuzzvalue)
            new_subdomains, deviation_count_subdomains = random_switch_case_of_char_in_string(subdomains, fuzzvalue)
            new_path, deviation_count_path = random_switch_case_of_char_in_string(path, fuzzvalue)
            deviation_count=deviation_count_scheme+deviation_count_domain+deviation_count_subdomains+deviation_count_path
            #This inserts the sudomain in the uri

            request_sub=request_sch.replace(self.subdomain_placeholder,new_subdomains)
            request_dom=request_sub.replace(self.domain_placeholder, new_domain)
            request=request_dom.replace(self.path_placeholder, new_path)
            #The Subdomain inclusion for the host header field takes places here,
            request=request.replace(self.host_placeholder, host)
            
            new_uri=self.extract_new_uri(request)
            
            return request, deviation_count, new_uri
        except Exception as ex:
            print(ex)



class HTTP1_Request_CC_URI_Hex_Hex(HTTP1_Request_Builder):
    # CC with addional changes in the URL,  HEX Representation of the URL
    # empty absolute path interpreta as "/"
    #  Hex representation can  7e or 7E
    
    
    
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
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

# CC which adds header fields from the common and uncommon header list 
class HTTP1_Request_CC_Random_Content(HTTP1_Request_Builder):
 
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        '''Generation of request package '''

         # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        scheme=""

        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))


          # Build a new URL from the given host
        request_line, new_uri = self.build_request_line(port, method, path, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)
        content="random"

        deviation_count=0

        # Add Content more randomness, content length field yes, no, wrong value, other position
        if content is not None:
            if content=="random":
                #"Generate Random Content"
                length=random.randint(0, 100)
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
        return request_string, deviation_count, new_uri


class HTTP1_Request_CC_Random_Content_No_Lenght_Field(HTTP1_Request_Builder):
    # CC which adds header fields from the common and uncommon header list
  
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
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
    
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
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
        headers.insert(0, ("Host", self.host_placeholder))


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
        
        
        scheme=""
        request_line, new_uri = self.build_request_line(port, method, new_path, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)

        request_string = request_line
        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        request_string += "\r\n"
          
        return request_string, deviation_count, new_uri


class HTTP1_Request_CC_URI_Common_Addresses_And_Anchors(HTTP1_Request_Builder):
    
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
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

        length=0
        #Add Fragments
        while random.random() < fuzzvalue:
            length+=1
        anchor="#"+mutators.generate_random_string(string.ascii_letters+string.digits, length) 

        new_path+=anchor

        if new_path != path:
            deviation_count += 1
        
        request_line, new_uri = self.build_request_line(port, method, new_path, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)
       
        request_string = request_line
        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        request_string += "\r\n"
          
        return request_string, deviation_count, new_uri


class HTTP1_Request_CC_URI_Extend_with_fragments(HTTP1_Request_Builder):
    def __init__(self):
        super().__init__()  # Call the constructor of the base class first
        self.cc_uri_post_generation = False

    def build_request_line(self, port, method, path, fragment, headers, scheme, fuzzvalue, relative_uri=True, include_subdomain=False, include_port=False, protocol="HTTP/1.1"):
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
               subdomain=self.subdomain_placeholder   ###SUBDOMAINS need to be ended with .
            else:
               subdomain="" 
            #Port
            if include_port==True:
                new_port=":"+str(port)
            else:
                new_port=""
            #absolute uri
            new_uri =scheme + subdomain + self.domain_placeholder + new_port + self.path_placeholder + "#" +fragment
        else:
            #relative uri
            new_uri=self.path_placeholder + "#" +fragment

        request_line = f"{method} {new_uri} {protocol}\r\n"

        return request_line, new_uri   

    
    
    
    
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        '''CC URI  with addional changes in Case insensitvity'''
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        scheme=""

        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))

        ###CC Part#
        max_length=1024*100    #8kb nginx and apache limit for repsonse line
            
        char_sets = {
            "letters_digits": string.ascii_letters + string.digits,
            "subdelimiters": "!$&'()*+,;=",
            "general_delimiters": ":/?#[]@"
        }
        chosen_set = random.choice(list(char_sets.keys()))

        min_length = 1 # 1in bytes
        max_length=1024*100   # 100 KB in bytes
        sca1e=20
        random_border = int(np.random.exponential(sca1e)*1024)
        random_border = max(min_length, min(max_length, random_border))

        #random_border=random.randint(0, max_length)
        fragment=mutators.generate_random_string(chosen_set, random_border, 0)
        if random.random()<fuzzvalue:
            fragment = urllib.parse.quote(fragment) 
        deviation_count=len(fragment)+1
        
        #### 

          # Build a new URL from the given host
        request_line, new_uri = self.build_request_line(port, method, path, fragment, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)
        

        if protocol=="":
            protocol="HTTP/1.1"
        request_line = f"{method} {new_uri} {protocol}\r\n"
        request_string = request_line

        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        request_string += "\r\n"

        return request_string, deviation_count, new_uri

    def replace_host_and_domain(self, prerequest, uri, standard_subdomain="", host_header=None, include_subdomain_host_header=False, path="", override_uri="", fuzzvalue=0.5):
        "Replace the the Placeholders from the Prerequest to adapt it to the host"
        try:
            #Prepare the parts of URI
            #Break the domain into pieces
            _scheme, subdomains, hostname, tldomain, _port, uri_path =self.parse_host(uri)
            #if subdomains=="":
            #    subdomains=standard_subdomain
            if not subdomains=="" and not subdomains.endswith('.'):
                subdomains += '.'
            new_domain=hostname+"."+tldomain
            #Build host from domain if not provided
            if host_header is None:
                if include_subdomain_host_header is True:
                    host_header=subdomains+"."+new_domain
                else:
                    host_header=new_domain
            #Replace domain if override_uri
            if override_uri!="":
                new_domain=override_uri
                prerequest=prerequest.replace('https://', '',1)
            if uri_path=="":
                new_path=path
            else:
                new_path=uri_path
            if not new_path.startswith("/"):
                new_path="/"+new_path   

            deviation_count=0

                       
            #This inserts the sudomain in the uri
            request=prerequest.replace(self.subdomain_placeholder,subdomains)
            request=request.replace(self.domain_placeholder, new_domain)
            request=request.replace(self.path_placeholder, new_path)
            #The Subdomain inclusion for the host header field takes places here,
            request=request.replace(self.host_placeholder, host_header)

    

            new_uri=self.extract_new_uri(request)
            return request, deviation_count, new_uri
        except Exception as ex:
            print(ex)


    #Try to verify findings of first runn
    
class  HTTP1_Request_CC_Add_Random_Header_Fields(HTTP1_Request_Builder):      
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        
        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))
        
        # Build the request_line from the provided arguments
        
        scheme=""
        
        request_line, new_uri = self.build_request_line(port, method, path, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)
       
        deviation_count = 0
        request_string = request_line
        
        max_header_key_length= 16
        max_header_value_length =16
        max_header_field_count = 1024
        

        # Generate random header key-value pairs
        header_count=len(headers)  
        chosen_header_field_count=random.randint(header_count, max_header_field_count)  
        while header_count<chosen_header_field_count: 
            header_count+=1
            random_header_key = mutators.generate_random_string(length=max_header_key_length)
            random_header_value = mutators.generate_random_string(length=max_header_value_length)
            deviation_count+=len(random_header_key)+len(random_header_value)
            headers.append((random_header_key, random_header_value))
    
        #CC PART
        header_count=+1
        headers.append(("Head-Count", header_count))


        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        # End the request Sclass HTTP1_Request_CC_tring
        request_string += "\r\n"

        return request_string, deviation_count, new_uri

class  HTTP1_Request_CC_Add_Big_Header_Field(HTTP1_Request_Builder):      
    def generate_cc_request(self, port, method, path, headers, content, fuzzvalue, relative_uri, include_subdomain, include_port, protocol):
        # Check if headers are provided elsewise take default headers
        if headers is None:
            headers = default_headers.copy()
        else:
            # Create a copy to avoid modifying the original list
            headers = headers.copy()
        
        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", self.host_placeholder))
        
        # Build the request_line from the provided arguments
        
        scheme=""
        
        request_line, new_uri = self.build_request_line(port, method, path, headers, scheme, fuzzvalue, relative_uri, include_subdomain, include_port, protocol)
       
        deviation_count = 0
        request_string = request_line
        
        max_header_key_length= 20*1024
        max_header_value_length =20*1024
        #CC PART
        
        # Generate random header key-value pairs
        random_header_key = mutators.generate_random_string(length=random.randint(1,max_header_key_length))
        random_header_value = mutators.generate_random_string(length=random.randint(1,max_header_value_length))
        headers.append((random_header_key, random_header_value))
        header_count=len(headers)    
        deviation_count+=len(random_header_key)+len(random_header_value)
        
            
    
        

        for header in headers:
            request_string += f"{header[0]}: {header[1]}\r\n"

        # End the request Sclass HTTP1_Request_CC_tring
        request_string += "\r\n"

        return request_string, deviation_count, new_uri

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


    