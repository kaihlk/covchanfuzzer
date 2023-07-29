#main
from runner import ExperimentRunner





def main():
    '''Function that runs the connection, selection of the CC and the fuzzer, should be cleaned up and externalised'''
    # TODO
    # host and channelselction, number of attempts as arguments?

    # Add a cautios mode that leaves some time between requests to the same adress (Not getting caught by Denial of service counter measures)
    # Add a mode that sends a well formed request every x attempts to verify not being blocked

    # Control the body of the response as well (?)

    # Experiment Configuration Values
    experiment_configuration = {
        "comment": "Some text describing the Testrun",
        "covertchannel_number": 3,
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
