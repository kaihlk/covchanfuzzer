import json
from collections import defaultdict


def uri_inspector():
    file_path = "logs/20230804_223630_localhost/log_file.json"
    uri_status_count = defaultdict(lambda: defaultdict(int))

    with open(file_path, "r") as file:
        data = json.load(file)

    for entry in data:
        request_lines = entry["request"].split("\r\n")
        first_line_parts = request_lines[0].split()

        if len(first_line_parts) >= 3:
            method, uri, _ = first_line_parts
            status_code = entry["status_code"]

            uri_status_count[status_code][uri] += 1

    # Sort status codes in ascending order
    sorted_status_codes = sorted(uri_status_count.keys(), key=int)

    print("Status Code\tCount\t\tURI")
    print("-------------------------------------------")
    for status_code in sorted_status_codes:
        uri_counts = uri_status_count[status_code]
        sorted_uris = sorted(uri_counts.keys(), key=lambda uri: (len(uri), uri))
        
        for uri in sorted_uris:
            count = uri_counts[uri]
            print(f"{status_code}\t\t{count}\t{uri}")

def request_inspector():
    file_path = "logs/20230805_002725_www.google.com/log_file.json"
    request_status_count = defaultdict(lambda: defaultdict(int))

    with open(file_path, "r") as file:
        data = json.load(file)

    for entry in data:
        request = entry["request"]
        status_code = entry["status_code"]
        request_status_count[request][status_code] += 1

    # Sort requests alphabetically
    sorted_requests = sorted(request_status_count.keys(), key=lambda request: (len(request), request))

    print("Request\t\t\tStatus Code\tCount")
    print("-------------------------------------------")
    for request in sorted_requests:
        status_counts = request_status_count[request]
        sorted_status_codes = sorted(status_counts.keys(), key=int)
        
        for status_code in sorted_status_codes:
            count = status_counts[status_code]
            print(f"{request}\t{status_code}\t\t{count}")


def request_inspector_CC_add_content():
    file_path = "logs/20230806_172732_www.google.com/log_file.json"
    

    with open(file_path, "r") as file:
        data = json.load(file)

    for entry in data:
        request_lines = entry['request'].split('\r\n')
        has_content_length = any('Content-Length' in line for line in request_lines)

    content_length_counts = defaultdict(int)
    status_code_counts_with_content_length = defaultdict(int)
    status_code_counts_without_content_length = defaultdict(int)

    for entry in data:
        request_lines = entry['request'].split('\r\n')
        has_content_length = any('Content-Length' in line for line in request_lines)
        
        content_length_counts[has_content_length] += 1
        status_code = entry['status_code']
        
        if has_content_length:
            status_code_counts_with_content_length[status_code] += 1
        else:
            status_code_counts_without_content_length[status_code] += 1


    print("Content-Length Counts:")
    print(content_length_counts)

    print("\nStatus Code Counts with Content-Length:")
    print(status_code_counts_with_content_length)

    print("\nStatus Code Counts without Content-Length:")
    print(status_code_counts_without_content_length)

# Call the function to execute
request_inspector_CC_add_content()

