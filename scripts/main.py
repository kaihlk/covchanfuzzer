#main
from runner import ExperimentRunner

""" class_mapping_requests ={
    1: HTTP1_Request_Builder,
    2: HTTP1_Request_CC_Case_Insensitivity,
    3: HTTP1_Request_CC_Random_Whitespace,
    4: HTTP1_Request_CC_Reordering_Header_Fields,
    5: HTTP1_Reqeust_CC_URI_Represenation,
    6: HTTP1_Request_CC_URI_Case_Insentivity,
    7: HTTP1_Reqeust_CC_URI_Hex_Hex,
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

    # Experiment Configuration Values
    experiment_configuration = {
        "comment": "Some text describing the Testrun",
        "covertchannel_request_number": 3,
        "covertchannel_connection_number": 1,
        "covertchannel_timing_number": 1,
        "num_attempts": 100,
        "conn_timeout": 20.0,
        "nw_interface": "lo",
        "fuzz_value": 0.5,
        "use_ipv4": True,
        "target_host": "localhost",
        "target_port": 8080,
    }
    ExperimentRunner(experiment_configuration).setup_and_start_experiment()


if __name__ == "__main__":
    main()
