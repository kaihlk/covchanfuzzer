import random
import string
import urllib.parse
import csv
import matplotlib.pyplot as plt
import numpy as np

# Function to generate a random fragment with custom mean and standard deviation
# (Same function as in the previous response)

http_request5 = "GET https://www.zoho.com/de/ HTTP/1.1\r\nHost: www.zoho.com\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.5\r\nDNT: 1\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\nSec-Fetch-Dest: document\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-Site: cross-site\r\nDj33M1E07A38HhbW: fT8BeP9A61QC3YTn\r\nwjlZbVJPoyV02gXc: 8mbRiL0b6B8D3A6I\r\nyd3WcTgSE7Pua0lJ: ovuZFOJ9VVhgI0ky\r\nOaFLQVX2CIY05rAo: yLsrtq6mdsSqNvbS\r\nqPSUK96Yo8xZCFyJ: yDrOwcDMBbJ1WMPu\r\nHead-Count: 1\r\n\r\n"
http_request2 = "GET https://www.zoho.com/de/ HTTP/1.1\r\nHost: www.zoho.com\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.5\r\nDNT: 1\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\nSec-Fetch-Dest: document\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-Site: cross-site\r\nwyLwC2a1zj961iZF: 1Qxf0l0gogWAoooA\r\nVAaEijqRLrDucYmN: feKTmGCQdUaqpOoD\r\nHead-Count: 1\r\n\r\n"
http_request1 = "GET https://www.zoho.com/de/ HTTP/1.1\r\nHost: www.zoho.com\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.5\r\nDNT: 1\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\nSec-Fetch-Dest: document\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-Site: cross-site\r\nvBqZm9bixtllMPIG: suqTFH0LPYEYNC6l\r\nHead-Count: 1\r\n\r\n"
http_request0 = "GET  HTTP/1.1\r\nHost: \r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.5\r\nDNT: 1\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\nSec-Fetch-Dest: document\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-Site: cross-site\r\n\r\n"

length_of_request5 = len(http_request5)
length_of_request2 = len(http_request2)
length_of_request1 = len(http_request1)
length_of_request0 = len(http_request0)
print("5: ",length_of_request5)
print("2: ",length_of_request2)
print("1: ",length_of_request1)
print("0: ", length_of_request0)

"""# Parameters
print(" ",length_of_request)
n = 1000  # Number of iterations
min_length = 1
max_length = 100  # Maximum length set to 100 (1-100 range)
fuzzvalue = 0.1  # Adjust as needed

# Parameter set for the exponential distribution
scale = 20  # You can adjust this value to control the shape of the distribution

# Generate fragments and store their lengths using the exponential distribution
lengths = np.random.exponential(scale, n).round().astype(int)

lengths[lengths > max_length] = max_length

# Plot the distribution
plt.figure(figsize=(10, 6))
plt.hist(lengths, bins=1000, density=True, alpha=0.6, color='b', label="Exponential Distribution")

# Configure the plot
plt.title("Distribution of Fragment Lengths")
plt.xlabel("Length")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True)
plt.show()"""