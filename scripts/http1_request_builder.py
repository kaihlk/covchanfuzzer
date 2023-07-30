# http1_covered_channels.py

# Definition of functions to generate cover channels in http/1.1 requests
# TODO HTTP/2 request generation, with method:

import random
import logging
from urllib.parse import quote
logging.basicConfig(level=logging.DEBUG)


class HTTP1_Request_Builder:
    def __init__(self): 
        self.default_headers_sets = {
            # The field with the Host and the url must be generated and inserted in the functions
            "rfc": [
                ("User-Agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                ),
                (
                    "Accept",
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                ),
                ("Accept-Encoding", "gzip, deflate, br"),
                ("Accept-Language", "en-US,en;q=0.9"),
                ("Connection", "keep-alive"),
            ],
            "safari": [
                # The field with the Host and the url must be generated and inserted in the functions
                (
                    "User-Agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                ),
                (
                    "Accept",
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                ),
                ("Accept-Encoding", "gzip, deflate, br"),
                ("Accept-Language", "en-US,en;q=0.9"),
                ("Connection", "keep-alive"),
            ],
            "chrome": [
                # The field with the Host and the url must be generated and inserted in the functions
                (
                    "User-Agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                ),
                (
                    "Accept",
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                ),
                ("Accept-Encoding", "gzip, deflate, br"),
                ("Accept-Language", "en-US,en;q=0.9"),
                ("Connection", "keep-alive"),
            ],
            "firefox": [
                # The field with the Host and the url must be generated and inserted in the functions
                (
                    "User-Agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                ),
                (
                    "Accept",
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                ),
                ("Accept-Encoding", "gzip, deflate, br"),
                ("Accept-Language", "en-US,en;q=0.9"),
                ("Connection", "keep-alive"),
            ],
        }

    def parse_host(self, host):
        '''Parse host uris'''
        # Initialize variables
        scheme = ""
        subdomain = ""
        hostname = ""
        domain = ""
        port = ""
        path = ""
        host = self.target_host
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

    def generate_cc_request(self, host, port, url="/", method="GET", headers=None, fuzzvalue=None):



        '''Generation of request package without insertion of a covert channel'''
       

        # Insert the Host header at the beginning of the list
        headers.insert(0, ("Host", host))

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

    def generate_request(self, experiment_configuration):
        '''Covered Channel Classes must implement this method'''
        host=experiment_configuration["target_host"]
        port=experiment_configuration["target_port"]
        url=experiment_configuration["url"]
        method=experiment_configuration["method"]
        headers=experiment_configuration["headers"]
        standard_headers=experiment_configuration["standard_headers"]
        fuzzvalue=experiment_configuration["fuzz_value"]
         # Check if headers are provided elsewise take default headers
        if headers is None: 
            if standard_headers in self.default_headers_sets:
                headers= self.default_headers_sets[standard_headers].copy()       
            else:
                headers = self.default_headers_sets["rfc"].copy()

            # Create a copy to avoid modifying the original list
        print("Arguments:")
        print(host)
        print(port)
        print(url)
        print(method)
        print(headers)
        print(fuzzvalue)
        return self.generate_cc_request(host, port, url, method, headers, fuzzvalue)
