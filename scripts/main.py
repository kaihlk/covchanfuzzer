from custom_http import CustomHTTP
import http_utils

hosts = [
    ('www.example.com', 80),
   # ('www.google.com', 80),
  # ('www.amazon.com', 443)
]

def main():
    # Select the method for forging the header
    method = 2
    # Number of attempts
    num_attempts = 10

    


    for _ in range(num_attempts):
        
        for targethost, targetport in hosts:
            #Todo:   Baseline Check if Client is not blocked yet
            
            request, deviation_count = http_utils.forge_http_request(targethost, method)

            # Send the HTTP request and get the response        
           
            response=CustomHTTP().http_request(host=targethost, port=targetport, customRequest=request)

            # Print the response status code and deviation count
            print("Host: {}".format(targethost))
            print("Port: {}".format(targetport))
            print("Status Code: {}".format(response.Status_Code.decode('utf-8')))
            print("Deviation Count: {}\n".format(deviation_count))
            

            #ToDo Save request, deviation, status_code maybe response Time? 


            

if __name__ == '__main__':
    main()
