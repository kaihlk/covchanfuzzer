from custom_http import CustomHTTP
import http_utils 
import mutators
import random
#Todo
#host and channelselction, number of attempts as arguments?
#host and channels as a file?
#auto capture the packets, tls with wireshark/tshark
# Data Output: Host, port, Channel, Request Packet, Answer Status Code
#Add a mode that leaves some time between requests to the same adress (Not getting caught by Denial of service counter measures)
# Add a mode that sends a well formed request every x attempts to verify not being blocked
# Control the body of the response as well (?)

hosts = [
    ('www.example.com', 80),
  #  ('www.google.com', 80),
   #('www.amazon.com', 443)
]
SampleString="Hallo Welt!"


def main():
    print(SampleString)
    print(mutators.delete_random_char(SampleString))
    print(mutators.insert_random_char(SampleString))
    print(mutators.random_switch_case_of_char_in_string(SampleString))
    print(mutators.random_switch_chars(SampleString))
    print(mutators.random_slice_and_swap_string(SampleString))
    print(SampleString+mutators.generate_random_string(" \t", random.randint(0,10))+"<--")
    print(mutators.generate_random_string(SampleString, 15))
    
"""  # Select the method for forging the header
    covertchannel_number = 7
    # Number of attempts
    num_attempts = 10
    ok=0
    for _ in range(num_attempts):
        
        for targethost, targetport in hosts:
            #Todo:   Baseline Check if Client is not blocked yet
       
            request, deviation_count = http_utils.forge_http_request(cc_number=covertchannel_number, host=targethost, port=targetport, url='/', method="GET", headers=None, fuzzvalue=0.1)

            # Send the HTTP request and get the response        
           
            response=CustomHTTP().http_request(host=targethost, port=targetport, customRequest=request)
            response_status_code=response.Status_Code.decode('utf-8')

            # Print the response status code and deviation count
            print("Host: {}".format(targethost))
            print("Port: {}".format(targetport))
            print("Status Code: {}".format(response.Status_Code.decode('utf-8')))
            print("Deviation Count: {}\n".format(deviation_count))

            if response_status_code=='200':
                ok+=1
            #ToDo Save request, deviation, status_code maybe response Time? 
    print('Successfull packets: '+str(ok) + ' of '+str(num_attempts)+ ' attempts.') """

            

if __name__ == '__main__':
    main()
