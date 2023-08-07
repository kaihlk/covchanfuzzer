#main

from runner import ExperimentRunner
import class_mapping
##For Infoe
""" class_mapping_requests ={
    1: HTTP1_Request_Builder,
    2: HTTP1_Request_CC_Case_Insensitivity,
    3: HTTP1_Request_CC_Random_Whitespace,
    4: HTTP1_Request_CC_Reordering_Header_Fields,
    5: HTTP1_Reqeust_CC_URI_RepresenaURtion,
    6: HTTP1_Request_CC_URI_Case_Insentivity,
    7: HTTP1_Reqeust_CC_URI_Hex_Hex,
    8: HTTP1_Request_CC_Random_Content,
    9: HTTP1_Request_CC_Random_Content_No_Lenght_Field,

}

class_mapping_connection = {
    1: HTTP1_TCP_Connection,
    2: HTTP1_TLS_Connection,
    3: HTTP1_CC_TCP2TLS_Upgrade,
    4: HTTP2_TLS_Connection
    }

class_mapping_timing  = {
    1: Standard,
    2: Frequency_Modulation,
    3: Amplitude_Modulation,
} """

def main():
    '''Function that runs the connection, selection of the CC and the fuzzer'''
    # TODO
    # host and channelselction, number of attempts as arguments?

    # Add a cautios mode that leaves some time between requests to the same adress (Not getting caught by Denial of service counter measures)
    # Add a mode that sends a well formed request every x attempts to verify not being blocked

    # Control the body of the response as well (?)
    #Add Verbose mode

    # Experiment Configuration Values
   # try:
    experiment_configuration = {
        "comment": "Test: google.com_Add_Content_to_get_request",
        "covertchannel_request_number": 4,
        "covertchannel_connection_number": 1,
        "covertchannel_timing_number": 1,
        "content": "random",  #"random", "some_text"  
        "num_attempts": 100,
        "wait_between_request": 0,
        "base_line_check_frequency": 0,
        "conn_timeout": 0.5,
        "nw_interface": "lo",#"enp0s3",  #lo, docker, enp0s3
        "fuzz_value": 0.9,
        "use_ipv4": True,
        "use_TLS": False,
        "target_host": "localhost",
        "target_port": 8080, #443, 8080 Apache
        "method" : "TRACE",
        "url": "/",
        "headers": None,
        "standard_headers": "firefox_HTTP/1.1",  #curl_HTTP/1.1(TLS), firefox_HTTP/1.1, firefox_HTTP/1.1_TLS, chromium_HTTP/1.1, chromium_HTTP/1.1_TLS"
        "verbose": True,    

    }
    ExperimentRunner(experiment_configuration).setup_and_start_experiment()
    #except Exception as ex:
     #   print("Error: ", str(ex))

if __name__ == "__main__":
    main()
