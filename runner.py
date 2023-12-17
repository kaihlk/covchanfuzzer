# runner.py
# runs a http fuzzing experiment


import concurrent.futures
import time
import logging
import hashlib
import threading
import random
import pandas
import http1_covert_channels
from logger import ExperimentLogger, TestRunLogger
from custom_http_client import CustomHTTP
from host_crawler import host_crawler
import class_mapping
import http1_request_builder as request_builder
import target_list_preparator
import exp_analyzer


class ExperimentRunner:
    '''Runs the experiment'''

    def __init__(self, experiment_configuration, target_list, global_log_folder):
        self.experiment_configuration = experiment_configuration
        self.global_log_folder = global_log_folder
        self.target_list = target_list
        self.lock_ptl = threading.Lock()
        self.processed_targets = []
        self.base_check_fails = []
        self.lock_bcf = threading.Lock()
        self.dns_fails = []
        self.lock_df = threading.Lock()
        self.message_count = 0
        self.lock_mc = threading.Lock()
        self.prerequest_list = []
        self.lock_prl = threading.Lock()
        self.exp_log = None
        self.pd_matrix = pandas.DataFrame(columns=["Attempt No.\Domain"])
        self.lock_matrix = threading.Lock()
        self.runner_logger = logging.getLogger('main.runner')
        self.error_event = threading.Event()
        self.cc_uri_post_generation = False
        self.uri_deviation_table = pandas.DataFrame(
            columns=["Deviation Count"])
        self.rel_uri_deviation_table = pandas.DataFrame(
            columns=["Relative Deviation"])
        self.lock_udt = threading.Lock()
 
    def get_target_subset(self, target_dataframe, start_position=0, length=10):
        """Takes a subset from the target DataFrame to reduce the traffic to one target."""
        # Check inputs
        if start_position < 0 or start_position + length > len(target_dataframe):
            raise ValueError("Invalid start_position")

        # Prevent length from exceeding the DataFrame length
        length = min(length, len(target_dataframe) - start_position)

        # Extract the subset of the DataFrame
        subset = target_dataframe.iloc[start_position:start_position + length]

        return subset


    def baseline_check(self):
        """Check if the host is not blocking the request due to detection"""
        # TODO: TLS Rebuild Messages doesnt work
        return True

    

    def pregenerate_request(self, covert_channel, attempt_no):
        '''Build a HTTP Request Message'''
        unique = False
        min_fuzz_value = self.experiment_configuration["min_fuzz_value"]
        deviation_count_spread = False
        maximum_retries = 100*self.experiment_configuration["num_attempts"]
        retry = 0
        random_element = random.random()
        new_fuzz_value = min_fuzz_value + \
            (random_element * (1-2*min_fuzz_value))
        selected_covert_channel = class_mapping.requests_builders[covert_channel](
        )

        
        #Need to be implemented
        if covert_channel == 0:
            request, deviation_count, uri = self.get_prerequest_from_list(
                attempt_no, self.experiment_configuration["CSV_request_list"])

        elif covert_channel == 1:
            request, deviation_count, uri = selected_covert_channel.generate_request(
                self.experiment_configuration, self.experiment_configuration["target_port"], new_fuzz_value)
            request_hash = hashlib.md5(str(request).encode()).hexdigest()
        else:

            # Break the loop if the prerequest is unique or the deviation count is accpeted
            while unique is False or deviation_count_spread is False:
                try:
                    deviation_count_spread = False
                    deviation_count_found = False
                    deviation_count = 0
                    # Make sure, that a least a bit of cc data is added
                    self.cc_uri_post_generation = False
                    while self.cc_uri_post_generation is False and deviation_count == 0:
                        request, deviation_count, uri = selected_covert_channel.generate_request(
                            self.experiment_configuration, self.experiment_configuration["target_port"], new_fuzz_value)
                        request_hash = hashlib.md5(
                            str(request).encode()).hexdigest()

                        self.cc_uri_post_generation = selected_covert_channel.get_cc_uri_post_generation()

                    # Some CC may be added after pregeneration, example changing the URI, would lead needlessly to RunTime Exception
                    if self.cc_uri_post_generation is False:
                        # First Entry is always unique
                        if len(self.prerequest_list) == 0:
                            unique = True
                            deviation_count_spread = True
                        # Iterate through prerequest list to check if entry is already existing or a similar entry within 5% deviation_count isn  already existing
                        for entry in self.prerequest_list:
                            # Found if is within 5% range
                            if abs(deviation_count - entry["deviation_count"]) < deviation_count*0.05:
                                deviation_count_found = True
                            # Check uniqueness
                            if request_hash != entry["request_hash"]:
                                if covert_channel==3:
                                    if deviation_count==entry["deviation_count"]:
                                        unique=False
                                        random_element = random.random()
                                        new_fuzz_value = min_fuzz_value +  (random_element * (1-2*min_fuzz_value))
                                        break
                                    else:
                                        unique=True
                                else:
                                    unique = True
                            # Break if already existing
                            else:
                                random_element = random.random()
                                new_fuzz_value = min_fuzz_value + \
                                    (random_element * (1-2*min_fuzz_value))
                                unique = False
                                break
                        # Prevent endless loop if all variations have been tried, save them for later check

                        if retry > maximum_retries:
                            self.exp_log.save_prerequests(self.prerequest_list)
                            raise RuntimeError(
                                "Unable to generate a unique prerequest after maximum retries.")
                        # Mechanismus to higher the spread of different deviation counts
                        retry += 1
                        if deviation_count_found is True:
                            if random.random() > self.experiment_configuration["spread_deviation"]:
                                deviation_count_spread = True
                            else:
                                retry -= 1
                                random_element = random.random()
                                new_fuzz_value = min_fuzz_value + \
                                    (random_element * (1-2*min_fuzz_value))

                                print("New Fuzz Value: ", new_fuzz_value)
                        else:
                            deviation_count_spread = True
                    else:
                        # If CC Variation is added later skip the unique check
                        unique = True
                        deviation_count_spread = True
                except Exception as e:
                    self.runner_logger.error("Error generating request: %s", e)
                    self.error_event.set()
                    raise

        if self.experiment_configuration["verbose"] is True:
            print(request)
        prerequest = {
            "no": 0,
            "request": request,
            "request_hash": request_hash,
            "deviation_count": deviation_count,
            "uri": uri,
            "1xx": 0,
            "2xx": 0,
            "3xx": 0,
            "4xx": 0,
            "5xx": 0,
            "9xx": 0,
        }

        return prerequest

    def get_prerequest_from_list(self, attempt, request_list):
        """TODO: Loads pregenerated HTTP Requests from a external source"""
        uri = ""
        request = ""
        deviation_count = 0
        return request, deviation_count, uri

    def get_next_prerequest(self, attempt_number):
        """Get next Prerequest from Prerequest List or create and add to list if not existing"""
        # Thread safe
        with self.lock_prl:
            # Check if new prerequest needs to be get
            if attempt_number >= len(self.prerequest_list):
                prerequest = self.pregenerate_request(
                    self.experiment_configuration["covertchannel_request_number"], attempt_number)
                self.prerequest_list.append(prerequest)
            # Or take it from the Prerequest List
            else:
                prerequest = self.prerequest_list[attempt_number]
        return prerequest

    def add_entry_to_pd_matrix(self, domain, attempt_no, response_line):
        """Save response and prerequest no to a matrix for further analysation"""
        if response_line is not None:
            response_status_code = response_line["status_code"]
        else:
            response_status_code = 999
        # Ensure the "Domain" column is present in the DataFrame
        with self.lock_matrix:
            if domain not in self.pd_matrix.index:
                self.pd_matrix.at[domain, "Attempt No.\Domain"] = domain
            self.pd_matrix.at[domain, attempt_no] = response_status_code

        return

    def add_status_code_to_prerequest_list(self, attempt_no, response_line):
        """Save Response Statuscode to prerequest_list"""
        with self.lock_prl:
            self.prerequest_list[attempt_no]["no"] = attempt_no
            if response_line is not None:
                response_status_code = response_line["status_code"]
            else:
                response_status_code = 999
            first_digit = str(response_status_code)[0]
            if first_digit == "1":
                self.prerequest_list[attempt_no]["1xx"] += 1
            elif first_digit == "2":
                self.prerequest_list[attempt_no]["2xx"] += 1
            elif first_digit == "3":
                self.prerequest_list[attempt_no]["3xx"] += 1
            elif first_digit == "4":
                self.prerequest_list[attempt_no]["4xx"] += 1
            elif first_digit == "5":
                self.prerequest_list[attempt_no]["5xx"] += 1
            else:
                self.prerequest_list[attempt_no]["9xx"] += 1
        return

    def add_devcount_and_status_code_to_df(self, deviation_count, response_line, uri):
        """Save Response Statuscode to URI Table"""
        with self.lock_udt:
            if response_line is not None:
                response_status_code = response_line["status_code"]
            else:
                response_status_code = 999
            first_digit = str(response_status_code)[0]
            category = first_digit + "xx"

            if category not in self.uri_deviation_table.columns:
                self.uri_deviation_table[category] = 0

            if category not in self.rel_uri_deviation_table.columns:
                self.rel_uri_deviation_table[category] = 0

            if deviation_count <= 0:
                rel_deviation = 0
            # Calculate relative change in percentage  
            # Count only letters
            letter_count = sum(1 for char in uri if char.isalpha())
            rel_deviation = (deviation_count / letter_count) * 100
            
            # Round to the nearest whole percent
            rel_deviation = round(rel_deviation)

            # RELATIV DF
            if rel_deviation not in self.rel_uri_deviation_table["Relative Deviation"].values:
                new_row = {"Relative Deviation": rel_deviation}
                for col in self.rel_uri_deviation_table.columns:
                    if col != "Relative Deviation":
                        new_row[col] = 0

                # Create a new DataFrame with the new row
                new_df = pandas.DataFrame([new_row])

                # Concatenate the new DataFrame with the existing DataFrame
                self.rel_uri_deviation_table = pandas.concat(
                    [self.rel_uri_deviation_table, new_df], ignore_index=True)

            # ABSOLUT DF
            # Check if the deviation_count row already exists in the DataFrame
            if deviation_count not in self.uri_deviation_table["Deviation Count"].values:
                new_row = {"Deviation Count": deviation_count}
                for col in self.uri_deviation_table.columns:
                    if col != "Deviation Count":
                        new_row[col] = 0

                # Create a new DataFrame with the new row
                new_df = pandas.DataFrame([new_row])

                # Concatenate the new DataFrame with the existing DataFrame
                self.uri_deviation_table = pandas.concat(
                    [self.uri_deviation_table, new_df], ignore_index=True)

            # Find the index of the deviation_count row
            row_index = self.uri_deviation_table.index[self.uri_deviation_table["Deviation Count"] == deviation_count].tolist()[
                0]
            rel_row_index = self.rel_uri_deviation_table.index[self.rel_uri_deviation_table["Relative Deviation"] == rel_deviation].tolist()[
                0]

            # Get the current count for the specified category
            count = self.uri_deviation_table.at[row_index, category]
            rel_count = self.rel_uri_deviation_table.at[rel_row_index, category]
            # Increment the value in the specified category column
            self.uri_deviation_table.at[row_index, category] = count + 1
            self.rel_uri_deviation_table.at[rel_row_index,
                                            category] = rel_count + 1

            # Sort the DataFrame by "Deviation Count" in ascending order
            self.uri_deviation_table = self.uri_deviation_table.sort_values(
                by="Deviation Count", ascending=True)
            self.rel_uri_deviation_table = self.rel_uri_deviation_table.sort_values(
                by="Relative Deviation", ascending=True)
        return

    def check_content(self, body):
        # TODO add hash or check length function and standard body
        return True

    def send_and_receive_request(self, attempt_number, request, deviation_count, uri, host_data, log_path):
        """Send the request and receive response"""
        response_line, response_header_fields, body, measured_times, error_message = CustomHTTP().http_request(
            host=host_data["host"],
            use_ipv4=self.experiment_configuration["use_ipv4"],
            port=host_data["port"],
            host_ip_info=host_data["socket_info"],
            custom_request=request,
            timeout=self.experiment_configuration["conn_timeout"],
            verbose=self.experiment_configuration["verbose"],
            log_path=log_path,  # Transfer to save TLS Keys
        )
        if self.experiment_configuration["verbose"] is True:
            print("Response:", response_line)

        return response_line, response_header_fields, body, measured_times, error_message

    def run_experiment_subset(self, logger_list, sub_set_dns):
        '''Run the experiment'''

        for i in range(self.experiment_configuration["num_attempts"]):
            if self.error_event.is_set():
                break
            try:
                prerequest = self.get_next_prerequest(i)
            except RuntimeError as e:
                self.runner_logger.error(
                    "Error getting Prerequest from list %s", e)
                raise
            except Exception as e:
                self.runner_logger.error(
                    "Error getting Prerequest from list %s", e)

            # for host_data,logger in zip(sub_set_dns, logger_list):

            for host_data, logger in zip(sub_set_dns.iterrows(), logger_list):
                host_data = host_data[1]

            # Round Robin one Host after each other
                if self.baseline_check() is False:
                    # TODO, raise error
                    print("Baseline Check Failure, Connection maybe blocked")
                else:
                    # Send the HTTP request and get the response in the main threads
                    try:
                        # Adapt the prerequest to the host
                        uri = host_data["uri"]
                        socket_dns_info = host_data["socket_dns_info"]
                        selected_covert_channel = class_mapping.requests_builders[
                            self.experiment_configuration["covertchannel_request_number"]]()

                        path = selected_covert_channel.path_generator(
                            host_data["paths"], test_path=self.experiment_configuration["path"], fuzzvalue=self.experiment_configuration["min_fuzz_value"])

                        # INSERT CLEVER DEVIATION SPREADER HERE
                        request, deviation_count_uri, uri = selected_covert_channel.replace_host_and_domain(prerequest["request"], uri, self.experiment_configuration["standard_subdomain"], socket_dns_info["host"], include_subdomain_host_header=self.experiment_configuration["include_subdomain_host_header"], path=path, override_uri="",  fuzzvalue=self.experiment_configuration["min_fuzz_value"])
                        deviation_count_request = prerequest["deviation_count"]
                        deviation_count = deviation_count_uri+deviation_count_request

                    except Exception as e:
                        self.runner_logger.error(
                            "Error building request for host: %s", e)
                    try:
                        start_time = time.time()
                        response_line, response_header_fields, body, measured_times, error_message = self.send_and_receive_request(
                            i,
                            request,
                            deviation_count,
                            uri,
                            socket_dns_info,
                            logger.get_logging_folder())
                        logger.add_request_response_data(
                            i, request, deviation_count, uri, response_line, response_header_fields, body, measured_times, error_message)
                        try:
                            self.add_status_code_to_prerequest_list(
                                i, response_line)
                        except Exception as e:
                            self.runner_logger.error(
                                "Exception during updating request_list: %s", e)
                        try:
                            self.add_entry_to_pd_matrix(
                                i, host_data["tranco_domain"], response_line)
                        except Exception as e:
                            self.runner_logger.error(
                                "Exception during updating request matrix: %s", e)
                        self.add_devcount_and_status_code_to_df(
                            deviation_count_uri, response_line, uri)

                        self.check_content(body)
                        with self.lock_mc:
                            self.message_count += 1
                        end_time = time.time()
                        response_time = end_time-start_time
                        print(" Message No: " + str(self.message_count)+" Host: "+str(
                            host_data["tranco_domain"])+" Complete Message Time: " + str(response_time))
                    except Exception as e:
                        self.runner_logger.error(
                            "Error sending/receiving request: %s", e)
        return

    def fuzz_subset(self, df_target_list, start_position, subset_length):
        """Take the subset from target_list, start a logger for domain and execute Experiment"""
        try:
            subset = self.get_target_subset(
                df_target_list, start_position, subset_length)
        except Exception as e:
            self.runner_logger.error(
                "Error while getting subset objects: %s", e)
        # Initialise Logger List
        logger_list = []
        # Create logger object for each target in subset_dns
 
        # Start the processing of the subset_dns and its corresponding loggers
        for index, target_info in subset.iterrows():
            try:
                host_ip_info = target_info["socket_dns_info"]
                logger = TestRunLogger(
                    self.experiment_configuration,
                    self.exp_log.get_experiment_folder(),
                    host_ip_info,
                    target_info["tranco_domain"],
                    host_ip_info["ip_address"],
                    host_ip_info["port"],
                    target_info["paths"],
                    target_info["uri"]
                )
                logger_list.append(logger)
            except Exception as e:
                self.runner_logger.error(
                    "Error while creating logger objects: %s", e)

        # RUN the Experiment
        try:
            self.run_experiment_subset(logger_list, subset)
        except RuntimeError as e:
            self.runner_logger.error(
                "Exception during run_experiment_subset: %s", e)
            raise
            return subset
        except Exception as e:
            self.runner_logger.error(
                "Exception during run_experiment_subset: %s", e)
        # Save Log files in the logger files
        for logger in logger_list:
            try:
                logger.save_logfiles()
            except Exception as e:
                self.runner_logger.error(
                    "Exception during saving log_files: %s", e)
        return subset


    def setup_and_start_experiment(self):
        '''Setups the Experiment, creates an experiment logger, and starts the experiment run'''
        start_time = time.time()
        try:
            
            # Create Folder for the experiment and save the path
            self.exp_log = ExperimentLogger(
                self.experiment_configuration, self.global_log_folder)

            # Start Global Capturing Process

            global_stop_event = threading.Event()
            global_capture_thread = threading.Thread(
                target=self.exp_log.capture_packets_dumpcap, args=(global_stop_event,))
            global_capture_thread.start()
            time.sleep(1)

            list_preparator = target_list_preparator.TargetListPreperator(
                self.experiment_configuration, self.exp_log)
            df_target_list, invalid_entries = list_preparator.prepare_target_list()


            # Initialize
            fuzz_tasks = []
            subset_length = self.experiment_configuration["target_subset_size"]
            max_workers = self.experiment_configuration["max_workers"]
            # Check max ative workers depending on configuration
            max_active_workers = max(
                self.experiment_configuration["max_targets"]/subset_length, 1)
            if max_active_workers > self.experiment_configuration["max_workers"]:
                max_active_workers = self.experiment_configuration["max_workers"]
            active_workers = 0
            processed_targets = 0
            start_position = 0

            # Iterate through target list
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.experiment_configuration["max_workers"]) as fuzz_executor:
                # Iterate though the list, if DNS Lookups or Basechecks fail, the entry from the list is droped and a new entry will be appended
                # Take subsets from target_list until the the processed targets are equal or less than  configured max_targets
                while processed_targets < self.experiment_configuration["max_targets"]:
                    # Create futures until max__active workers

                    while active_workers < max_active_workers:
                        # If target_list limit is reached, break_
                        # len(prepared_target_list):
                        if start_position+subset_length > df_target_list.shape[0]:
                            #    #Raise Error?
                            subset_length -= 1
                            break
                            # Get DNS Infomation for the subset, if the lookup fails for an entry the subset will be shortened
                        try:
                            fuzz_task = fuzz_executor.submit(
                                self.fuzz_subset, df_target_list, start_position, subset_length)  # prepared_target_list

                            # Get a subset with valid entries
                            # Shift the start position for next iteration

                            start_position += subset_length
                            # Submit the subset for processing to executor
                            fuzz_tasks.append(fuzz_task)
                            active_workers += 1
                            if self.error_event.is_set():
                                break

                        except Exception as e:
                            self.runner_logger.error(
                                "Error during subset Fuzzing DNS Lookups for subset: %s", e)
                            active_workers -= 1
                            continue
                    if self.error_event.is_set():
                        break

                    # Wait for a completed task

                    completed_tasks, _ = concurrent.futures.wait(
                        fuzz_tasks, return_when=concurrent.futures.FIRST_COMPLETED)
                    for completed_task in completed_tasks:
                        try:
                            processed_targets += len(completed_task.result())

                        except Exception as e:
                            self.runner_logger.error(
                                "Error while processing completed task: %s", e)
                        finally:
                            # Remove the task from the list
                            fuzz_tasks.remove(completed_task)
                            active_workers -= 1

        except RuntimeError as e:
            self.runner_logger.error(
                "During the experiment an error occured" %s, e)
            raise

        except Exception as e:
            self.runner_logger.error(
                "During the experiment an error occured %s", e)
        finally:
            # Wait for the global capture thread to finish
            global_stop_event.set()

            global_capture_thread.join()
            end_time = time.time()
            duration = end_time-start_time
            print("Experiment Duration(s):", duration)
            print("Processed Targets: ", processed_targets)
            # Save OutCome to experiment Folder csv.
            try:

                self.exp_log.add_global_entry_to_experiment_list(
                    self.experiment_configuration["experiment_no"])
                #self.exp_log.save_dns_fails(self.dns_fails)
                #self.exp_log.save_target_list(self.processed_targets)
                #self.exp_log.save_base_checks_fails(self.base_check_fails)
                self.exp_log.save_prerequests(self.prerequest_list)
                self.exp_log.prerequest_statisics(
                    self.prerequest_list, self.message_count)
                self.exp_log.uri_deviation_table(
                    self.uri_deviation_table, self.rel_uri_deviation_table)
                self.exp_log.save_pdmatrix(self.pd_matrix)
                self.exp_log.save_exp_stats(
                    duration, self.message_count, invalid_entries)
                exp_analyzer.Domain_Response_Analyzator(
                    self.exp_log.get_experiment_folder()).start()
                # self.exp_log.analyze_prerequest_outcome()
            except Exception() as e:
                self.runner_logger.error(
                    "Exception During saving the Experiment Logs/Results: %s", e)
            finally:
                self.exp_log.copy_log_file()
        return
