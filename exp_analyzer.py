# Experimentdata-Analysisation-Domain-Statuscode
import pandas as pandas
import os
import ast
import json
import matplotlib
import logging
import matplotlib.pyplot as mpl
import numpy as numpy
from urllib.parse import urlparse
from sklearn.cluster import KMeans
from matplotlib.ticker import PercentFormatter
import seaborn as sns
from scipy.stats import norm
from scipy import stats
from scipy.optimize import curve_fit
from matplotlib.gridspec import GridSpec
from scipy.interpolate import interp1d
from http1_request_builder import HTTP1_Request_Builder

class Domain_Response_Analyzator():
    def __init__(self, path):
        self.log_dir=self.get_logs_directory()
        self.exp_path = path
        self.data_frame_exp_stats = pandas.read_csv(
            path+"/experiment_stats.csv")
        self.data_frame_prerequest_stats = pandas.read_csv(
            path+"/prerequests.csv")
        self.data_frame_pd_matrix = pandas.read_csv(
            path+"/pd_matrix.csv")
        self.log_dir=get_logs_directory()
        # Try reading the existing global CSV file; if it doesn't exist, create an empty DataFrame
        try:
            self.df_global = pandas.read_csv(f'{self.log_dir}/global_status_codes.csv', index_col=0)
        except FileNotFoundError:
            self.df_global = pandas.DataFrame()
        ###CC6
        #self.data_frame_uri = pandas.read_csv(path+"/uri_dev_statuscode.csv")
        #self.data_frame_rel_uri = pandas.read_csv(path+"/rel_uri_dev_statuscode.csv")   
        #self.data_frame_rel_uri_2xx = pandas.read_csv(path+"/rel_uri_host_2xx.csv")      
        self.experiment_configuration, self.exp_meta_data=self.load_exp_outcome(self.exp_path)
        self.dra_logging=logging.getLogger("main.runner.dra_logger")
        self.font_size_axis=10
        self.font_size_title=12
        self.font_size_label=8
        self.slope=0
        self.host100=0
      #  self.data_frame_target_list = pandas.read_csv(path+"/base_request/target_list.csv")

        return

    def load_exp_outcome(self, path):
        json_file_path = path+'/experiment_outcome.json'

        # Load the JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        # Extract the dictionaries from the JSON data
        captured_packages = data["captured_packages"]
        outcome = data["Outcome"]
        experiment_configuration = data["Experiment_Configuration"]
        experiment_duration_seconds = data["Experiment_Duration(s)"]
        packets_per_second = data["Packets_per_second"]
        messages = data["Messages"]
        messages_per_second = data["Messages_per_second"]
        active_workers = data["Active_Workers"]
        folder_size_mb = data["Folder_Size im MB"]
        invalid_target_entries = data["Invalid Target Entries"]
        return experiment_configuration, data
    
    def get_logs_directory(self):
        """Get or create local log directory"""
        script_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.dirname(script_directory)

        # Check if directory for experiment_logs exist
        logs_directory = os.path.join(parent_directory, "logs")
    
        return logs_directory

    def start(self):

        cc=1
        eval_folder= f"{self.exp_path}/evaluation"
        os.makedirs(eval_folder, exist_ok=True)
        self.exp_path=eval_folder
        ###Work for all experiments
        
        host_statistics=self.host_stats(self.data_frame_exp_stats)
        prerequest_statistics=self.prerequest_stats(self.data_frame_prerequest_stats)  
        self.save_exp_analyzer_results(host_statistics, prerequest_statistics)
        self.analyze_status_codes(self.data_frame_pd_matrix.copy())
        statuscodes_dict=self.count_status_codes(self.data_frame_pd_matrix.copy())  
        latex_code = self.generate_latex_table(self.experiment_configuration, self.exp_meta_data, prerequest_statistics, host_statistics, statuscodes_dict)
        report_filename = f'{self.exp_path}/experiment_report.tex'  
        self.export_latex_to_report(latex_code, report_filename)  
        
        print(statuscodes_dict)
        relativ_statuscodes_dict=self.convert_to_relative_values(statuscodes_dict.copy())
        print(relativ_statuscodes_dict)
        #Distribution of modifications
        self.single_plot_deviation_count_distribution(1) 
        #Response rates over modifications
        ##CC1
        self.singleplot_mod(cc)
        ###CC Specific Plots
        ##CC3
        #self.singleplot_mod(3)
        #self.double_plot_deviation_count_distribution_CC3()
        ##CC34
        #self.singleplot_mod(34)
        #CC4
        #self.singleplot_mod(4)
        #CC7
        #self.singleplot_mod(7)

        #CCr  
        #
        #self.singleplot_mod()
        #s
        ##
        #self.singleplot_blocking()##CC3
        #self.singleplot_mod()##CC3s
        ##target_list_dict=self.analyze_target_list(self.data_frame_target_list, self.data_frame_exp_stats)
        
        
        

       ## self.doubleplot_response_rate_message_index()
        ##CC4
       # #self.doubleplot_modification()
        
        ##_, decoded_df=self.decode_save_cc52(self.data_frame_prerequest_stats)
        ##self.count_and_plot_bit_occurrences52(decoded_df.copy())
        
        ##_, decoded_df=self.decode_save_cc53(self.data_frame_prerequest_stats)
        ##self.count_and_plot_bit_occurrences53(decoded_df)

        _, decoded_df=self.decode_save_cc33(self.data_frame_prerequest_stats)
        self.count_and_plot_bit_occurrences33(decoded_df)
        ##_, decoded_df=self.decode_save_cc71(self.data_frame_prerequest_stats)
        ##self.count_and_plot_bit_occurrences71(decoded_df)
        ##CC91
        ##self.check_91_key_value_length(self.data_frame_prerequest_stats.copy())
        ##self.grouped_results_csv(self.data_frame_pd_matrix,self.data_frame_prerequest_stats)
        ##self.status_code_curves_over_deviation(self.data_frame_prerequest_stats.copy(), ax=None)
        ##self.status_code_bars_over_deviation(self.data_frame_prerequest_stats, ax=None)
        #self.plot_unsorted_data(self.data_frame_exp_stats)
        ##self.filter_and_aggregate(self.data_frame_pd_matrix.copy(), 429, decoded_df.copy())

        
      
        ##self.plot_scatter_prerequest(self.data_frame_rel_uri)
        #self.plot_hosts_responses(self.data_frame_exp_stats)
        ##self.figure1(self.data_frame_pd_matrix)
        ##self.quadplot()
     
        ##self.update_status_code_csv(statuscodes_dict, self.df_global)
        ###CC6
        ####self.singleplot_rel_uri() #ACHTUNG
        ####self.plot_uri_deviation_count_distribution(self.data_frame_uri)
        ####Delte self.plot_rel_uri_deviation_distribution(self.data_frame_rel_uri)
        ##self.single_plot_mod_cc6()
        ##self.analyze_modifications_cc6()
        ##self.grouped_cc6(self.data_frame_rel_uri_2xx.copy())
        

        return
    

    def analyze_status_codes(self, df):
       
        ten_percent_index = int(len(df) * 0.1)
        if ten_percent_index == 0:
            ten_percent_index = 1  # Ensure at least one row is included
     
        # Initialize a list to hold the results
        results_list = []

        # Analyze each domain (column) except for the 'Attempt No.'
        for column in df.columns[1:]:
            # Get the counts of all status codes for the current host
            status_counts = df[column].astype(int).value_counts().to_dict()  # Ensure status codes are integers

            # Calculate the share and absolute number of 200 codes in the first 10%
            first_10_data = df[column].iloc[:ten_percent_index].astype(int)  # Convert to int for comparison
            first_10_share = (first_10_data == 200).mean()
            first_10_absolute = (first_10_data == 200).sum()

            # Calculate the share and absolute number of 200 codes in the last 10%
            last_10_data = df[column].iloc[-ten_percent_index:].astype(int)  # Convert to int for comparison
            last_10_share = (last_10_data == 200).mean()
            last_10_absolute = (last_10_data == 200).sum()

            # Calculate the difference in shares and absolute numbers
            difference_share = last_10_share - first_10_share
            difference_absolute = last_10_absolute - first_10_absolute

            # Prepare the results dictionary for the current host
            results_dict = {
                'Host': column,
                'First_10_Percent_Share': first_10_share,
                'First_10_Percent_Absolute': first_10_absolute,
                'Last_10_Percent_Share': last_10_share,
                'Last_10_Percent_Absolute': last_10_absolute,
                'Difference_Share': difference_share,
                'Difference_Absolute': difference_absolute,
                'Total_Non_200_Count': sum(status_counts.values()),
            }
            # Add the counts for each non-200 status code to the results dictionary
            for status_code, count in status_counts.items():
                results_dict[f'{status_code}'] = count

            # Append the results dictionary to the results list
            results_list.append(results_dict)
        
        

        # Convert the list of dictionaries to a DataFrame
        results_df = pandas.DataFrame(results_list)

        # Extracting status code columns and sorting them numerically
        status_code_columns = [col for col in results_df if col.isdigit()]  # Assuming status codes are direct column names
        sorted_status_code_columns = sorted(status_code_columns, key=lambda x: int(x))

        # Reordering DataFrame columns: Host and other metrics first, then sorted status codes
        other_columns = [col for col in results_df.columns if col not in status_code_columns]
        ordered_columns = other_columns + sorted_status_code_columns
        results_df = results_df[ordered_columns]


        # Sort the DataFrame by 'Difference_Absolute', then by 'Total_Non_200_Count', both ascending
        sorted_results_df = results_df.sort_values(by=['Difference_Absolute', 'Total_Non_200_Count'], ascending=[True, True])

        # Save the sorted DataFrame to a new CSV file
        sorted_results_df.to_csv(f'{self.exp_path}/status_codes_analysis.csv', index=False)



        return #num_hosts_100_percent_200, status_code_summary

     

    def grouped_cc6(self, data_frame):
        
       
        bins = [0, 20, 40, 60, 80, 101]
        # Create a dictionary to store the averages for each host
        host_averages = {}

        # Exclude the first column (hosts)
        columns_to_consider = data_frame.columns[1:]

        # Iterate through each row
        for index, row in data_frame.iterrows():
            host = row[0]  # Assuming the first column is the host
            # Initialize Sum and Number for each bin range for the current row
            row_averages = {f'{bins[i]}-{bins[i+1]}_average': {'Sum': 0, 'Number': 0} for i in range(len(bins) - 1)}

            # Iterate through each column and classify them into bins
            for col in columns_to_consider:
                value = row[col]
                if value > 0:
                    # Determine the bin for the current column
                    for i in range(len(bins) - 1):
                        if bins[i] <= int(col) < bins[i + 1]:
                            bin_key = f'{bins[i]}-{bins[i+1]}_average'
                            row_averages[bin_key]['Sum'] += value
                            row_averages[bin_key]['Number'] += 1
                            break

            # Calculate and store averages for each bin for the current row
            host_averages[host] = {bin_key: (row_averages[bin_key]['Sum'] / row_averages[bin_key]['Number']) if row_averages[bin_key]['Number'] > 0 else 0 for bin_key in row_averages}

        # Create a new DataFrame from the host_averages dictionary
        
        file_path = f'{self.exp_path}/grouped6.csv'
        average_df = pandas.DataFrame.from_dict(host_averages, orient='index')
        average_df.to_csv(file_path)
       
    
        percentage_ranges = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]
        range_counts = {f"{lower}-{upper}%": {column: ((average_df[column] >= lower) & (average_df[column] <= upper)).sum()
                                            for column in average_df.columns[:]}  # Exclude the first column
                        for lower, upper in percentage_ranges}

        bins_df=pandas.DataFrame(range_counts).T


        file_path = f'{self.exp_path}/grouped6_10percent_bins.csv'
        bins_df.to_csv(file_path)     
        bins_df.to_latex(self.exp_path+"/grouped6_10percent_bins.tex", index=True)
        
        
        return data_frame


    def convert_to_relative_values(self, data_dict):
        # Calculate the total count
        total = sum(data_dict.values())

        # Convert each value to a relative value (percentage)
        relative_values = {key: (value / total) * 100 for key, value in data_dict.items()}

        return relative_values

   

    def update_status_code_csv(self, status_code_dict, df_global):
        """
        Updates the global status code CSV file with data from the current experiment.
        Returns a DataFrame or dictionary with relative differences for each status code.
        """
        
        # Convert status_code_dict to DataFrame
        df_current_experiment = pandas.DataFrame.from_dict(status_code_dict, orient='index', columns=[self.exp_path])

        # Drop the column if it already exists
        if self.exp_path in df_global.columns:
            df_global.drop(columns=[self.exp_path], inplace=True)

        # Merge and fill missing values
        if not df_global.empty:
            df_global = pandas.merge(df_global, df_current_experiment, left_index=True, right_index=True, how='outer')
        else:
            df_global = df_current_experiment
        df_global.fillna(0, inplace=True)

        # Save the updated DataFrame back to the CSV file
        df_global.to_csv(file_path)

        # Calculate relative values for the current experiment and the second column
        total_current = df_current_experiment[self.exp_path].sum()
        relative_current = df_current_experiment[self.exp_path] / total_current

        second_column = df_global.columns[0]
        total_global = df_global[second_column].sum()
        relative_global = df_global[second_column] / total_global

        # Calculate relative differences
        relative_differences = (relative_current - relative_global) / relative_global
        relative_differences = relative_differences.replace([float('inf'), -float('inf')], 0)
        relative_differences = relative_differences.fillna(0)
        relative_differences = relative_differences.apply(lambda x: f"{x:.2%}")
        print(relative_differences)
        # Return relative differences as a DataFrame or dict
        return relative_differences.to_dict()




    




    def analyze_target_list(self,df_target_list, df_exp_stats):
        def extract_host_from_string(s):
            try:
                # Split the string by single quotes and get the fourth element
                return s.split("'")[3]  # Index 3 corresponds to the value between the third and fourth single quotes
            except IndexError:
                # Handle cases where the string format is not as expected
                return None

        def calculate_mean_host_length(df, column_name):
            # Extract the host lengths
            host_lengths = []
            for row in df[column_name]:
                host = extract_host_from_string(row)
                if host:
                    host_lengths.append(len(host))

            # Calculate the mean of the host lengths
            if host_lengths:
                mean_host_length = sum(host_lengths) / len(host_lengths)
                print(f"Mean Host Length: {mean_host_length}")
            else:
                print("No host values found.") 
                mean_host_length = None
            return float(mean_host_length)

        def is_path_longer_than_slash(uri):
            scheme, subdomain, hostname, domain, port, path = HTTP1_Request_Builder().parse_host(uri)
            if len(path)>1:
                print("Pfad: "+ path +" Länge: "+str(len(path)))
                return True
            else: return False     

        def calculate_uri_length_stats(df, uri_column):
            uri_lengths = df[uri_column].apply(lambda uri: len(str(uri)))
            longest = uri_lengths.max()
            shortest = uri_lengths.min()
            average = uri_lengths.mean()
            longest_uri = df[uri_lengths == longest][uri_column].iloc[0]
            shortest_uri = df[uri_lengths == shortest][uri_column].iloc[0]

            uri_length= {
                "Max_URI_Length": int(longest),
                "Longest_URI": longest_uri,
                "Min_URI_Length": int(shortest),
                "Shortest_URI": shortest_uri,
                "Average URI":  float(average),
            }
            print(f"Longest URI Length: {longest}")
            print(f"Shortest URI Length: {shortest}")
            print(f"Average URI Length: {average}")
            return uri_length

        mean_host_length=calculate_mean_host_length(df_target_list.copy(), "socket_dns_info")
        uri_stats=calculate_uri_length_stats(df_target_list.copy(), 'uri')
        df_exp_stats['2xx_rate'] = df_exp_stats['2xx'] / df_exp_stats['Messages Send']
        df_target_list['has_long_path'] = df_target_list['uri'].apply(is_path_longer_than_slash)
        merged_df = pandas.merge(df_target_list, df_exp_stats, left_on='tranco_domain', right_on='Host')
        correlation = merged_df['has_long_path'].corr(merged_df['2xx_rate'])
        print(f"Correlation between URI having a long path and 2xx response rate: {correlation}")
        average_2xx_rates = merged_df.groupby('has_long_path')['2xx_rate'].mean()
        print("Average Rate: ", average_2xx_rates)
        average_uri_length = df_target_list['uri'].apply(lambda uri: len(uri)).mean()
        print(f"Average URI Length: {average_uri_length}")
        target_list_stats={
            "Mean_Host_Length":mean_host_length,
            "Uri_Stats": uri_stats,
        }
        with open(self.exp_path + f"/base_request/target_list_stats.json", "w", encoding="utf-8") as file:
            json.dump(target_list_stats, file, indent=4)
        return  target_list_stats


    def filter_and_aggregate(self,pd_matrix, target_status_code, decoded_df):
        #Filter the DataFrame to only include rows with the target_status_code
        
      
        
        filtered_df = pd_matrix[pd_matrix.iloc[:, 1:].eq(target_status_code).any(axis=1)]


        columns_mask = filtered_df.iloc[:, 1:].eq(target_status_code).any(axis=0)
        # Select the columns based on the mask and always include the first column
        filtered_df = filtered_df.loc[:, ['Attempt No.\Domain'] + columns_mask[columns_mask].index.tolist()]
        #52
        bit_columns = decoded_df.loc[:, ['no'] + decoded_df.columns[-11:].tolist()]


        # Join the filtered DataFrame with the last 11 columns of the decoded DataFrame
        # Ensure that the joining columns are correctly named and aligned
        merged_df = pandas.merge(filtered_df, bit_columns, left_on='Attempt No.\Domain', right_on='no', how='left')


        
        merged_df.to_csv(self.exp_path + f"/pd_{target_status_code}.csv", index=False)

        #Group the filtered DataFrame by domain and count the occurrences of the target_status_code
        status_code_counts = filtered_df.iloc[:, 1:].eq(target_status_code).sum()

        #Create a dictionary to store message indexes when the code was received
        message_indexes = {}
        for domain in filtered_df.columns[1:]:
            messages = filtered_df[filtered_df[domain] == target_status_code]['Attempt No.\Domain'].tolist()
            if messages:  # Check if the list is not empty
                message_indexes[domain] = messages

        #Convert the aggregated counts to a DataFrame
        counts_df = status_code_counts.reset_index()
        counts_df.columns = ['Domain', 'Count']
        
        counts_df = counts_df[counts_df['Count'] > 0]
        
        #Save Results
        with open(self.exp_path + f"/message_indexes_{target_status_code}.json", "w", encoding="utf-8") as file:
            json.dump(message_indexes, file, indent=4)
        counts_df.to_csv(self.exp_path+f"/counts_{target_status_code}.csv")

        return counts_df, message_indexes




    def create_stacked_bar_chart(self,data_frame):
        # Filter the DataFrame where Bit 0 is equal to 1
        filtered_data = data_frame[data_frame['Bit 0: Exclude Scheme'] == 1]

        # Sum the response categories for the filtered data
        stacked_data = filtered_data[['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']].sum()

        # Define colors for the response categories
        colors = ['#9B59BB', '#2ECC77', '#F1C400', '#E74C33', '#3498DD', '#344955']

        # Create a single stacked bar chart
        stacked_data.plot(kind='bar', stacked=True, color=colors, figsize=(10, 6))

        mpl.xlabel('Response Categories')
        mpl.ylabel('Total Values')
        mpl.title('Stacked Bar Chart for Bit 0 = 1')
        mpl.legend(['Bit 0: Include Scheme'])

        #mpl.show()

    def decode_save_cc71(self,data_frame):
        
        #CC71 Columns
        bit_columns=  [
            'Digit+Letters',
            'Lowercase Letters',
            'Uppercase Letters',
            'Digits',
            'Sub-Delimiters',
            'Reserverd Characters',
            'Encoded res. Characters',
            'Additional Characters',
        ]

        def decode_bits(deviation_count, num_bits):
            # Create a list of bit values by decoding the deviation_count.
            bit_values = [(deviation_count >> bit_index) & 1 for bit_index in range(num_bits)]
            return bit_values    

       

        # Decode each row in the original DataFrame and add the bit columns.
        for bit_index, bit_column in enumerate(bit_columns):
            data_frame[bit_column] = data_frame['deviation_count'].apply(lambda x: (x >> bit_index) & 1)

        data_frame.to_csv(self.exp_path + "/prerequest_decoded.csv", index=False)
        
        # Create an empty DataFrame to store the result
        result_df = pandas.DataFrame(columns=['Bit Name', 'Mean 1xx', 'Mean 2xx', 'Mean 3xx', 'Mean 4xx', 'Mean 5xx', 'Mean 9xx'])

        result_dfs = []

        # Iterate through each bit, calculate the mean values, and add them to the list of DataFrames
        for bit_column in bit_columns:
            filtered_data = data_frame[data_frame[bit_column] == 1]
            mean_values = filtered_data[['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']].mean()
            bit_df = pandas.DataFrame({'Bit Name': [bit_column], **mean_values.to_dict()})
            result_dfs.append(bit_df)

        # Concatenate the list of DataFrames into a single result DataFrame
        result_df = pandas.concat(result_dfs, ignore_index=True)
        #Percentage
        result_df.iloc[:, 1:] = result_df.iloc[:, 1:].apply(lambda x: (x / x.sum()) * 100, axis=1)
        
            # Save the DataFrame to a CSV file.
        result_df.iloc[:, 1:] = result_df.iloc[:, 1:].round(1)
        result_df.to_csv(self.exp_path + "/deviations_mean.csv", index=False)
        transpose_df=result_df
        transpose_df.iloc[:, 1:] = transpose_df.iloc[:, 1:].round(2)
        transpose_df.to_latex(self.exp_path+"/deviation_means_t.tex", index=False)
        colors = ['#9B59BB', '#2ECC77', '#F1C400', '#E74C33', '#3498DD', '#344955']
        fig, ax = mpl.subplots(figsize=(10, 10))

        bottom = 0

        for i, col in enumerate(result_df.columns[1:]):
            ax.bar(result_df['Bit Name'], result_df[col], label=col, bottom=bottom, color=colors[i])
            bottom += result_df[col]

        ax.tick_params(axis='both', labelsize=self.font_size_axis)
        ax.set_ylabel('Response Status Codes Share (%)', fontsize=self.font_size_axis)
        ax.set_title('Response Codes over different Modifications',fontsize=self.font_size_title)
        ax.legend(loc='lower right')
        mpl.xticks(rotation=90)
        mpl.tight_layout()
        mpl.savefig(self.exp_path+'/discrete_deviation_response_rates.png', dpi=300)
        
        return result_df, data_frame
        
        



    def count_and_plot_bit_occurrences71(self, data_frame):
        def count_bit_occurrences(df, bit_columns):     
            bit_occurrences = {}
            for bit_column in bit_columns:
                bit_count = df[bit_column].sum()
                bit_occurrences[bit_column] = bit_count
            return bit_occurrences

        bit_columns = [
            'Digit+Letters',
            'Lowercase Letters',
            'Uppercase Letters',
            'Digits',
            'Sub-Delimiters',
            'Reserverd Characters',
            'Encoded res. Characters',
            'Additional Characters',
        ]

        bit_occurrences = count_bit_occurrences(data_frame, bit_columns)

        # Plotting
        fig, ax = mpl.subplots(figsize=(10, 6))
        bits = list(bit_occurrences.keys())
        occurrences = list(bit_occurrences.values())

        ax.bar(bits, occurrences, color='#3498DD')
        ax.set_xlabel('Bit Columns')
        ax.set_ylabel('Occurrences')
        ax.set_title('Occurrences of Each Bit Column')
        mpl.xticks(rotation=45, ha='right')
        mpl.tight_layout()
        mpl.savefig(self.exp_path+'/discrete_modification_occurence71.png', dpi=300)
        
        return


    def decode_save_cc33(self,data_frame):
        
        #CC3 Columns
        bit_columns= [ 
            'Spaces and tabs variant 1',
            'Spaces and tabs variant 2',
            'Spaces and tabs variant 3',
            'Spaces and tabs variant 4',
            'Spaces and tabs variant 5',
            'Spaces and tabs variant 6',
            'Host and space',
            'Host and tab',
            'Newline',
            'Host, space and newline',
            'Host, tab and newline',
            'Add. separating space',
        ]

        def decode_bits(deviation_count, num_bits):
            # Create a list of bit values by decoding the deviation_count.
            bit_values = [(deviation_count >> bit_index) & 1 for bit_index in range(num_bits)]
            return bit_values    

       

        # Decode each row in the original DataFrame and add the bit columns.
        for bit_index, bit_column in enumerate(bit_columns):
            data_frame[bit_column] = data_frame['deviation_count'].apply(lambda x: (x >> bit_index) & 1)

        data_frame.to_csv(self.exp_path + "/prerequest_decoded.csv", index=False)
        
        # Create an empty DataFrame to store the result
        result_df = pandas.DataFrame(columns=['Bit Name', 'Mean 1xx', 'Mean 2xx', 'Mean 3xx', 'Mean 4xx', 'Mean 5xx', 'Mean 9xx'])

        result_dfs = []

        # Iterate through each bit, calculate the mean values, and add them to the list of DataFrames
        for bit_column in bit_columns:
            filtered_data = data_frame[data_frame[bit_column] == 1]
            mean_values = filtered_data[['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']].mean()
            bit_df = pandas.DataFrame({'Bit Name': [bit_column], **mean_values.to_dict()})
            result_dfs.append(bit_df)

        # Concatenate the list of DataFrames into a single result DataFrame
        result_df = pandas.concat(result_dfs, ignore_index=True)
        #Percentage
        result_df.iloc[:, 1:] = result_df.iloc[:, 1:].apply(lambda x: (x / x.sum()) * 100, axis=1)
        
            # Save the DataFrame to a CSV file.
        result_df.iloc[:, 1:] = result_df.iloc[:, 1:].round(1)
        result_df.to_csv(self.exp_path + "/deviations_mean.csv", index=False)
        transpose_df=result_df
        transpose_df.iloc[:, 1:] = transpose_df.iloc[:, 1:].round(2)
        transpose_df.to_latex(self.exp_path+"/deviation_means_t.tex", index=False)
        colors = ['#9B59BB', '#2ECC77', '#F1C400', '#E74C33', '#3498DD', '#344955']
        fig, ax = mpl.subplots(figsize=(10, 10))

        bottom = 0

        for i, col in enumerate(result_df.columns[1:]):
            ax.bar(result_df['Bit Name'], result_df[col], label=col, bottom=bottom, color=colors[i])
            bottom += result_df[col]

        ax.tick_params(axis='both', labelsize=self.font_size_axis)
        ax.set_ylabel('Response Status Codes Share (%)', fontsize=self.font_size_axis)
        ax.set_title('Response Codes over different Modifications',fontsize=self.font_size_title)
        ax.legend(loc='lower right')
        mpl.xticks(rotation=90)
        mpl.tight_layout()
        mpl.savefig(self.exp_path+'/discrete_deviation_response_rates.png', dpi=300)
        
        return result_df, data_frame
        
        



    def count_and_plot_bit_occurrences33(self, data_frame):
        def count_bit_occurrences(df, bit_columns):     
            bit_occurrences = {}
            for bit_column in bit_columns:
                bit_count = df[bit_column].sum()
                bit_occurrences[bit_column] = bit_count
            return bit_occurrences

        bit_columns = [
            'Spaces and tabs variant 1',
            'Spaces and tabs variant 2',
            'Spaces and tabs variant 3',
            'Spaces and tabs variant 4',
            'Spaces and tabs variant 5',
            'Spaces and tabs variant 6',
            'Host and space',
            'Host and tab',
            'Newline',
            'Host, space and newline',
            'Host, tab and newline',
            'Add. separating space',
        ]

        bit_occurrences = count_bit_occurrences(data_frame, bit_columns)

        # Plotting
        fig, ax = mpl.subplots(figsize=(10, 6))
        bits = list(bit_occurrences.keys())
        occurrences = list(bit_occurrences.values())

        ax.bar(bits, occurrences, color='#3498DD')
        ax.set_xlabel('Bit Columns')
        ax.set_ylabel('Occurrences')
        ax.set_title('Occurrences of Each Bit Column')
        mpl.xticks(rotation=45, ha='right')
        mpl.tight_layout()
        mpl.savefig(self.exp_path+'/discrete_modification_occurence.png', dpi=300)
        
        return


    def count_and_plot_bit_occurrences52(self, data_frame):
        def count_bit_occurrences(df, bit_columns):     
            bit_occurrences = {}
            for bit_column in bit_columns:
                bit_count = df[bit_column].sum()
                bit_occurrences[bit_column] = bit_count
            return bit_occurrences

        bit_columns = [
            'Exclude Scheme',
            'Switch Scheme',
            'Exclude subdomain',
            'Include fitting port',
            'Counter Scheme fitting Port',
            'Random Port in Port Range 65535',
            'Random Integer as Port',
            'Random String L=5 as Port',
            'Random String L=6-100 as Port',
            'Delete path if path is provided',
            'No changes',]

        bit_occurrences = count_bit_occurrences(data_frame, bit_columns)

        # Plotting
        fig, ax = mpl.subplots(figsize=(10, 6))
        bits = list(bit_occurrences.keys())
        occurrences = list(bit_occurrences.values())

        ax.bar(bits, occurrences, width=0.2, color='b')#, color='#3498DD')
        #ax.set_xlabel('Bit Columns')
        ax.set_ylabel('Requests', fontsize=self.font_size_axis)
        ax.set_title('Distribution of Modifications among Requests', fontsize=self.font_size_title)
        mpl.xticks(rotation=45, ha='right')
        mpl.tight_layout()
        mpl.savefig(self.exp_path+'/discrete_modification_occurence.png', dpi=300)
        
        return

    def count_and_plot_bit_occurrences53(self, data_frame):
        def count_bit_occurrences(df, bit_columns):     
            bit_occurrences = {}
            for bit_column in bit_columns:
                bit_count = df[bit_column].sum()
                bit_occurrences[bit_column] = bit_count
            return bit_occurrences

        bit_columns = [
            'pos 16Bit signed Int.',
            'neg 16Bit signed Int.',
            'pos 32Bit signed Int.',
            'neg 32Bit signed Int.',
            'pos 64Bit signed Int.',
            'neg 64Bit signed Int.',
            'No changes',
        ]

        bit_occurrences = count_bit_occurrences(data_frame, bit_columns)

        # Plotting
        fig, ax = mpl.subplots(figsize=(10, 6))
        bits = list(bit_occurrences.keys())
        occurrences = list(bit_occurrences.values())

        ax.bar(bits, occurrences, width=0.2, color='b')#, color='#3498DD')
        #ax.set_xlabel('Bit Columns')
        ax.set_ylabel('Requests', fontsize=self.font_size_axis)
        ax.set_title('Distribution of Modifications among Requests', fontsize=self.font_size_title)
        mpl.xticks(rotation=45, ha='right')
        mpl.tight_layout()
        mpl.savefig(self.exp_path+'/discrete_modification_occurence.png', dpi=300)
        
        return
    

    def decode_save_cc53(self,data_frame):
      
        #CC53Columns
        bit_columns = [
            'pos 16Bit signed Int.',
            'neg 16Bit signed Int.',
            'pos 32Bit signed Int.',
            'neg 32Bit signed Int.',
            'pos 64Bit signed Int.',
            'neg 64Bit signed Int.',
            'No changes',
            ]

        def decode_bits(deviation_count, num_bits):
            # Create a list of bit values by decoding the deviation_count.
            bit_values = [(deviation_count >> bit_index) & 1 for bit_index in range(num_bits)]
            return bit_values    

       

        # Decode each row in the original DataFrame and add the bit columns.
        for bit_index, bit_column in enumerate(bit_columns):
            data_frame[bit_column] = data_frame['deviation_count'].apply(lambda x: (x >> bit_index) & 1)

        data_frame.to_csv(self.exp_path + "/prerequest_decoded.csv", index=False)
        
        # Create an empty DataFrame to store the result
        result_df = pandas.DataFrame(columns=['Bit Name', 'Mean 1xx', 'Mean 2xx', 'Mean 3xx', 'Mean 4xx', 'Mean 5xx', 'Mean 9xx'])

        result_dfs = []

        # Iterate through each bit, calculate the mean values, and add them to the list of DataFrames
        for bit_column in bit_columns:
            filtered_data = data_frame[data_frame[bit_column] == 1]
            mean_values = filtered_data[['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']].mean()
            bit_df = pandas.DataFrame({'Bit Name': [bit_column], **mean_values.to_dict()})
            result_dfs.append(bit_df)

        # Concatenate the list of DataFrames into a single result DataFrame
        result_df = pandas.concat(result_dfs, ignore_index=True)
        #Percentage
        result_df.iloc[:, 1:] = result_df.iloc[:, 1:].apply(lambda x: (x / x.sum()) * 100, axis=1)
        
            # Save the DataFrame to a CSV file.
        result_df.iloc[:, 1:] = result_df.iloc[:, 1:].round(1)
        result_df.to_csv(self.exp_path + "/deviations_mean.csv", index=False)
        transpose_df=result_df
        transpose_df.iloc[:, 1:] = transpose_df.iloc[:, 1:].round(2)
        transpose_df.to_latex(self.exp_path+"/deviation_means_t.tex", index=False)
        colors = ['#9B59BB', '#2ECC77', '#F1C400', '#E74C33', '#3498DD', '#344955']
        fig, ax = mpl.subplots(figsize=(10, 10))

        bottom = 0

        for i, col in enumerate(result_df.columns[1:]):
            ax.bar(result_df['Bit Name'], result_df[col], label=col, bottom=bottom, color=colors[i])
            bottom += result_df[col]

        #ax.set_xlabel('Bit Name')
        ax.tick_params(axis='both', labelsize=self.font_size_axis)
        
        ax.set_ylabel('Response Status Codes Share (%)', fontsize=self.font_size_axis)
        ax.set_title('Response Codes over different Modifications',fontsize=self.font_size_title)
        ax.legend(title='2xx Rates', loc='lower right')
        mpl.xticks(rotation=90)
        mpl.tight_layout()
        mpl.savefig(self.exp_path+'/discrete_deviation_response_rates.png', dpi=300)
        return result_df, data_frame


    def decode_save_cc52(self,data_frame):
      
        #CC52Columns
        bit_columns= [ 
            'Exclude Scheme',
            'Switch Scheme',
            'Exclude subdomain',
            'Include fitting port',
            'Counter Scheme fitting Port',
            'Random Port in Port Range 65535',
            'Random Integer as Port',
            'Random String L=5 as Port',
            'Random String L=6-100 as Port',
            'Delete path if path is provided',
            'No changes',
       
        ]

        def decode_bits(deviation_count, num_bits):
            # Create a list of bit values by decoding the deviation_count.
            bit_values = [(deviation_count >> bit_index) & 1 for bit_index in range(num_bits)]
            return bit_values    

       

        # Decode each row in the original DataFrame and add the bit columns.
        for bit_index, bit_column in enumerate(bit_columns):
            data_frame[bit_column] = data_frame['deviation_count'].apply(lambda x: (x >> bit_index) & 1)

        data_frame.to_csv(self.exp_path + "/prerequest_decoded.csv", index=False)
        
        # Create an empty DataFrame to store the result
        result_df = pandas.DataFrame(columns=['Bit Name', 'Mean 1xx', 'Mean 2xx', 'Mean 3xx', 'Mean 4xx', 'Mean 5xx', 'Mean 9xx'])

        result_dfs = []

        # Iterate through each bit, calculate the mean values, and add them to the list of DataFrames
        for bit_column in bit_columns:
            filtered_data = data_frame[data_frame[bit_column] == 1]
            mean_values = filtered_data[['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']].mean()
            bit_df = pandas.DataFrame({'Bit Name': [bit_column], **mean_values.to_dict()})
            result_dfs.append(bit_df)

        # Concatenate the list of DataFrames into a single result DataFrame
        result_df = pandas.concat(result_dfs, ignore_index=True)
        #Percentage
        result_df.iloc[:, 1:] = result_df.iloc[:, 1:].apply(lambda x: (x / x.sum()) * 100, axis=1)
        
            # Save the DataFrame to a CSV file.
        result_df.iloc[:, 1:] = result_df.iloc[:, 1:].round(1)
        result_df.to_csv(self.exp_path + "/deviations_mean.csv", index=False)
        transpose_df=result_df
        transpose_df.iloc[:, 1:] = transpose_df.iloc[:, 1:].round(2)
        transpose_df.to_latex(self.exp_path+"/deviation_means_t.tex", index=False)
        colors = ['#9B59BB', '#2ECC77', '#F1C400', '#E74C33', '#3498DD', '#344955']
        fig, ax = mpl.subplots(figsize=(10, 10))

        bottom = 0

        for i, col in enumerate(result_df.columns[1:]):
            ax.bar(result_df['Bit Name'], result_df[col], label=col, bottom=bottom, color=colors[i])
            bottom += result_df[col]

        #ax.set_xlabel('Bit Name')
        ax.tick_params(axis='both', labelsize=self.font_size_axis)
        
        ax.set_ylabel('Response Status Codes Share (%)', fontsize=self.font_size_axis)
        ax.set_title('Response Codes over different Modifications',fontsize=self.font_size_title)
        ax.legend(title='2xx Rates', loc='lower right')
        mpl.xticks(rotation=90)
        mpl.tight_layout()
        mpl.savefig(self.exp_path+'/discrete_deviation_response_rates.png', dpi=300)
        return result_df, data_frame

    
    def grouped_results_csv(self, pd_matrix, prerequests, attempt_no=1000):
        temp_matrix=pd_matrix.copy()
        #Status Code to leading digit
        def replace_with_xxx(value):
            if value >= 100 and value <= 999:
                leading_digit = str(value)[0]
                return leading_digit + "xx"
            else:
                return value
        #Status_Codes to Int
        for col in pd_matrix.columns:
            if col != "Attempt No.\Domain":
                temp_matrix[col] = temp_matrix[col].round(0).astype(int)
                temp_matrix[col] = temp_matrix[col].apply(replace_with_xxx)
        result = temp_matrix.merge(prerequests[['no', 'deviation_count']], left_on='Attempt No.\Domain', right_on='no')
        result = result.iloc[:, 1:]

        #Grouping of the deviation count
        # Define the bin edges and labels
        #CC1
        #bins = [-1,1]
        #labels = ['0']  
        #CC3 Exp19
        #bins = [-1, 20, 200, result['deviation_count'].max() + 1]
        #labels = ['0-20', '20-200', '200-2000']     
        #CC EOW2
        #CC4: 
        #bins = [-1, 5, 8, result['deviation_count'].max() + 1]
        #labels = ['2-5', '5-8', '8-12'] 
        #"""##CC52
        """bins = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512 ,1024]   ##
        labels = [
            'Exclude Scheme',
            'Switch Scheme',
            'Exclude subdomain',
            'Include fitting port',
            'Counter Scheme fitting Port',
            'Random Port in Port Range 65535',
            'Random Integer as Port',
            'Random String L=5 as Port',
            'Random String L=6-100 as Port',
            'Delete path if path is provided',
            'No changes',
        ]#"""
        ##CC53
        #"""bins = [0, 1, 2, 4, 8, 16, 32, 64]   ##
        """labels = [
            'pos 16Bit signed Int.',
            'neg 16Bit signed Int.',
            'pos 32Bit signed Int.',
            'neg 32Bit signed Int.',
            'pos 64Bit signed Int.',
            'neg 64Bit signed Int.',
            'No changes',
            ]"""
        #CC7
        #bins = [-1, 1025, 8201, 16401, 32801, result['deviation_count'].max() + 1]
        #labels = ['0-1024', '1025-8200', '8201-16400', '16401-32800', '32801-Max'] 
        #CC71
        #bins = [0, 1, 2, 4, 8, 16, 32, 64, 128+1]   ##
        """labels = [
            'Digit+Letters',
            'Lowercase Letters',
            'Uppercase Letters',
            'Digits',
            'Sub-Delimiters',
            'Reserverd Characters',
            'Encoded res. Characters',
            'Additional Characters',
        ]#"""
        #bins = [-1, 10, 50,100, result['deviation_count'].max() + 1]
        # labels = ['0-10', '11-50', '51-100', '101-Max']  
        #bins = [-1, 20, 40, 60, 80, 1001]
        #labels = ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%']  
        #CC61
        #bins = [0, 1, 11, 101, 1001, 10001]
        #labels = ['Scheme', 'Subdomain', 'Hostname', 'Toplevel Domain', 'Path']  
        ##CC8,CC9
        #bins = [-1, 1025, 8201, 16401, 32801, result['deviation_count'].max() + 1]
        #labels = ['0-1024', '1025-8200', '8201-16400', '16401-32800', '32801-Max'] 
        #CC91
        bins = [-1, 1025, 2049, 4097, 8183, result['deviation_count'].max() + 1]
        labels = ['0-1024', '1025-2048', '2049-4096', '4097-8192', '8193-Max'] 
        #result['deviation_group'] = pandas.cut(result['deviation_count'], bins=bins, labels=labels)
        result['deviation_group'] = pandas.cut(result['deviation_count'], bins=bins, labels=labels)
        result.to_csv(self.exp_path+"/temp1.csv")
        bin_dataframes = {}
        status_codes = ['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']
        length = len(result)
        requests_per_bin={}
        # Loop through each unique bin label
        for label in labels:
            # Extract the DataFrame for the current bin
            bin_dataframe = result[result['deviation_group'] == label]
            requests_per_bin[label] = round(len(bin_dataframe)/attempt_no*100,1)
            bin_dataframe = bin_dataframe.iloc[:, :-3]
            #result_df = pandas.DataFrame({'Status Codes': status_codes})
            host_percentages = {}
            #Calculate the share for each host
            for host in bin_dataframe.columns:
                status_percentages = {}
                total_count = len(bin_dataframe)
                #status_counts = {}
                for status_code in status_codes:
                    # Calculate the count for the current status code for the current host
                    count = bin_dataframe[host].str.contains(status_code).sum()
                    percentage = round((count / total_count) * 100,1)
                    status_percentages[status_code] = percentage
                host_percentages[host] = status_percentages

            bin_dataframes[label] = pandas.DataFrame(host_percentages)
            bin_dataframes[label].insert(0, "Status Codes", status_codes)
            #bin_dataframes[label] = bin_dataframes[label].set_index("Status Codes")
         
        bins_tp = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 101]
        labels_tp  = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
        result_df = pandas.DataFrame({'Percentage Bins': labels_tp})
        for label in labels:
            # Get the DataFrame for the current deviation count bin
            bin_dataframe = bin_dataframes[label]

            # Iterate through each percentage bin
            for i in range(len(bins_tp) - 1):
                lower_bound = bins_tp[i]
                upper_bound = bins_tp[i + 1]
                
                # Calculate the count of hosts within the current percentage bin for '2xx'
                count = ((bin_dataframe.loc['2xx'].iloc[1:] >= lower_bound) & (bin_dataframe.loc['2xx'].iloc[1:] < upper_bound)).sum()
                total_count = len(bin_dataframe)
                percentage = round(count/attempt_no*100,1)

                # Add the host count to the result DataFrame
                result_df.loc[i, label] = percentage
                #
                # result_df.loc[i, label + ' Percentage'] = percentage

        # Save the result as a CSV file
        new_row = pandas.DataFrame.from_dict(requests_per_bin, orient='index', columns=['Number of Requests'])
        # Transpose the DataFrame to make it a row
        new_row = new_row.transpose()
        result_df=pandas.concat([result_df,new_row], ignore_index=True)
        #Percent Value
        #result_df = result_df.div(length/100)
        result_df.to_csv(self.exp_path+"/hosts_count_in_10_percent_bins.csv", index=False)
        result_df.to_latex(self.exp_path+"/hosts_count_in_10_percent_bins.tex", index=False)
        latex_table = result_df.to_latex(index=False)
        with open(self.exp_path+"/table.tex", "w") as f:
            f.write(latex_table)
        result.to_csv(self.exp_path+"/grouped_host_analysis.csv")
        return result
    
    def count_status_codes(self,df):
        status_code_counts = {}

        # Iterate through the DataFrame to count the status codes
        for col in df.columns[1:]:
            for index, status_code in enumerate(df[col]):
                if status_code not in status_code_counts:
                    status_code_counts[status_code] = 1
                else:
                    status_code_counts[status_code] += 1

        return status_code_counts
    
    def format_status_codes(self, status_code_counts):
        # Create a table with 6 columns for each group
        
        status_code_counts = {k: status_code_counts[k] for k in sorted(status_code_counts, key=lambda x: int(x))}

        table = r"""
        \begin{tabular}{p{1.1cm} p{2.4cm} p{2.4cm} p{2.4cm} p{2.4cm} p{2.4cm}}
            \hline
            \textbf{1xx} & \textbf{2xx} & \textbf{3xx} & \textbf{4xx} & \textbf{5xx} & \textbf{9xx} \\
            \hline
        """

        # Initialize lists for each group
        groups = {
            '1xx': [],
            '2xx': [],
            '3xx': [],
            '4xx': [],
            '5xx': [],
            '9xx': [],
        }

        # Group the status codes based on the leading digit
        for code, count in status_code_counts.items():
            leading_digit = str(int(code))[0] 
            group_name = leading_digit + 'xx'
            if group_name in groups:
                groups[group_name].append(f"{int(code):03d} ({count})")

        max_group_length = max(len(group) for group in groups.values())

        # Populate the table
        for i in range(max_group_length):
            for group_name in ['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']:
                if i < len(groups[group_name]):
                    table += groups[group_name][i]
                table += ' & '

            table = table[:-2]  # Remove the last ' & ' for the current row
            table += r" \\"

        table += r"""
        \end{tabular}
        """

        return table




    def generate_latex_table(self, experiment_configuration, outcome_info, prerequest_statistics, host_statistics, status_codes):
        if experiment_configuration['relative_uri'] is True:
            uri_type="relative"
        else: 
            uri_type="absolut"

        if "EOW" in self.exp_path:
            covertsender="EOW/TVCable"
            imagepath=f"images/eow_exp_{experiment_configuration['experiment_no']}/"
        else:
            covertsender="ATTIC/FtH"
            imagepath=f"images/exp_{experiment_configuration['experiment_no']}/"
            
        seconds=outcome_info["Experiment_Duration(s)"]
        hours, remainder = divmod(seconds, 3600)  # 3600 seconds in an hour
        minutes, _ = divmod(remainder, 60)        # 60 seconds in a minute
        duration_str = f"{int(hours):2d}:{int(minutes):2d}h"
        
        
        latex_table = r"""
\begin{table}[htbp]
\caption{Experiment Outcome: CC"""+str(experiment_configuration["covertchannel_request_number"])+r""": TODT}
    \label{tab:outcomeCC"""+str(experiment_configuration["covertchannel_request_number"])+r"""}
    \begin{tabular}{p{8cm} p{7cm}}
        \hline
        \textbf{Experiment Parameters} & \textbf{Experiment Outcome} \\
        \hline
        \begin{tabular}{ll}
            Experiment No. & """ + str(experiment_configuration['experiment_no']) + r""" \\
            Timestamp & """ + str(experiment_configuration['timestamp']) + r""" \\
            Target Hosts & """ + str(experiment_configuration['max_targets']) + r""" \\
            Messages per Host & """ + str(experiment_configuration['num_attempts']) + r""" \\
            min. Fuzz & """ + str(experiment_configuration['min_fuzz_value']) + r""" \\
            Deviation Spread & """ + str(experiment_configuration['spread_deviation']) + r""" \\
            URI Type & """ + uri_type + r""" \\
            Basis request & """ + experiment_configuration['standard_headers'] + r""" \\
            Parallel worker & """ + str(experiment_configuration['max_workers']) + r""" \\
            Subset size & """ + str(experiment_configuration['target_subset_size']) + r""" \\
            Covert Sender & """ + covertsender+ r""" \\
        \end{tabular}
        &
                
        \begin{tabular}{ll}
            Duration & """ + duration_str + r""" \\
            Packets & """ + str(outcome_info["captured_packages"]) + r""" \\
            HTTP Messages/s & """ + str(round(outcome_info["Messages_per_second"],2)) + r""" \\
            Recorded Data(Mb) & """ + str(round(outcome_info['Folder_Size im MB'],0)) + r""" \\
            Response Codes & \% \\
            1xx: & """ + str(round(outcome_info["Outcome"]['1xx(%)'],2)) + r""" \\
            2xx: & """ + str(round(outcome_info["Outcome"]['2xx(%)'],2)) + r""" \\
            3xx: & """ + str(round(outcome_info["Outcome"]['3xx(%)'],2)) + r""" \\
            4xx: & """ + str(round(outcome_info["Outcome"]['4xx(%)'],2)) + r""" \\
            5xx: & """ + str(round(outcome_info["Outcome"]['5xx(%)'],2)) + r""" \\
            Socket Errors: & """ +str(round(outcome_info["Outcome"]['9xx(%)'],2)) + r""" \\
        \end{tabular} \\
        \hline
        \textbf{Request Analysis} & \textbf{Host Analysis}\ \\
        \hline
        \begin{tabular}{ll}
            Min. Deviation & """ + str(prerequest_statistics['min_deviation_count']) + r""" \\
            Max. Deviation & """ + str(prerequest_statistics['max_deviation_count']) + r""" \\
            Min. 2xx Response Rate & """ + str(prerequest_statistics['min_2xx']*100/experiment_configuration['num_attempts']) + r"""\% \\
            Max. 2xx Response Rate & """ + str(prerequest_statistics['max_2xx']*100/experiment_configuration['num_attempts']) + r"""\% \\
        \end{tabular} &
        \begin{tabular}{ll}
            Min. 2xx Response Rate & """ + str(round(host_statistics['min_2xx'],2)) + r"""\% \\
            Max. 2xx Response Rate & """ + str(round(host_statistics['max_2xx'],2)) + r"""\% \\
            Avg. 2xx Response Rate & """ + str(round(host_statistics['avg_2xx'],2)) + r"""\% \\
            Hosts with over 99\% 200 response &"""+ str(self.host100) +r"""\% \\
        \end{tabular} 
        \\
        \hline
        Avg. 2xx rate of first 10\% messages & """ + str(round(prerequest_statistics['average_2xx_first_10'],1)) + r"""\% \\
        Avg. 2xx rate of last 10\% messages & """ + str(round(prerequest_statistics['average_2xx_last_10'],1)) + r"""\% \\
        \textbf{Response Statuscodes:}\\
        
        \multicolumn{2}{c}{%
        \begin{minipage}{\dimexpr\linewidth-2\tabcolsep}""" + self.format_status_codes(status_codes)+ r"""
        \end{minipage}
        } \\
        \hline
\end{tabular}  
\end{table}


\begin{table}[H]
    \caption{Experiment CC"""""": Received Response Status Codes}
    \label{tab:cc"""+str(experiment_configuration["covertchannel_request_number"])+r"""statuscodes}
    \centering
         """+ self.format_status_codes(status_codes)+ r""" 
\end{table}


\begin{figure}[htbp]
\centering
\includegraphics[width=1\linewidth]{"""+imagepath+r"""combined_plots.png}
\caption{Experiment CC"""+ str(experiment_configuration["covertchannel_request_number"])+r""": Outcome}
\label{fig:cc"""+ str(experiment_configuration["covertchannel_request_number"])+r"""_combined}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=1\linewidth]{"""+imagepath+r"""exp_stats_host_statuscode_bars.png}
\caption{Experiment CC"""+ str(experiment_configuration["covertchannel_request_number"])+r""": Outcome}
\label{fig:cc"""+ str(experiment_configuration["covertchannel_request_number"])+r"""_bars}
\end{figure}
"""
        return latex_table


    def doubleplot_modification(self):
        """Create 2x1 Plot Matrix"""
        # Create a figure with subplots

        self.font_size_axis=16
        self.font_size_title=18
        self.font_size_label=8
        
        fig, axs = mpl.subplots(2, 1, figsize=(14, 7))
        #gs = GridSpec(2, 2, figure=fig)
        mpl.subplots_adjust(wspace=0.3, hspace=0.3)
        
        # Top
        self.status_code_curves_over_deviation(self.data_frame_prerequest_stats.copy(), ax=axs[0],subplottitles=False, autolimits=False, y_low=98, y_up=100 )
        axs[0].set_title('Statuscodes Frequency over Steganographic Payload', fontsize=14, fontweight='bold')
        axs[0].set_xlabel('')  # Remove x-axis label for the top plot
        
        # Bottom 
        self.status_code_curves_over_deviation(self.data_frame_prerequest_stats.copy(), ax=axs[1], subplottitles=False, autolimits=False, y_low=0, y_up=2, )
        axs[1].set_xlabel('Steganographic Payload / Modifications', fontsize=self.font_size_axis)  # Set x-axis label for the bottom plot
        axs[1].legend(loc='upper right')
        fig.text(0.04, 0.5, 'Response Code Frequency(%) per Request', va='center', rotation='vertical', fontsize=self.font_size_axis)
  

        # Adjust spacing between subplots
        #mpl.tight_layout()
        
        # Save the figure as a single PNG file
        mpl.savefig(self.exp_path+'/double_status_code_curves_over_deviation.png', dpi=300, bbox_inches='tight')
       

        # Show the combined plot
        #mpl.show()

        return



    def doubleplot_response_rate_message_index(self):
        """Create 2x1 Plot Matrix"""
        # Create a figure with subplots

        self.font_size_axis=16
        self.font_size_title=18
        self.font_size_label=8
        
        fig, axs = mpl.subplots(2, 1, figsize=(14, 7))
        #gs = GridSpec(2, 2, figure=fig)
        mpl.subplots_adjust(wspace=0.3, hspace=0.3)
        
        # Top
        self.plot_2xx_over_attempt_no_double(self.data_frame_prerequest_stats, ax=axs[0],subplottitles=False, autolimits=False, y_low=98, y_up=100 )
        axs[0].set_title(f'Development of Response Rates (blocking rate delta: {self.slope}%)', fontsize=self.font_size_title, fontweight='bold')
        axs[0].set_xlabel('')  # Remove x-axis label for the top plot
       
        # Bottom 
        self.plot_2xx_over_attempt_no_double(self.data_frame_prerequest_stats, ax=axs[1], subplottitles=False, autolimits=False, y_low=0, y_up=2, )
        axs[1].set_xlabel('Request Index', fontsize=self.font_size_axis)  # Set x-axis label for the bottom plot
        axs[1].legend(loc='upper right')
        fig.text(0.04, 0.5, 'Response Rate per Request (%)', va='center', rotation='vertical', fontsize=self.font_size_axis)
  

        # Adjust spacing between subplots
        #mpl.tight_layout()
        
        # Save the figure as a single PNG file
        mpl.savefig(self.exp_path+'/double_plot.png', dpi=300)

        # Show the combined plot
        #mpl.show()

        return
    

    def double_plot_deviation_count_distribution_CC3(self):
        """Create 2x1 Plot Matrix"""
        # Create a figure with subplots

        self.font_size_axis=16
        self.font_size_title=18
        self.font_size_label=8
        
        fig, axs = mpl.subplots(1, 2, figsize=(14, 7))
        #gs = GridSpec(2, 2, figure=fig)
        mpl.subplots_adjust(wspace=0.3, hspace=0.3)
        fig.suptitle("Histogram: Distribution of Steganographic Payload among Requests", fontsize=self.font_size_title, fontweight='bold')
        # Top
        self.plot_deviation_count_distribution(self.data_frame_prerequest_stats, ax=axs[0], bins=1000)
        axs[0].set_title("Overview", fontsize=self.font_size_title)
        axs[0].set_xlabel('Number of Modifications', fontsize=self.font_size_axis) # Remove x-axis label for the top plot
        axs[0].set_ylabel('Number of Requests', fontsize=self.font_size_axis)
        self.plot_deviation_count_distribution(self.data_frame_prerequest_stats, ax=axs[1], autolimits=False, x_low=0, x_up=200,  y_low=0, y_up=10,  bins=1000)
        axs[1].set_title("Detail on small Modification Numbers", fontsize=self.font_size_title)
        axs[1].set_xlabel('Number of Modifications', fontsize=self.font_size_axis)  # Set x-axis label for the bottom 
        axs[1].set_ylabel('Number of Requests',fontsize=self.font_size_axis) 
        # Adjust spacing between subplots
        #mpl.tight_layout()

        # Save the figure as a single PNG file
        mpl.savefig(self.exp_path+'/double_request_distribution_plot.png', dpi=300)

        # Show the combined plot
        #mpl.show()

        return

    def single_plot_deviation_count_distribution(self, nr=0):
        # Create a figure with subplots

        self.font_size_axis=16
        self.font_size_title=18
        self.font_size_label=8
        
        fig, axs = mpl.subplots(1,1, figsize=(14, 7))
         # Adjust spacing between subplots
        

        #mpl.subplots_adjust(wspace=0.3, hspace=0.3)
        axs.set_xlabel('Number of Modifications', fontsize=self.font_size_axis) 
        axs.set_ylabel('Number of Requests', fontsize=self.font_size_axis)
        if nr==4:
            self.plot_deviation_count_distribution(self.data_frame_prerequest_stats, ax=axs, bins=100 )
        elif nr==52:
            self.plot_deviation_count_distribution(self.data_frame_prerequest_stats, ax=axs, bins=1000 )
        elif nr==7:
            self.plot_deviation_count_distribution(self.data_frame_prerequest_stats, ax=axs, bins=100 )
        else:
            self.plot_deviation_count_distribution(self.data_frame_prerequest_stats, ax=axs, bins=100 )
        #fig.suptitle("Histogram: Distribution of Modifications among Requests", fontsize=self.font_size_title, fontweight='bold')
        mpl.tight_layout()
       
        # Save the figure as a single PNG file
        mpl.savefig(self.exp_path+'/single_request_distribution_plot.png', dpi=300)

        # Show the combined plot
        #mpl.show()

        return


        """def doubleplot(self):
        #Create 2x1 Plot Matrix
        # Create a figure with subplots

        self.font_size_axis=16
        self.font_size_title=18
        self.font_size_label=8
        
        fig, axs = mpl.subplots(2, 1, figsize=(14, 7))
        #gs = GridSpec(2, 2, figure=fig)
        mpl.subplots_adjust(wspace=0.3, hspace=0.3)
        
        # Top
        self.plot_2xx_over_attempt_no_double(self.data_frame_prerequest_stats, ax=axs[0],subplottitles=False, autolimits=False, y_low=98, y_up=100 )
        axs[0].set_title(f'Development of Response Rates (blocking rate delta: {self.slope}%)', fontsize=self.font_size_title, fontweight='bold')
        axs[0].set_xlabel('')  # Remove x-axis label for the top plot
        axs[0].legend(loc='upper right')
        # Bottom 
        self.plot_2xx_over_attempt_no_double(self.data_frame_prerequest_stats, ax=axs[1], subplottitles=False, autolimits=False, y_low=0, y_up=2, )
        axs[1].set_xlabel('Request Index', fontsize=self.font_size_axis)  # Set x-axis label for the bottom plot

        fig.text(0.04, 0.5, 'Response Rate per Request (%)', va='center', rotation='vertical', fontsize=self.font_size_axis)
  

        # Adjust spacing between subplots
        #mpl.tight_layout()
        
        # Save the figure as a single PNG file
        mpl.savefig(self.exp_path+'/double_plot.png', dpi=300)

        # Show the combined plot
        #mpl.show()

        return"""

    def singleplot_blocking(self):
        """Create 1x1 Plot Matrix"""
        # Create a figure with subplots

        self.font_size_axis=16
        self.font_size_title=18
        self.font_size_label=8
        
        fig, axs = mpl.subplots(1, 1, figsize=(14, 7))
        #gs = GridSpec(2, 2, figure=fig)
        mpl.subplots_adjust(wspace=0.3, hspace=0.3)
        
        # Top
        #CC3
        #self.plot_2xx_over_attempt_no_double(self.data_frame_prerequest_stats, ax=axs,subplottitles=False, autolimits=False, y_low=0, y_up=100, only_2xx=True )
        #mpl.axhline(y=32.5, color='b', linestyle='-')
        #mpl.text(x=-50, y=32.5, s=32.5, color='b', va='bottom', fontsize=12)
        #CC4
        #self.plot_2xx_over_attempt_no_double(self.data_frame_prerequest_stats, ax=axs,subplottitles=False, autolimits=False, y_low=95, y_up=100, only_2xx=True )
        ##CC52self.plot_2xx_over_attempt_no_double(self.data_frame_prerequest_stats, ax=axs,subplottitles=False, autolimits=False, y_low=0, y_up=100, only_2xx=True )
        #self.plot_2xx_over_attempt_no_double(self.data_frame_prerequest_stats, ax=axs,subplottitles=False, autolimits=True, y_low=0, y_up=100, only_2xx=True)
        #CC6
        #self.plot_2xx_over_attempt_no_double(self.data_frame_prerequest_stats, ax=axs,subplottitles=False, autolimits=False, y_low=0, y_up=100, only_2xx=False)
        #CC7
        self.plot_2xx_over_attempt_no_double(self.data_frame_prerequest_stats, ax=axs,subplottitles=False, autolimits=False, y_low=0, y_up=100, only_2xx=False, no_regression=False)
        
        axs.set_title(f'Development of Response Rate (blocking rate delta: {self.slope}%)', fontsize=self.font_size_title, fontweight='bold')
        axs.set_xlabel('Message Index', fontsize=self.font_size_axis)  # Remove x-axis label for the top plot
        axs.legend(loc='upper right')
        axs.set_ylabel('Response Rates (%) per Request ', fontsize=self.font_size_axis)
  

        # Adjust spacing between subplots
        #mpl.tight_layout()
        
        # Save the figure as a single PNG file
        mpl.savefig(self.exp_path+'/single_plot_block.png', dpi=300)

        # Show the combined plot
        #mpl.show()

        return


 
    def singleplot_rel_uri(self):
        """Create 1x1 Plot Matrix"""
        # Create a figure with subplots

        self.font_size_axis=16
        self.font_size_title=18
        self.font_size_label=8
        
        fig, axs = mpl.subplots(1, 1, figsize=(14, 7))
        #gs = GridSpec(2, 2, figure=fig)
        mpl.subplots_adjust(wspace=0.3, hspace=0.3)
        
        # Top
        #CC3 self.status_code_curves_over_deviation(self.data_frame_prerequest_stats, ax=axs,subplottitles=False, autolimits=False, y_low=15, y_up=85 )  CC3
        #self.status_code_curves_over_deviation(self.data_frame_prerequest_stats, ax=axs,subplottitles=False, autolimits=False, y_low=95, y_up=100)
        #CC4
        self.plot_rel_uri_deviation_distribution(self.data_frame_rel_uri, ax=axs)
        #subplottitles=False, autolimits=False, y_low=0, y_up=100)
        # Adjust spacing between subplots
        #mpl.tight_layout()
        axs.set_xlabel('Relative URI Modifications (%)', fontsize=self.font_size_axis)
        axs.set_ylabel('Requests', fontsize=self.font_size_axis)
        axs.set_title('Status Codes Frequency over Modifications', fontsize=self.font_size_title, fontweight='bold')
        # sSave the figure as a single PNG file
        mpl.savefig(self.exp_path+'/single_plot_rel_uri_mod.png', facecolor='white', edgecolor='white', dpi=300)

        # Show the combined plot
        #mpl.show()

        return

    def single_plot_mod_cc6(self):
        def status_code_curves_over_deviation6(data_frame, ax=None, subplottitles=True, autolimits=False, y_low=0, y_up=100):

            """
            MARCO1
            Plot percentage curves for different response codes over the deviation count.
            """
            
            if ax==None: 
                fig, ax = mpl.subplots(figsize=(10, 8))

            #mpl.style.use('fivethirtyeight')
            colors = ['#9B59BB','#2ECC77','#F1C400','#E74C33','#3498DD','#344955']

            response_codes = [ '2xx', '3xx', '4xx', '5xx', '9xx']  #'1xx' not present

            i=1
            for code in response_codes:
                data_frame[code + '_percentage'] = numpy.where(data_frame['Sum'] != 0, data_frame[code] / data_frame['Sum']*100, 0)
                #Curves
                ax.plot(data_frame['Relative Deviation'], data_frame[f'{code}_percentage'], label=code, color=colors[i])
                i+=1

            if subplottitles is True:
                ax.set_xlabel('Steganographic Payload / Modifications', fontsize=12)
                ax.set_ylabel('Response Code Frequency(%)', fontsize=12)
                ax.set_title('Statuscodes Frequency over Steganographic Payload', fontsize=14, fontweight='bold')

            if autolimits is False:
                ax.set_ylim(y_low, y_up)
                yticks = ax.get_yticks()
                ax.set_yticks(yticks)
                ax.set_yticklabels(['{:.2f}%'.format(ytick) for ytick in yticks])
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(data_frame['Relative Deviation'], data_frame['2xx_percentage'])
            regression_line = slope * data_frame['Relative Deviation'] + intercept
            ax.plot(data_frame['Relative Deviation'], regression_line, color='darkgreen', linestyle='dotted', label='2xx Regression Line')

            intercept_start = slope* data_frame['Relative Deviation'].min()+intercept
            intercept_start_str = f"{intercept_start:.1f}%"
            intercept_start=round(intercept_start)
            max_x=data_frame['Relative Deviation'].max()+1
            intercept_end=slope* max_x+intercept
            intercept_end_str = f"{intercept_end:.1f}%"
            intercept_end=round(intercept_end)
            ax.text(-int(0.05*max_x), intercept_start, intercept_start_str, fontsize=12, color='black')
            ax.text(int(0.995*max_x), intercept_end, intercept_end_str, fontsize=12, color='black')
            

            # Show the plot
            ax.grid(True)
            ax.legend(loc='best')
            #mpl.show()

            return ax

        self.font_size_axis=16
        self.font_size_title=18
        self.font_size_label=8
        
        fig, axs = mpl.subplots(1, 1, figsize=(14, 7))
        #gs = GridSpec(2, 2, figure=fig)
        mpl.subplots_adjust(wspace=0.3, hspace=0.3)
        
        # Top
        status_code_curves_over_deviation6(self.data_frame_rel_uri, ax=axs,subplottitles=False, autolimits=False, y_low=0, y_up=100)
        # Adjust spacing between subplots
        #mpl.tight_layout()
        axs.set_xlabel('Relative URI Modifications', fontsize=self.font_size_axis)
        axs.set_ylabel('Status Code Frequency(%)', fontsize=self.font_size_axis)
        axs.set_title('Status Codes Frequency over relativ URI Modifications', fontsize=self.font_size_title, fontweight='bold')
        # sSave the figure as a single PNG file
        mpl.savefig(self.exp_path+'/single_plot_mod6.png', dpi=300)

        # Show the combined plot
        #mpl.show()

        return
      
    def analyze_modifications_cc6(self):
        # Read data from CSV file
        data_frame = pandas.read_csv(self.exp_path + "/rel_mod_uri_host_2xx.csv")
        single_bit_columns = ['1', '10', '100', '1000', '10000']

        # Define the percentage ranges for bins
        percentage_ranges = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 80), (80, 90), (90, 101)]

        # Initialize a dictionary to store the count of entries in each percentage range
        range_counts = {f"{lower}-{upper}%": {column: 0 for column in single_bit_columns} for lower, upper in percentage_ranges}

        # Iterate through each row and count the occurrences in each percentage range
        for index, row in data_frame.iterrows():
            for col in single_bit_columns:
                value = row[col]
                for lower, upper in percentage_ranges:
                    if lower <= value < upper:
                        range_key = f"{lower}-{upper}%"
                        range_counts[range_key][col] += 1
                        break

        # Create a DataFrame from the range_counts dictionary
        bins_df = pandas.DataFrame(range_counts)

        # Save the DataFrame to CSV and LaTeX files
        file_path_csv = f'{self.exp_path}/grouped_mod6_10percent_bins.csv'
        file_path_tex = f'{self.exp_path}/grouped_mod6_10percent_bins.tex'
        
        bins_df.to_csv(file_path_csv)
        bins_df.to_latex(file_path_tex, index=True)
        
        return data_frame
        
        """# Select columns with only one bit set
        single_bit_columns = ['1', '10', '100', '1000', '10000']
        
        # Create custom bins: (0, 10), (10, 20), ..., (90, 100)
        bins = pandas.IntervalIndex.from_tuples([(0, 10), (10, 20), (20, 30), (30, 40), (40, 50),
                                            (50, 60), (60, 70), (70, 80), (80, 90), (90, 100)])
        
        # Initialize the DataFrame to store the grouped data
        grouped = pandas.DataFrame(index=[f"{interval.left}-{interval.right}%" for interval in bins],
                            columns=[f"Bit {str(bin).count('1')}" for bin in single_bit_columns])

        # Count hosts in each bin for each bit
        for col in single_bit_columns:
            # Group and count the data
            counts = pandas.cut(df[col], bins=bins, right=False).value_counts().sort_index()
            grouped[f"Bit {str(col).count('1')}"] = counts.reindex(bins).fillna(0).astype(int).values

        # Transpose the DataFrame for the desired format
        grouped = grouped.transpose()

        # Save the grouped data to CSV
        grouped.to_csv(self.exp_path + "/grouped_cc6_mod.csv")

        return grouped

        """


    def singleplot_mod(self, nr):
        """Create 1x1 Plot Matrix"""
        # Create a figure with subplots
        x_values=None
        self.font_size_axis=16
        self.font_size_title=18
        self.font_size_label=8
        
        fig, axs = mpl.subplots(1, 1, figsize=(14, 7))
        
        mpl.subplots_adjust(wspace=0.3, hspace=0.3)
        axs.set_xlabel('Number of Modifications', fontsize=self.font_size_axis)
        axs.set_ylabel('Status Code Frequency(%)', fontsize=self.font_size_axis)
        axs.legend(loc="upper right")
        if nr==1:
            self.status_code_curves_over_deviation(self.data_frame_prerequest_stats.copy(), ax=axs, subplottitles=False, autolimits=False, y_low=0, y_up=100, no_regression=True)

        elif nr==3:
            self.status_code_curves_over_deviation(self.data_frame_prerequest_stats.copy(), ax=axs,subplottitles=False, autolimits=False, y_low=0, y_up=100 )
        elif nr==34:
            x_values = [17542, 26605, 29656, 35028, 72716, 92990] 
            self.status_code_curves_over_size(self.data_frame_prerequest_stats.copy(), ax=axs,subplottitles=False, autolimits=False, y_low=0, y_up=100)
            axs.set_xlabel('Size of the Request in Bytes', fontsize=self.font_size_axis)
            axs.set_ylabel('Status Code Frequency(%)', fontsize=self.font_size_axis)
            #axs.set_title('Status Codes Frequency over Request Size', fontsize=self.font_size_title, fontweight='bold')
        elif nr==4:
            self.status_code_curves_over_deviation(self.data_frame_prerequest_stats.copy(), ax=axs,subplottitles=False, autolimits=False, y_low=95, y_up=100)
        elif nr==7:
            self.status_code_curves_over_deviation(self.data_frame_prerequest_stats.copy(), ax=axs,subplottitles=False, autolimits=False, y_low=0, y_up=100, no_regression=True)#  CC3
            x_values = [8258, 16381, 32283, 65661, 83079]
            x_values2 = [69036]
            #for x in x_values2:
                #ax.axvline(x, color='magenta', linestyle=':', linewidth=1) 
                #ax.annotate(f'{x}', (x+2300,80), textcoords="offset points", xytext=(0,10), ha='center')
        elif nr==8:
            #(16*2)
            x_values = [1792, 6240,22320,28400,58080,83504] 
        elif nr==81:
            #(16*2)
            x_values = [2128, 7486, 22534, 29735, 58767,87362]  
        elif nr==9:
            x_values = [ 8205,16476,25305,32468,66155] 
            ax.set_ylim(80, 100)
            ax.set_xlim(0, 4000)
            mpl.savefig(self.exp_path+'/single_plot_mod_detail.png', dpi=300)

        else:
            self.status_code_curves_over_deviation(self.data_frame_prerequest_stats.copy(), ax=axs,subplottitles=False, autolimits=False, y_low=0, y_up=100)
            #axs.set_title('Status Codes Frequency over Modifications', fontsize=self.font_size_title, fontweight='bold')  
        #mpl.tight_layout()
 


        if x_values is not None:
            i=0
            for x in x_values:
                axs.axvline(x, color='magenta', linestyle='--', linewidth=1) 
                if nr==3:
                    axs.annotate(f'{x}', (x+2500,85-i), textcoords="offset points", xytext=(0,10), ha='center')
                    i+=5
                elif nr==7:
                    axs.annotate(f'{x}', (x+2300,90), textcoords="offset points", xytext=(0,10), ha='center')
                elif nr==8:
                    if i==0:
                        axs.annotate(f'{x}', (x+2200,90-i), textcoords="offset points", xytext=(0,10), ha='center')
                    else:
                        axs.annotate(f'{x}', (x+3000,90-i), textcoords="offset points", xytext=(0,10), ha='center')
                    i+=3
                #y_value = data_frame.loc[data_frame['deviation_count'] == x, '2xx_percentage'].values[0]
                #ax.scatter(x, y_value, color='blue')  # Change color as needed
                #y_value = data_frame.loc[data_frame['deviation_count'] == x, '2xx_percentage'].values[0]

        # Save the figure as a single PNG file
        mpl.savefig(self.exp_path+'/single_plot_mod.png', dpi=300)

        # Show the combined plot
        #mpl.show()

        return

        

    def save_exp_analyzer_results(self, host_statistics, prerequest_statistics):
        log_file_path = self.exp_path + '/exp_analyzer_data.json'
        results = {
            'host_statistics': host_statistics,
            'prerequest_statistics': prerequest_statistics,  
        }
        with open(log_file_path, "w", encoding="utf-8") as file:
            json.dump(results, file, indent=4)


    
    
    def host_stats(self, data_frame):

        ###Host with maximum 200
        ###Host with minimum 200
        ###Host average 200
        df_2xx = data_frame[['Host', '2xx']]
        host_statistics={
            'min_2xx': df_2xx['2xx'].min(),
            'max_2xx': df_2xx['2xx'].max(),
            'avg_2xx': df_2xx['2xx'].mean(),
            'std_2xx': numpy.std(df_2xx['2xx']),
            'min_2xx_no': df_2xx.loc[df_2xx['2xx'] == df_2xx['2xx'].min(), 'Host'].iloc[0],
            'max_2xx_no': df_2xx.loc[df_2xx['2xx'] == df_2xx['2xx'].max(), 'Host'].iloc[0],
        
        }
        
        return host_statistics
    


    def prerequest_stats(self, data_frame):
       
        
        
        # Compute the average 2xx rate for the first and alst 10% of the messages
        
        df_2xx = data_frame[['no', 'deviation_count', '2xx']]
        ten_percent_count = int(len(data_frame) * 0.1)

        prereq_statistics = {
            'min_2xx': int(df_2xx['2xx'].min()),
            'max_2xx': int(df_2xx['2xx'].max()),
            'avg_2xx': df_2xx['2xx'].mean(),
            'std_deviation_2xx': numpy.std(df_2xx['2xx']),
            'min_2xx_no': int(df_2xx.loc[df_2xx['2xx'] == df_2xx['2xx'].min(), 'no'].iloc[0]),
            'max_2xx_no': int(df_2xx.loc[df_2xx['2xx'] == df_2xx['2xx'].max(), 'no'].iloc[0]),
            'min_deviation_count': int(df_2xx['deviation_count'].min()),
            'max_deviation_count': int(df_2xx['deviation_count'].max()),
            'avg_deviation_count': df_2xx['deviation_count'].mean(),
            'std_deviation_deviation_count': numpy.std(df_2xx['deviation_count']),
            'min_deviation_count_no': int(df_2xx.loc[df_2xx['deviation_count'] == df_2xx['deviation_count'].min(), 'no'].iloc[0]),
            'max_deviation_count_no': int(df_2xx.loc[df_2xx['deviation_count'] == df_2xx['deviation_count'].max(), 'no'].iloc[0]),
            'average_2xx_first_10': df_2xx['2xx'].iloc[:ten_percent_count].mean(),
            'average_2xx_last_10': df_2xx['2xx'].iloc[-ten_percent_count:].mean(),
            #MARIKERUNG
        }

        return prereq_statistics


    def plot_2xx_over_attempt_no(self, data_frame, ax, subplottitles=True, autolimits=True, y_low=0,y_up=100):
        """Plot 5 Bottom right"""
        # Calculate the share of '200x' values over the total attempt number
        data_frame['Share_2xx'] = (data_frame['2xx'] / self.experiment_configuration["max_targets"]) * 100
        data_frame = data_frame.sort_values(by='no')
        # Create a plot
        #mpl.figure(figsize=(10, 8))
        
        # Create a subplot
        #ax = mpl.gca()
        """data_frame['Share_3xx'] = (data_frame['3xx'] / self.experiment_configuration["max_targets"]) * 100
        data_frame['Share_4xx'] = (data_frame['4xx'] / self.experiment_configuration["max_targets"]) * 100
        data_frame['Share_5xx'] = (data_frame['5xx'] / self.experiment_configuration["max_targets"]) * 100
        data_frame['Share_9xx'] = (data_frame['9xx'] / self.experiment_configuration["max_targets"]) * 100

        
        
        ax.plot(data_frame['no'], data_frame['Share_2xx'], label='2xx', marker='', linestyle='-')
        ax.plot(data_frame['no'], data_frame['Share_3xx'], label='3xx', marker='', linestyle='-')
        ax.plot(data_frame['no'], data_frame['Share_4xx'], label='4xx', marker='', linestyle='-')
        ax.plot(data_frame['no'], data_frame['Share_5xx'], label='5xx', marker='', linestyle='-')
        ax.plot(data_frame['no'], data_frame['Share_9xx'], label='9xx', marker='', linestyle='-')"""
        ax.plot(data_frame['no'], data_frame['Share_2xx'], label='2xx', marker='', linestyle='-')

        
        slope, intercept, r_value, p_value, std_err = stats.linregress(data_frame['no'], data_frame['Share_2xx'])
        regression_line = slope * data_frame['no'] + intercept
        ax.plot(data_frame['no'], regression_line, 'r--', label='Regression Line')
        intercept_start = slope* data_frame['no'].min()+intercept
        intercept_start_str = f"{intercept_start:.1f}"
        intercept_start=round(intercept_start)
        max_x=data_frame['no'].max()+1
        intercept_end=slope* max_x+intercept
        intercept_end_str = f"{intercept_end:.1f}"
        intercept_end=round(intercept_end)
        #definition = f'Regression Line: y = {slope:.4f}x + {intercept:.4f}\nR-squared: {r_value ** 2:.2f}'
        
        #ax.text(400, (intercept_start+intercept_end)/2, definition, fontsize=12, color='black')
        ax.text(1-int(0.08*max_x), intercept_start, intercept_start_str, fontsize=12, color='black')
        ax.text(int(1.01*max_x), intercept_end, intercept_end_str, fontsize=12, color='black')
       
        slope=str(round(slope*(-max_x),1))  ##Request count??
        self.slope=slope
        # Customize labels and title
        if subplottitles is True:
            ax.set_xlabel('Request Index', fontsize=self.font_size_axis)
            ax.set_ylabel('2xx Response Rate per Request (%)', fontsize=self.font_size_axis)  # Updated y-axis label
            ax.set_title(f'Development of 2xx Response Rate\n over Request Index\n (blocking rate delta: '+slope+'%)' , fontsize=self.font_size_title, fontweight='bold')

        # Set y-axis limits to range from 0% to 100%
        if autolimits is False:
            ax.set_ylim(y_low, y_up)
        
        # Show the plot
        ax.grid(True)
        #ax.tight_layout()

        #mpl.savefig(self.exp_path+'/exp_stats_2xx_no_development.png', dpi=300, bbox_inches='tight')
        #mpl.show()
        return ax
#   

    def plot_2xx_over_attempt_no_double(self, data_frame, ax, subplottitles=True, autolimits=True, y_low=0,y_up=100, only_2xx=False, no_regression=False):
        """Plot 5 Bottom right"""
        # Calculate the share of '200x' values over the total attempt number
        
        
        # Create a plot
        #mpl.figure(figsize=(10, 8))
        
        # Create a subplot
        #ax = mpl.gca()
        colors = ['#9B59BB', '#2ECC77', '#F1C400', '#E74C33', '#3498DD', '#344955']
        if only_2xx is True:
            data_frame['Share_2xx'] = (data_frame['2xx'] / self.experiment_configuration["max_targets"]) * 100
            ax.plot(data_frame['no'], data_frame['Share_2xx'], label='2xx', marker='', linestyle='-', color=colors[1])
        
        else:
            data_frame['Share_1xx'] = (data_frame['1xx'] / self.experiment_configuration["max_targets"]) * 100
            data_frame['Share_2xx'] = (data_frame['2xx'] / self.experiment_configuration["max_targets"]) * 100
            data_frame['Share_3xx'] = (data_frame['3xx'] / self.experiment_configuration["max_targets"]) * 100
            data_frame['Share_4xx'] = (data_frame['4xx'] / self.experiment_configuration["max_targets"]) * 100
            data_frame['Share_5xx'] = (data_frame['5xx'] / self.experiment_configuration["max_targets"]) * 100
            data_frame['Share_9xx'] = (data_frame['9xx'] / self.experiment_configuration["max_targets"]) * 100
            data_frame = data_frame.sort_values(by='no')
            
        
            ax.plot(data_frame['no'], data_frame['Share_1xx'], label='1xx', marker='', linestyle='-', color=colors[0])
            ax.plot(data_frame['no'], data_frame['Share_2xx'], label='2xx', marker='', linestyle='-', color=colors[1])
            ax.plot(data_frame['no'], data_frame['Share_3xx'], label='3xx', marker='', linestyle='-', color=colors[2])
            ax.plot(data_frame['no'], data_frame['Share_4xx'], label='4xx', marker='', linestyle='-', color=colors[3])
            ax.plot(data_frame['no'], data_frame['Share_5xx'], label='5xx', marker='', linestyle='-', color=colors[4])
            ax.plot(data_frame['no'], data_frame['Share_9xx'], label='9xx', marker='', linestyle='-', color=colors[5])

    

        if no_regression is False:
            slope, intercept, r_value, p_value, std_err = stats.linregress(data_frame['no'], data_frame['Share_2xx'])
            regression_line = slope * data_frame['no'] + intercept
            ax.plot(data_frame['no'], regression_line, 'r--', label='Regression Line')
            intercept_start = intercept #slope* data_frame['no'].min()+intercept
            intercept_start_str = f"{intercept_start:.2f}"
            #intercept_start=round(intercept_start)
            max_x=data_frame['no'].max()+1
            intercept_end=slope* max_x+intercept
            intercept_end_str = f"{intercept_end:.2f}"
            #intercept_end=round(intercept_end)
            definition = f'Regression Line: y = {slope:.4f}x + {intercept:.4f}\nR-squared: {r_value ** 2:.2f}'
            #ax.text(400, (intercept_start+intercept_end)/2, definition, fontsize=12, color='black')
            ax.text(int(-0.05*max_x), intercept_start, intercept_start_str, fontsize=12, color='black')#-int(0.08*max_x)
            ax.text(int(1.0*max_x), intercept_end, intercept_end_str, fontsize=12, color='black')
            
            slope_percent=slope*(-max_x) ##Request count??
            self.slope=f'{slope_percent:.2f}'
            # Customize labels and title
        if subplottitles is True:
            ax.set_xlabel('Request Index', fontsize=self.font_size_axis)
            ax.set_ylabel('2xx Response Rate (%) per Request ', fontsize=self.font_size_axis)  # Updated y-axis label
            ax.set_title(f'Development of 2xx Response Rate\n over Request Index\n (blocking rate delta: '+slope+'%)' , fontsize=self.font_size_title, fontweight='bold')

        # Set y-axis limits to range from 0% to 100%
        if autolimits is False:
            ax.set_ylim(y_low, y_up)
       
        # Show the plot
        ax.grid(True)
        #ax.tight_layout()

        #mpl.savefig(self.exp_path+'/exp_stats_2xx_no_development.png', dpi=300, bbox_inches='tight')
        #mpl.show()
        return ax
    
    def plot_deviation_count_distribution(self, data_frame, ax, autolimits=True, x_low=-1, x_up=100,  y_low=0, y_up=100, bins=100 ):
        """Distribution of Modifications among request"""
        deviation_count = data_frame['deviation_count'].values

        # Create a histogram

        sns.histplot(x=deviation_count, stat='count',  color='blue', bins=bins, label='Data Distribution', ax=ax)#kde=True,

        ax.grid(True)
        if autolimits is False:
            ax.set_xlim(x_low, x_up)  
            ax.set_ylim(y_low, y_up)       
       
        return ax
    
    def export_latex_to_report(self, latex_code, report_filename):
        with open(report_filename, 'w') as report_file:
            report_file.write(latex_code)
        return    

 
    
    def plot_uri_deviation_count_distribution(self, data_frame):
        """Plot 4.1"""
        deviation_counts = data_frame['Deviation Count'].values
        sums=data_frame['Sum'].values
        frequency = sums / data_frame['Sum'].values.sum()*100
        # Create a histogram
        mpl.figure(figsize=(10, 8))
        mpl.bar(deviation_counts, frequency, color='blue', label='Data Distribution')
        #sns.histplot(deviation_counts, kde=True, color='blue', bins=100, label='Data Distribution')
        
        mpl.xlabel('Steganographic Payload / Modifications from original URI')
        mpl.ylabel('Share of Requests (%)')
        mpl.title('Steganographic Payload URI Distribution')
        mpl.legend()
        mpl.grid(True) 
        mpl.savefig(self.exp_path+'/exp_stats_uri_deviation_distribution.png', dpi=300, bbox_inches='tight')
    
    def plot_rel_uri_deviation_distribution(self, data_frame, ax):
        """Plot 4.2"""
        
        deviation_counts = data_frame['Relative Deviation'].values
        sums=data_frame['Sum'].values
        frequency = sums / data_frame['Sum'].values.sum()*100

        
        #fig, ax = mpl.subplots(figsize=(10, 8))

        #fig.patch.set_facecolor('white')
        #ax.set_facecolor('white')

        bar_plot = ax.bar(deviation_counts, sums, color='blue', label='Data Distribution')
        ax.set_xlabel('Relative Modification (%) from original URI')
        ax.set_ylabel('Request (of 1000000)')
        ax.set_title('Relative Modifications URI Distribution')
        #ax.legend()
        ax.set_facecolor('white')
        ax.patch.set_facecolor('white')
        ax.grid=True
        
        #mpl.savefig(self.exp_path+'/exp_stats_rel_uri_deviation_distribution.png', dpi=300, bbox_inches='tight')
        return ax


    def plot_unsorted_data(self, df):
        # Daten in NumPy-Arrays umwandeln
        data_frame = df.sort_values(by=['3xx', '4xx', '5xx', '9xx', '2xx'], ascending=[False, False, False, False, True])

        hosts = numpy.array(data_frame['Host'])

        statuscode_1xx = numpy.array(data_frame['1xx'])
        statuscode_2xx = numpy.array(data_frame['2xx'])
        statuscode_3xx = numpy.array(data_frame['3xx'])
        statuscode_4xx = numpy.array(data_frame['4xx'])
        statuscode_5xx = numpy.array(data_frame['5xx'])
        statuscode_9xx = numpy.array(data_frame['9xx'])

        host_count = len(hosts)
        step_size = max(1, host_count // 10)  # At least 1 host per tick
        x_ticks = numpy.arange(0, host_count + step_size, step_size)
        
        # Ungeclusterte Visualisierung der Statuscodes für Domains
        mpl.style.use('fivethirtyeight')
        mpl.figure(figsize=(12, 6))
        mpl.plot(numpy.arange(host_count), statuscode_1xx, label='Statuscode 1xx')
        mpl.plot(numpy.arange(host_count), statuscode_2xx, label='Statuscode 2xx')
        mpl.plot(numpy.arange(host_count), statuscode_3xx, label='Statuscode 3xx')
        mpl.plot(numpy.arange(host_count), statuscode_4xx, label='Statuscode 4xx')
        mpl.plot(numpy.arange(host_count), statuscode_5xx, label='Statuscode 5xx')
        mpl.plot(numpy.arange(host_count), statuscode_9xx, label='Statuscode 9xx')

        mpl.xlabel('Hosts Count')
        mpl.ylabel('Statuscodes share')
        mpl.title('Distribution of Statuscodes per Host')
        mpl.legend()
        #mpl.xticks(rotation=90)
        mpl.grid(True)
        mpl.tight_layout()
        mpl.xticks(x_ticks)    
        mpl.savefig(self.exp_path+'/exp_stats_host_statuscode.png',
                    dpi=300, bbox_inches='tight')
        #mpl.show()
        
    def plot_hosts_responses(self, dataframe, num_clusters=1000):
        
        """Plot 1"""
        
        file_path=self.exp_path+"/sorted_data.csv"
        
        #Extract Data
        df=dataframe[['Host', '1xx', '2xx', '3xx', '4xx', '5xx', '9xx']]
        #10 is not constant????
        df.loc[:, ['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']] *= 10      

        df = df.sort_values(by=['2xx', '1xx', '3xx', '4xx', '5xx', '9xx'], ascending=[False, False, False, False, False, False])

        # Divide Host into Cluster
        if len(df)<100:
            num_clusters=len(df)
        else: 
            num_clusters = 1000
        
        cluster_size = len(df) // num_clusters
        df['Cluster'] = numpy.repeat(range(num_clusters), cluster_size)
        
            
        # Sums per Cluster
        clustered_data = df.groupby('Cluster').sum()
        clustered_data.to_csv(file_path, index=False)

        #Build Diagram
        mpl.style.use('fivethirtyeight')
        colors = ['#9B59BB', '#2ECC77', '#F1C400', '#E74C33',  '#3498DD',   '#344955']
        ax = clustered_data.plot(kind='bar',  stacked=True, figsize=(12, 12),width=1, color=colors )
        
        mpl.xlabel('Hosts sorted descending by 2xx response share')
        xticks = numpy.arange(0, num_clusters+1, 100)
        ax.set_xticks(xticks)
        #ax.set_xticklabels(xticks)
        mpl.ylabel('Requests ordered by Response Codes per Host')
        mpl.title('Response Code Distribution over Hosts')
        mpl.legend(title='Response Codes', loc='lower left')

        #mpl.show()
        mpl.savefig(self.exp_path+'/exp_stats_host_statuscode_bars.png',
                    dpi=300, bbox_inches='tight')


    def figure1(self, df):
        
        # Define a color mapping for the leading digits
        color_mapping = {'1': 'purple', '2': 'green', '3': 'yellow', '4': 'red', '5': 'blue', '9': 'black'}

        host_2xx_counts = df.apply(lambda x: (x // 100 == 2).sum(), axis=0)
        sorted_hosts = host_2xx_counts.sort_values(ascending=False).index
        df_sorted = df[sorted_hosts].reindex(columns=sorted(df.columns, key=lambda x: x.split()[0]))

        fig, ax = mpl.subplots(figsize=(12, 12))

        # Loop through the DataFrame and create colored dots based on the leading digit
        for row in df_sorted.index:
            for col in df_sorted.columns:
                response_code = str(df_sorted.loc[row, col])
                leading_digit = response_code[0]
                color = color_mapping.get(leading_digit, 'gray')  # Default to gray if not in mapping
                ax.scatter(df_sorted.columns.get_loc(col), df_sorted.index.get_loc(row), c=color, s=20)

        # Sort hosts by the number of 2xx status codes
        host_2xx_counts = df.apply(lambda x: (x // 100 == 2).sum(), axis=0)
        sorted_hosts = host_2xx_counts.sort_values(ascending=False).index

        # Sort the DataFrame columns by the leading digit
        sorted_df = df[sorted_hosts].loc[:, df.columns.str.split().sort_values()]

        
        mpl.imshow(sorted_df.values, cmap='viridis', aspect='auto')
        mpl.colorbar()
        mpl.title('Pixel Plot of Response Codes')
        mpl.xlabel('Hosts')
        mpl.ylabel('Messages')

        # Show the plot
        mpl.savefig(self.exp_path+'/exp_stats_host_statuscode_pixel.png',
                    dpi=300, bbox_inches='tight')

        return



    def cluster_domains(self, data_frame, ax):
        """Figure 2: TOP RIGHT"""
        #ax = mpl.gca()
        
        #mpl.figure(figsize=(10, 8))
        #ax.style.use('fivethirtyeight')

        bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        data = data_frame['2xx']
        values, bins, bars = ax.hist(data, weights=[1 / len(data)] * len(data), bins=bins, color='blue', edgecolor='black', alpha=0.7, orientation='horizontal')
        y_ticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # Specify your desired tick positions

        #mpl.gca().set_yticks(y_ticks)
        ax.set_yticks(y_ticks)
        #mpl.gca().xaxis.set_major_formatter(PercentFormatter(1))
        ax.xaxis.set_major_formatter(PercentFormatter(1))
        ax.set_ylabel('2xx Responses Rate\n per Host (10% steps)', fontsize=self.font_size_axis)
        ax.set_xlabel('Percentage of Hosts (%)', fontsize=self.font_size_axis)
        ax.set_title('Histogram:\nCategorizing Hosts with\n Similar 2xx Response Rates in 10% Steps', fontsize=self.font_size_title, fontweight='bold')

        ax.bar_label(bars, labels=[f'{x.get_width():.2%}' for x in bars], fontsize=15, color='black')

        #mpl.savefig(self.exp_path+'/exp_stats_2xx_histogramm.png', dpi=300, bbox_inches='tight')
        return ax
        
        
        """Figure 2"""
        """ selected_column = data_frame['2xx']

        num_clusters = 10
        mpl.figure(figsize=(10, 8))
        mpl.style.use('fivethirtyeight')
        #Weight percentage
        bins=[0,10,20,30,40,50,60,70,80,90,100]
        data=data_frame['2xx']
        values, bins, bars=mpl.hist(data,weights = [1/len(data)] * len(data), bins=bins, color='blue', edgecolor='black', alpha=0.7, label='2xx Frequency', orientation='vertical')
        mpl.gca().yaxis.set_major_formatter(PercentFormatter(1))
        # Customize x-axis ticks and labels

        mpl.xticks(bins)
        
        mpl.xlabel('Domain Cluster (10% Bins)')
        mpl.ylabel('Share of 2xx Status Codes (%)')
        mpl.title('Histogramm: Success Rate Distribution Among Domains')
         # Add labels above each bar

        mpl.bar_label(bars, labels = [f'{x.get_height():.2%}' for x in bars], fontsize=15, color='black')
        mpl.savefig(self.exp_path+'/exp_stats_2xx_histogramm.png',
                    dpi=300, bbox_inches='tight')
        #mpl.show() 
        return """
        
    def cluster_prerequest(self, data_frame, ax):
        """Figure 3 Bottom Left"""
        #mpl.figure(figsize=(10, 8))
        #ax = mpl.gca()
        data_frame['2xx_percentage'] = data_frame['2xx'] / self.experiment_configuration["max_targets"] * 100
        
        #Exp19 Specific
        def linear_regression(x, m, b):
            return m * x + b
        data_frame['Cluster'] = pandas.cut(data_frame['2xx_percentage'], bins=[0, 32, 42, 62, 100], labels=['Cluster 1', 'Cluster 2', 'Cluster 3', 'Cluster 4'])
        cluster_2 = data_frame[data_frame['Cluster'] == 'Cluster 2']
        cluster_3 = data_frame[data_frame['Cluster'] == 'Cluster 3']
        
        #params_2, covariance_2 = curve_fit(linear_regression, cluster_2['deviation_count'], cluster_2['2xx_percentage'])
        #params_3, covariance_3 = curve_fit(linear_regression, cluster_3['deviation_count'], cluster_3['2xx_percentage'])

        #x_values = numpy.linspace(min(cluster_2['deviation_count']), max(cluster_2['deviation_count']), 100)
        #y_fit_2 = linear_regression(x_values, *params_2)

        #x_values = numpy.linspace(min(cluster_3['deviation_count']), max(cluster_3['deviation_count']), 100)
        #y_fit_3 = linear_regression(x_values, *params_3)

        #mpl.plot(x_values, y_fit_2, label='Regression Curve for Cluster 2', color='green')
        #mpl.plot(x_values, y_fit_3, label='Regression Curve for Cluster 3', color='purple')
        
        #CC3
        data_frame['Cluster'] = pandas.cut(data_frame['2xx_percentage'], bins=[0, 32, 42, 62, 100], labels=['Cluster 1', 'Cluster 2', 'Cluster 3', 'Cluster 4'])
        cluster_2 = data_frame[data_frame['Cluster'] == 'Cluster 2']
        cluster_3 = data_frame[data_frame['Cluster'] == 'Cluster 3']
        
        #mean_2 = cluster_2['2xx_percentage'].mean()
        #mean_3 = cluster_3['2xx_percentage'].mean()
        #ax.axhline(mean_2, color='green', linestyle='--', label=f'Mean Cluster 1: {mean_2:.1f}%')
        #ax.axhline(mean_3, color='red', linestyle='--', label=f'Mean Cluster 2: {mean_3:.1f}%')

        ax.scatter(data_frame['deviation_count'], data_frame['2xx_percentage'], alpha=0.5, s=500)  # Alpha for transparency

        # Add labels and title
        ax.set_xlabel('Steganographic Payload', fontsize=self.font_size_axis)
        ax.set_ylabel('2xx Response Rate per Request (%)', fontsize=self.font_size_axis)
        ax.set_title('Scatterplot:\n2xx Response Rate over\n Steganographic Payload', fontsize=self.font_size_title, fontweight='bold' )

        # Set y-axis limits to 0% and 100%
        #ax.set_ylim(90, 105)  # 90,105 CC2

        # Set y-tick locations and format labels as percentages
        yticks = ax.get_yticks()
        ax.set_yticks(yticks)
        ax.set_yticklabels(['{:.0f}%'.format(ytick) for ytick in yticks])

        # Show the plot
        ax.grid(True)
        #ax.tight_layout()
        #ax.legend()
        #ax.savefig(self.exp_path+'/exp_stats_prerequest_statuscodes.png', dpi=300, bbox_inches='tight')
        #mpl.show()
        return ax


    def cluster_prerequest_cc6(self, data_frame, ax):
        """Figure 3 Bottom Left"""
        #mpl.figure(figsize=(10, 8))
        #ax = mpl.gca()
        data_frame['2xx_percentage'] = data_frame['2xx'] / self.experiment_configuration["max_targets"] * 100
        
      

        ax.scatter(data_frame['deviation_count'], data_frame['2xx_percentage'], alpha=0.5, s=500)  # Alpha for transparency

        # Add labels and title
        ax.set_xlabel('Steganographic Payload', fontsize=self.font_size_axis)
        ax.set_ylabel('2xx Response Rate per Request (%)', fontsize=self.font_size_axis)
        ax.set_title('Scatterplot:\n2xx Response Rate over\n Steganographic Payload', fontsize=self.font_size_title, fontweight='bold' )

        # Set y-axis limits to 0% and 100%
        #ax.set_ylim(90, 105)  # 90,105 CC2

        # Set y-tick locations and format labels as percentages
        yticks = ax.get_yticks()
        ax.set_yticks(yticks)
        ax.set_yticklabels(['{:.0f}%'.format(ytick) for ytick in yticks])

        # Show the plot
        ax.grid(True)
        #ax.tight_layout()
        ax.legend()
        #ax.savefig(self.exp_path+'/exp_stats_prerequest_statuscodes.png', dpi=300, bbox_inches='tight')
        #mpl.show()
        return ax

    def status_code_bars_over_deviation(self, data_frame, ax=None):

        """
        MARCO1
        Plot percentage curves for different response codes over the deviation count.
        """
        if ax==None: 
            fig, ax = mpl.subplots(figsize=(10, 8))

        mpl.style.use('fivethirtyeight')
        colors = ['#9B59BB','#2ECC77','#F1C400','#E74C33','#3498DD','#344955']

        response_codes = [ '1xx','2xx', '3xx', '4xx', '5xx', '9xx']
    
        # Select only the relevant columns
        data_frame = data_frame[['deviation_count'] + response_codes].copy()
        # Sort Data by Deviation Count
        data_frame.sort_values(by='deviation_count', ascending=True, inplace=True)
        # Mean Value per deviation count
        data_frame = data_frame.groupby('deviation_count').mean().reset_index()
        for code in response_codes:
            data_frame[f'{code}_percentage'] = data_frame[code] /self.experiment_configuration["max_targets"]  * 100
        maximum_dev_count=data_frame["deviation_count"].values.max()
        interpolation_range = range(1, maximum_dev_count)
        data_frame.set_index('deviation_count', inplace=True)
        data_frame = data_frame.reindex(interpolation_range).interpolate(method='linear')
        data_frame.reset_index(inplace=True)
        # Iterate through each response code and plot its curve.
        
        i=0
        for code in response_codes:
            #data_frame[f'{code}_percentage'] = data_frame[code] /self.experiment_configuration["max_targets"]  * 100
            #Curves
            #ax.plot(data_frame['deviation_count'], data_frame[f'{code}_percentage'], label=code, color=colors[i])
            #Stacked_Bars:
            if i == 0:
                ax.bar(data_frame['deviation_count'], data_frame[f'{code}_percentage'], label=code, color=colors[i], width=1 ,alpha=0.7)
            else:
                bottom_percentage = data_frame[[f'{c}_percentage' for c in response_codes[:i]]].sum(axis=1)
                ax.bar(data_frame['deviation_count'], data_frame[f'{code}_percentage'], label=code, color=colors[i], width=1 ,alpha=0.7, bottom=bottom_percentage)
            i+=1

        # Add labels and title

        
        ax.set_xlabel('Steganographic Payload / Modifications', fontsize=12)
        ax.set_ylabel('Response Code Frequency(%)', fontsize=12)
        ax.set_title('Statuscodes Frequency over Steganographic Payload', fontsize=14, fontweight='bold')

        # Set y-axis limits if needed
        # ax.set_ylim(0, 100)

        # Set y-tick locations and format labels as percentages
        yticks = ax.get_yticks()
        ax.set_yticks(yticks)
        ax.set_yticklabels(['{:.0f}%'.format(ytick) for ytick in yticks])

        # Show the plot
        ax.grid(True)
        ax.legend(loc="upper right")
        #mpl.show()
        mpl.savefig(self.exp_path+'/status_code_bars_over_deviation.png', dpi=300, bbox_inches='tight')
        return ax





    def status_code_curves_over_deviation(self, data_frame, ax=None, subplottitles=True, autolimits=False, y_low=0, y_up=100, no_regression=False):

        """
        MARCO1
        Plot percentage curves for different response codes over the deviation count.
        """
        if ax==None: 
            fig, ax = mpl.subplots(figsize=(10, 8))

        #mpl.style.use('fivethirtyeight')
        colors = ['#9B59BB','#2ECC77','#F1C400','#E74C33','#3498DD','#344955']

        response_codes = [ '1xx','2xx', '3xx', '4xx', '5xx', '9xx']
    
        # Select only the relevant columns
        data_frame = data_frame[['deviation_count'] + response_codes].copy()
        # Sort Data by Deviation Count
        data_frame.sort_values(by='deviation_count', ascending=True, inplace=True)
        # Mean Value per deviation count
        data_frame = data_frame.groupby('deviation_count').mean().reset_index()


        #maximum_dev_count=data_frame["deviation_count"].values.max()
        #interpolation_range = range(1, maximum_dev_count)
        #CC4
        #interpolation_range = range(2, maximum_dev_count+)
        #data_frame.set_index('deviation_count', inplace=True)
        #data_frame = data_frame.reindex(interpolation_range).interpolate(method='linear')
        
        #CC4
        #data_frame = data_frame.drop(1)
        
        data_frame.reset_index(inplace=True)
        # Iterate through each response code and plot its curve.
        
        i=0
        for code in response_codes:
            data_frame[f'{code}_percentage'] = data_frame[code] /self.experiment_configuration["max_targets"]  * 100
            #Curves
            ax.plot(data_frame['deviation_count'], data_frame[f'{code}_percentage'], label=code, color=colors[i])
            
            i+=1

                #CC3
        #data_frame['Cluster'] = pandas.cut(data_frame['2xx_percentage'], bins=[0, 32, 42, 62, 100], labels=['Cluster 1', 'Cluster 2', 'Cluster 3', 'Cluster 4'])
        #cluster_2 = data_frame[data_frame['Cluster'] == 'Cluster 2']
        #cluster_3 = data_frame[data_frame['Cluster'] == 'Cluster 3']
         #CC3
        #mean_2 = cluster_2['2xx_percentage'].mean()
        #mean_3 = cluster_3['2xx_percentage'].mean()
        #ax.axhline(33, color='magenta', linestyle='--', label=f'33%')
        if no_regression==False:
            slope, intercept, r_value, p_value, std_err = stats.linregress(data_frame['deviation_count'], data_frame['2xx_percentage'])
            regression_line = slope * data_frame['deviation_count'] + intercept
            ax.plot(data_frame['deviation_count'], regression_line, color='darkgreen', linestyle='dotted', label='2xx Regression Line')

            intercept_start = slope* data_frame['deviation_count'].min()+intercept
            intercept_start_str = f"{intercept_start:.1f}%"
            intercept_start=round(intercept_start)
            max_x=data_frame['deviation_count'].max()+1
            intercept_end=slope* max_x+intercept
            intercept_end_str = f"{intercept_end:.1f}%"
            intercept_end=round(intercept_end)
            #definition = f'Regression Line: y = {slope:.4f}x + {intercept:.4f}\nR-squared: {r_value ** 2:.2f}'"""
            #ax.text(400, (intercept_start+intercept_end)/2, definition, fontsize=12, color='black')
            
            #CC4
            #if y_low > 90:
            #    ax.text(1.6, intercept_start, intercept_start_str, fontsize=12, color='black')
            #    ax.text(10.8, intercept_end, intercept_end_str, fontsize=12, color='black')
        
            #Other CC
            ax.text(-int(0.045*max_x), intercept_start, intercept_start_str, fontsize=12, color='black')
            #
            ax.text(int(0.99*max_x), intercept_end, intercept_end_str, fontsize=12, color='black')
            ##CC3
            #if y_low > 90:
            #    ax.text(0, intercept_start-0.5, intercept_start_str, fontsize=12, color='black')
            #    ax.text(int(0.95*max_x), intercept_end-0.5, intercept_end_str, fontsize=12, color='black')
            

            #x1, y1 = 0, 62
            #x2, y2 = data_frame['deviation_count'].values.max(), 53
            #mpl.plot([x1, x2], [y1, y2], color='magenta', linestyle='dotted', label=f'62-53%')
            #ax.axhline(62, color='magenta', linestyle='dotted', label=f'62%')
            #ax.axhline(55, color='magenta', linestyle='-.', label=f'62%')
            #ax.fill_between(data_frame['deviation_count'], 35, 60, color='lightgrey', alpha=0.5)
            #ax.axhline(mean_2, color='black', linestyle='--', label=f'Mean Cluster 1: {mean_2:.1f}%')
            #ax.axhline(mean_3, color='black', linestyle='--', label=f'Mean Cluster 2: {mean_3:.1f}%')

        # Add labels and title
        if subplottitles is True:
            ax.set_xlabel('Steganographic Payload / Modifications', fontsize=12)
            ax.set_ylabel('Response Code Frequency(%)', fontsize=12)
            #ax.set_title('Statuscodes Frequency over Steganographic Payload', fontsize=14, fontweight='bold')

        # Set y-axis limits if needed

        # Set y-tick locations and format labels as percentages
        if autolimits is False:
            ax.set_ylim(y_low, y_up)
        yticks = ax.get_yticks()
        ax.set_yticks(yticks)
        ax.set_yticklabels(['{:.2f}%'.format(ytick) for ytick in yticks])

        if autolimits is False:
            ax.set_ylim(y_low, y_up)
        #"""
        # ax.set_ylim(0, 100)
 
     


        ##CC9 Details

        # Show the plot
        ax.grid(True)
        #ax.legend()
        #mpl.show()

        #mpl.savefig(self.exp_path+'/status_code_curves_over_deviation.png', dpi=300, bbox_inches='tight')
        return ax

  

    def check_91_key_value_length(self,df):
        def process_line_after_cross_site(request):
            """
            Process the line following the occurrence of "cross-site" in the request string.
            Splits the line into two parts divided by ": " and returns their lengths.
            """
            # Splitting the string by newlines
            lines = request.split('\n')
            
            # Finding the line after "cross-site"
            for i, line in enumerate(lines):
                if "cross-site" in line:
                    # Check if next line exists
                    if i+1 < len(lines):
                        next_line = lines[i+1]
                        parts = next_line.split(': ')
                        if len(parts) == 2:
                            key, value = parts
                        else:
                            # In case the format is not as expected
                            key, value = '', ''
                        return len(key), len(value)
            
            # Return 0,0 if "cross-site" not found or no line after it
            return 0, 0

        # Creating new columns for key and value lengths
        df[['key_length', 'value_length']] = df['request'].apply(
            lambda x: pandas.Series(process_line_after_cross_site(x))
        )

        # Sorting by key_length and value_length
        df_sorted_by_key = df.sort_values(by='key_length')
        df_sorted_by_value = df.sort_values(by='value_length')
        
        # Creating the plot
        mpl.figure(figsize=(12, 6))

        # Plotting key_length vs 2xx/10
        mpl.plot(df_sorted_by_key['key_length'], df_sorted_by_key['2xx']/10, label='Key Length', color='blue')

        # Plotting value_length vs 2xx/10
        mpl.plot(df_sorted_by_value['value_length'], df_sorted_by_value['2xx']/10, label='Value Length', color='red')

        mpl.xlabel('Length')
        mpl.ylabel('2xx Response Rate %')
        mpl.title('Header/Key Length vs 2xx Rates')
        mpl.legend()
        mpl.grid(True)
        #mpl.show()
        mpl.savefig(self.exp_path+'/key_value.png', dpi=300, bbox_inches='tight')
        mpl.xlim(0,1000)
        mpl.axvline(256, color='magenta', linestyle='--', linewidth=1)
        mpl.annotate('256', (280,80), textcoords="offset points", xytext=(0,10), ha='center')
        mpl.savefig(self.exp_path+'/key_value_detail.png', dpi=300, bbox_inches='tight')
        
    # Applying this function to the DataFrame
    



    def status_code_curves_over_size(self, data_frame, ax=None, subplottitles=True, autolimits=False, y_low=0, y_up=100):

        """
        MARCO1
        Plot percentage curves for different response codes over the deviation count.
        """
        if ax==None: 
            fig, ax = mpl.subplots(figsize=(10, 8))

        #mpl.style.use('fivethirtyeight')
        colors = ['#9B59BB','#2ECC77','#F1C400','#E74C33','#3498DD','#344955']

        response_codes = [ '1xx','2xx', '3xx', '4xx', '5xx', '9xx']
        
        path="20231109_214542_app.hubspot.com"
        df_size = pandas.read_csv(f'{self.exp_path}/{path}/log_file.csv', index_col=0)
        merged_df = pandas.merge(data_frame, df_size, left_on='no', right_on='number', how='inner')
        

        #CC3
        #78 is the uri and host from the unchanged request
        #uri:   https://app.hubspot.com/home-beta 33
        #host:  app.hubspot.com 15
        #Average URI 28,324
        #Average Host 14,456
        merged_df['request_length'] = merged_df['request_length'] - 33 -15 +28 + 14 +1
        # Select only the relevant columns
        data_frame = merged_df[['request_length'] + response_codes].copy()
        
        # Sort Data by Deviation Count

        data_frame.sort_values(by='request_length', ascending=True, inplace=True)
        # Mean Value per deviation count
        data_frame = data_frame.groupby('request_length').mean().reset_index()

 
        data_frame.to_csv(f'{self.exp_path}/request_size_response.csv', index=False)  # 


        maximum_dev_count=data_frame["request_length"].values.max()
        interpolation_range = range(1, maximum_dev_count)
        data_frame.set_index('request_length', inplace=True)
        data_frame = data_frame.reindex(interpolation_range).interpolate(method='linear')
        data_frame.reset_index(inplace=True)
        # Iterate through each response code and plot its curve.
        
        i=0
        for code in response_codes:
            data_frame[f'{code}_percentage'] = data_frame[code] /self.experiment_configuration["max_targets"]  * 100
            #Curves
            ax.plot(data_frame['request_length'], data_frame[f'{code}_percentage'], label=code, color=colors[i])
            
            i+=1

                #CC3
        #data_frame['Cluster'] = pandas.cut(data_frame['2xx_percentage'], bins=[0, 32, 42, 62, 100], labels=['Cluster 1', 'Cluster 2', 'Cluster 3', 'Cluster 4'])
        #cluster_2 = data_frame[data_frame['Cluster'] == 'Cluster 2']
        #cluster_3 = data_frame[data_frame['Cluster'] == 'Cluster 3']
         #CC3
        #mean_2 = cluster_2['2xx_percentage'].mean()
        #mean_3 = cluster_3['2xx_percentage'].mean()
        #ax.axhline(33, color='magenta', linestyle='--', label=f'33%')
        """"
        slope, intercept, r_value, p_value, std_err = stats.linregress(data_frame['request_length'], data_frame['2xx_percentage'])
        regression_line = slope * data_frame['request_length'] + intercept
        ax.plot(data_frame['request_length'], regression_line, color='darkgreen', linestyle='dotted', label='2xx Regression Line')

        intercept_start = slope* data_frame['request_length'].min()+intercept
        intercept_start_str = f"{intercept_start:.1f}%"
        intercept_start=round(intercept_start)
        max_x=data_frame['request_length'].max()+1
        intercept_end=slope* max_x+intercept
        intercept_end_str = f"{intercept_end:.1f}%"
        intercept_end=round(intercept_end)
        #definition = f'Regression Line: y = {slope:.4f}x + {intercept:.4f}\nR-squared: {r_value ** 2:.2f}'
        
        #ax.text(400, (intercept_start+intercept_end)/2, definition, fontsize=12, color='black')
        ax.text(-int(0.05*max_x), intercept_start, intercept_start_str, fontsize=12, color='black')
        ax.text(int(1.0*max_x), intercept_end, intercept_end_str, fontsize=12, color='black')
        """
        #x1, y1 = 0, 62
        #x2, y2 = data_frame['deviation_count'].values.max(), 53
        #mpl.plot([x1, x2], [y1, y2], color='magenta', linestyle='dotted', label=f'62-53%')
        #ax.axhline(62, color='magenta', linestyle='dotted', label=f'62%')
        #ax.axhline(55, color='magenta', linestyle='-.', label=f'62%')
        #ax.fill_between(data_frame['deviation_count'], 35, 60, color='lightgrey', alpha=0.5)
        #ax.axhline(mean_2, color='black', linestyle='--', label=f'Mean Cluster 1: {mean_2:.1f}%')
        #ax.axhline(mean_3, color='black', linestyle='--', label=f'Mean Cluster 2: {mean_3:.1f}%')

        # Add labels and title
        if subplottitles is True:
            ax.set_xlabel('Steganographic Payload / Modifications', fontsize=12)
            ax.set_ylabel('Response Code Frequency(%)', fontsize=12)
            ax.set_title('Statuscodes Frequency over Steganographic Payload', fontsize=14, fontweight='bold')

        # Set y-axis limits if needed

        # Set y-tick locations and format labels as percentages
        if autolimits is False:
            ax.set_ylim(y_low, y_up)
        yticks = ax.get_yticks()
        ax.set_yticks(yticks)
        ax.set_yticklabels(['{:.2f}%'.format(ytick) for ytick in yticks])

        if autolimits is False:
            ax.set_ylim(y_low, y_up)
        #"""
        # ax.set_ylim(0, 100)
        ##CC34
        x_values = [8918, 16412, 24687, 27483, 32430, 54630, 69234, 85014] 
        ##CC 7
        #x_values = [8299, 16272, 32983, 68243] 
        ##CC8 (16*2)
        #x_values = [1792, 6240,22320,28400,58080,83504] 
        ##CC 8a (19*2)
        #x_values = [2128, 7486, 22534, 29735, 58767] 
        ##CC9
        #x_values = [1743, 8205,16476,25305,32468,66155] 
        i=0
        for x in x_values:
            ax.axvline(x, color='magenta', linestyle='--', linewidth=1)  # Change color and style as needed
            #y_value = data_frame.loc[data_frame['deviation_count'] == x, '2xx_percentage'].values[0]
            #ax.scatter(x, y_value, color='blue')  # Change color as needed
            #y_value = data_frame.loc[data_frame['deviation_count'] == x, '2xx_percentage'].values[0]
            #CC3
            #ax.annotate(f'{x}', (x+2500,85-i), textcoords="offset points", xytext=(0,10), ha='center')
            #i+=5 
            #CC7
            #ax.annotate(f'{x}', (x+2200,90), textcoords="offset points", xytext=(0,10), ha='center')
            #CC8
            #CC34
            if i==0:
                ax.annotate(f'{x}', (x+2250,92), textcoords="offset points", xytext=(0,10), ha='center')
            elif i==3:
                ax.annotate(f'{x}', (x+2400,92), textcoords="offset points", xytext=(0,10), ha='center')
            else:
                ax.annotate(f'{x}', (x+2400,92-i), textcoords="offset points", xytext=(0,10), ha='center')
            i+=3
        #"""    



        # Show the plot
        ax.grid(True)
        ax.legend()
        #mpl.show()

        #mpl.savefig(self.exp_path+'/status_code_curves_over_deviation.png', dpi=300, bbox_inches='tight')
        return ax






    def plot_scatter_prerequest(self, data_frame):
        """Figure 3.1 Bottom Left, URI"""
        mpl.figure(figsize=(10, 8))
        mpl.scatter(data_frame['Relative Deviation'], data_frame['2xx'] / data_frame['Sum'] * 100, alpha=0.5, s=500)  # Alpha for transparency

        # Add labels and title
        mpl.xlabel('Relative Deviation of URI')
        mpl.ylabel('2xx Response Rate (%)')
        mpl.title('Scatter Plot of 2xx Response Rate over relative URI Deviation', fontweight='bold')

        # Set y-axis limits to 0% and 100%
        mpl.ylim(0, 100)

        # Set y-tick locations and format labels as percentages
        yticks = mpl.gca().get_yticks()
        mpl.gca().set_yticks(yticks)
        mpl.gca().set_yticklabels(['{:.1f}%'.format(ytick) for ytick in yticks])

        # Show the plot
        mpl.grid(True)
        mpl.tight_layout()
        mpl.savefig(self.exp_path+'/exp_stats_rel_uri_statuscodes.png', dpi=300, bbox_inches='tight')
        #mpl.show()

        return


def get_logs_directory():
    """Get or create local log directory"""
    script_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(script_directory)

    # Check if directory for experiment_logs exist
    logs_directory = os.path.join(parent_directory, "logs")
   
    return logs_directory

if __name__ == "__main__":
    log_dir=get_logs_directory()
    #path = f"{log_dir}/experiment_43"
    path = f"{log_dir}/extracted_logs/EOW/experiment_7"
    dra = Domain_Response_Analyzator(path)
    dra.start()
  






""" 
        # Normalize response code values by dividing by the total response count for each host
        response_codes = ['1xx','2xx', '3xx', '4xx', '5xx', '9xx']
        df[response_codes] = df[response_codes].div(df[response_codes].sum(axis=1), axis=0)

        # Perform K-means clustering with 100 clusters
        n_clusters = 100
        kmeans = KMeans(n_clusters=n_clusters)
        df['Cluster'] = kmeans.fit_predict(df[response_codes])
        
        
        # Create a stacked bar plot
        mpl.figure(figsize=(12, 6))

        bottom = 0
        for col in df.columns[6:11]:
            mpl.bar(df['Host'], df[col], label=col, bottom=bottom)
            bottom += df[col]
        
        # Set labels and title
        mpl.xlabel('Hosts')
        mpl.ylabel('Share of Response Codes')
        mpl.title('Distribution of Response Codes by Host')

        # Show the plot
        mpl.xticks(rotation=45, ha='right')
        mpl.legend(loc='upper right')
        mpl.tight_layout()
        mpl.show() """
""" 
        data_frame = df.copy()
        response_codes = ['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']
        
        # Calculate the proportion of each response code for each host
        for code in response_codes:
            data_frame[code] = data_frame[code] / data_frame[response_codes].sum(axis=1)

        # Create clusters based on the distribution of response codes
        cluster_size = len(data_frame) // num_clusters
        clusters = [data_frame[i:i + cluster_size] for i in range(0, len(data_frame), cluster_size)]

        # Initialize a list to store the bottom values for stacking
        bottom_values = [0] * len(clusters)

        # Create a figure and axis
        fig, ax = mpl.subplots(figsize=(12, 6))

        # Iterate through response codes and plot stacked bars for each code
        x = numpy.arange(len(clusters))
        width = 0.8
        for i, code in enumerate(response_codes):
            y = [cluster[code].mean() * 100 for cluster in clusters]
            ax.bar(x, y, width, label=f'Statuscode {code}', bottom=bottom_values)
            bottom_values = [bottom + val for bottom, val in zip(bottom_values, y)]

        # Remove x-axis tick labels
        ax.set_xticklabels([])

        # Set the legend
        ax.legend()

        # Set labels and title
        ax.set_xlabel('Host Clusters')
        ax.set_ylabel('Statuscode Share (%)')
        ax.set_title('Distribution of Statuscodes in Host Clusters')

        mpl.tight_layout()

        # Save or display the plot
        mpl.savefig(self.exp_path + '/exp_stats_host_statuscode_clusters_stacked.png', dpi=300, bbox_inches='tight')
        # mpl.show()
        """

        
""" 
        data_frame = df.copy()
        response_codes = ['1xx', '2xx', '3xx', '4xx', '5xx', '9xx']
        
        # Calculate the proportion of each response code for each host
        for code in response_codes:
            data_frame[code] = data_frame[code] / data_frame[response_codes].sum(axis=1)

        # Create clusters based on the distribution of response codes
        cluster_size = len(data_frame) // num_clusters
        clusters = [data_frame[i:i + cluster_size] for i in range(0, len(data_frame), cluster_size)]

        # Initialize a list to store cluster labels
        cluster_labels = []

        # Calculate cluster labels based on the dominant response code
        for cluster in clusters:
            dominant_response_code = cluster[response_codes].idxmax(axis=1).value_counts().idxmax()
            cluster_labels.append(f'Dominant: {dominant_response_code}')

        # Create a figure and axis
        fig, ax = mpl.subplots(figsize=(12, 6))

        # Plot the bars for each cluster
        x = numpy.arange(len(cluster_labels))
        width = 0.15
        for i, code in enumerate(response_codes):
            y = [cluster[code].mean() * 100 for cluster in clusters]
            ax.bar(x + i * width, y, width, label=f'Statuscode {code}')

        # Set the x-axis labels as cluster labels
        ax.set_xticks(x + 2.5 * width)
        ax.set_xticklabels(cluster_labels, rotation=45, ha='right')

        # Set the legend
        ax.legend()

        # Set labels and title
        ax.set_xlabel('Host Clusters')
        ax.set_ylabel('Average Statuscode Share (%)')
        ax.set_title('Distribution of Statuscodes in Host Clusters')
*
        mpl.tight_layout()

        # Save or display the plot
        mpl.savefig(self.exp_path + '/exp_stats_host_statuscode_clusters.png', dpi=300, bbox_inches='tight')
        # mpl.show()
         """
        
        
        
        
        
""" # Sort the DataFrame by 1xx, 3xx, 4xx, 5xx, 9xx, and 2xx columns in descending order
        data_frame = df.sort_values(by=['1xx', '3xx', '4xx', '5xx', '9xx', '2xx'], ascending=[False, False, False, False, False, True])

        hosts = data_frame['Host']
        response_codes = ['1xx', '3xx', '4xx', '5xx', '9xx', '2xx']
        colors = ['blue', 'orange', 'red', 'purple', 'gray', 'green']
        
        host_count = len(hosts)

        # Create an array of x-values for the bars
        x = numpy.arange(host_count)
        host_count = len(hosts)
        step_size = max(1, host_count // 10)  # At least 1 host per tick
        x_ticks = numpy.arange(0, host_count + step_size, step_size)
        
        # Create a figure and axis
        fig, ax = mpl.subplots(figsize=(12, 6))

        # Iterate through response codes and plot bars for each code
        for i, code in enumerate(response_codes):
            y = data_frame[code]
            ax.bar(x, y, label=f'Statuscode {code}', color=colors[i])
           # x += 0.15  # Increase the x position to separate bars

        # Set the x-axis labels as hostnames
        ax.set_xticks(numpy.arange(host_count))
        ax.set_xticklabels(hosts, rotation=45, ha='right')

        # Set the legend
        ax.legend()

        # Set labels and title
        ax.set_xlabel('Hosts')
        ax.set_ylabel('Statuscode Share')
        ax.set_title('Distribution of Statuscodes per Host')

        mpl.tight_layout()

        # Save or display the plot
        mpl.savefig(self.exp_path + '/exp_stats_host_statuscode_bars.png', dpi=300, bbox_inches='tight')
        # mpl.show() """