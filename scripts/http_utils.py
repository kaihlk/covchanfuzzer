# http_utils.py
import random
import urllib.parse
#from scapy.layers.http import *

def generate_chromium_header(url):
    headers = [
        ('Host', url),
        ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Accept-Language', 'en-US,en;q=0.9'),
        ('Connection', 'keep-alive')
    ]

    request_string = f"GET / HTTP/1.1\r\n"
    for header in headers:
        request_string += f"{header[0]}: {header[1]}\r\n"
    request_string += "\r\n"

    return request_string, 0


def generate_chromium_header_with_random_case(url):
    headers = [
        ('Host', url),
        ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Accept-Language', 'en-US,en;q=0.9'),
        ('Connection', 'keep-alive')
    ]

    request_string = f"GET / HTTP/1.1\r\n"
    deviation_count = 0

    original_request = request_string  # Save the original request

    for header in headers:
        field_name, field_value = header

        # Randomly change the case of the field name
        modified_field_name = ''.join(
            random.choice([c.lower(), c.upper()]) for c in field_name
        )

        request_string += f"{modified_field_name}: {field_value}\r\n"

    request_string += "\r\n"

    # Compare the modified request with the original request
    for c1, c2 in zip(generate_chromium_header(url)[0], request_string):
        if c1 != c2:
            deviation_count += 1

    return request_string, deviation_count


def generate_chromium_header_with_random_whitespace(url, limit=10):
    headers = [
        ('Host', url),
        ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Accept-Language', 'en-US,en;q=0.9'),
        ('Connection', 'keep-alive')
    ]

    request_string = f"GET / HTTP/1.1\r\n"
    deviation_count = 0

    for header in headers:
        field_name, field_value = header
        whitespace = ''.join(random.choice(['\t', ' ']) for _ in range(limit))
        field_value += whitespace
        request_string += f"{field_name}: {field_value}\r\n"
        deviation_count += len(whitespace.replace('\t', ''))

    request_string += "\r\n"

    return request_string, deviation_count



def generate_chromium_header_reorder_fields(url):
    # Define the original header order
    original_headers = [
        ('Host', url),
        ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Accept-Language', 'en-US,en;q=0.9'),
        ('Connection', 'keep-alive')
    ]

    # Shuffle the header fields randomly
    shuffled_headers = original_headers[:]
    random.shuffle(shuffled_headers)

    # Initialize the request string
    request_string = f"GET / HTTP/1.1\r\n"

    # Initialize the deviation count
    deviation_count = 0

    # Iterate over the shuffled headers and compare with the original order
    for shuffled_header, original_header in zip(shuffled_headers, original_headers):
        # Check if the header is not 'Host' and the order has deviated
        if shuffled_header[0] != 'Host' and shuffled_header != original_header:
            deviation_count += 1  # Increment the deviation count
        request_string += "{header_name}: {header_value}\r\n".format(header_name=shuffled_header[0], header_value=shuffled_header[1])

    # Add the final line break to the request string
    request_string += "\r\n"

    # Return the request string and deviation count
    return request_string, deviation_count


###Not working properly
### need testing
### 
def generate_chromium_header_change_uri_representation(url, port=None):
    deviation_count = 0

    if port and random.random() < 0.5:
        url += ':{}'.format(port)
        deviation_count += 1

    if random.random() < 0.5:
        if port == 80:
            url = 'http://' + url
        elif port == 443:
            url = 'https://' + url
        else:
            url = random.choice(['http://', 'https://']) + url
        deviation_count += 1

    if random.random() < 0.5:
        url += '/'
        deviation_count += 1

        # Add random component after the ending slash
        component = random.choice(['', '?', '%3F'])
        url += component
        if component == '%3F':
            deviation_count += 2
        elif component != '':
            deviation_count += 1

    headers = [
        ('Host', url),
        ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Accept-Language', 'en-US,en;q=0.9'),
        ('Connection', 'keep-alive')
    ]

    request_string = f"GET / HTTP/1.1\r\n"

    for header in headers:
        request_string += f"{header[0]}: {header[1]}\r\n"

    request_string += "\r\n"

    return request_string, deviation_count


def forge_http_request(url, port, method):
    if method == 1:
        return generate_chromium_header(url)
    elif method == 2:
         return generate_chromium_header_with_random_case(url)
    elif method == 3:
        return generate_chromium_header_with_random_whitespace(url)
    elif method == 4:
        return generate_chromium_header_reorder_fields(url)
    elif method == 5:
        return generate_chromium_header_change_uri_representation(url, port)
    else:
        raise ValueError("Invalid method number. Supported methods are 1, 2, 3, 4 and 5.")

