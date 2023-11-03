# Experimentdata-Analysisation-Domain-Statuscode
import pandas as pandas
import os
import json
import matplotlib
import logging
import matplotlib.pyplot as mpl
import numpy as numpy
from sklearn.cluster import KMeans
from matplotlib.ticker import PercentFormatter
import seaborn as sns
from scipy.stats import norm
from scipy import stats
from scipy.optimize import curve_fit
from matplotlib.gridspec import GridSpec
from scipy.interpolate import interp1d

class Domain_Response_Analyzator():
    def __init__(self, path):
        self.exp_path = path
        self.data_frame_exp_stats = pandas.read_csv(
            path+"/experiment_stats.csv")
        self.data_frame_prerequest_stats = pandas.read_csv(
            path+"/prerequests.csv")
        self.data_frame_pd_matrix = pandas.read_csv(
            path+"/pd_matrix.csv")
        
        self.data_frame_uri = pandas.read_csv(path+"/uri_dev_statuscode.csv")
        self.data_frame_rel_uri = pandas.read_csv(path+"/rel_uri_dev_statuscode.csv")        
        self.experiment_configuration, self.exp_meta_data=self.load_exp_outcome(self.exp_path)
        self.dra_logging=logging.getLogger("main.runner.dra_logger")
        self.font_size_axis=10
        self.font_size_title=12
        self.font_size_label=8
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

    def start(self):
        #This one for Marcos Suggestions:
        self.decode_save_cc6(self.data_frame_prerequest_stats)
        
        #self.grouped_results_csv(self.data_frame_pd_matrix,self.data_frame_prerequest_stats)
        self.status_code_curves_over_deviation(self.data_frame_prerequest_stats, ax=None)
        self.status_code_bars_over_deviation(self.data_frame_prerequest_stats, ax=None)
        #self.plot_unsorted_data(self.data_frame_exp_stats)
        statuscodes_dict=self.count_status_codes(self.data_frame_pd_matrix)
        host_statistics=self.host_stats(self.data_frame_exp_stats)
        prerequest_statistics=self.prerequest_stats(self.data_frame_prerequest_stats)
        
        latex_code = self.generate_latex_table(self.experiment_configuration, self.exp_meta_data, prerequest_statistics, host_statistics, statuscodes_dict)
        report_filename = f'{self.exp_path}/experiment_report.tex'  
        
        self.export_latex_to_report(latex_code, report_filename)  


        self.save_exp_analyzer_results(host_statistics, prerequest_statistics)
        #self.plot_deviation_count_distribution(self.data_frame_prerequest_stats)
        
        self.plot_uri_deviation_count_distribution(self.data_frame_uri)
        self.plot_rel_uri_deviation_distribution(self.data_frame_rel_uri)
        self.plot_scatter_prerequest(self.data_frame_rel_uri)
        self.plot_hosts_responses(self.data_frame_exp_stats)
        #self.figure1(self.data_frame_pd_matrix)
        self.quadplot()
        return

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

        mpl.show()

    def decode_save_cc6(self,data_frame):

        # Bit 0: 
        # Bit 1: 
        # Bit 2: 
        # Bit 3:   
        # Bit 4: 
        # Bit 5: 
        # Bit 6: 
        # Bit 7: 
        # Bit 8: 
        # Bit 9: 
        # 
        bit_columns= [ 
            'Bit 0: Random Non-critical SP+HTAB',
            'Bit 1: 2048 Non-critical',
            'Bit 2: 20480 Non-critical',
            'Bit 3: 40960 Non-critical',
            'Bit 4: 61440 Non critical',
            'Bit 5: 81920 Non critical',
            'Bit 6: 1x +SP after Host',
            'Bit 7: 1x +HTAB after Host',
            'Bit 8: 1x +CRLN random position',
            'Bit 9: 1x SP after host + 1x CRLN ',
            'Bit 10: 1x HTAP after host +1 CRLN',
            'Bit 11: +SP between key +value',
        ]


        def decode_bits(deviation_count, num_bits):
            # Create a list of bit values by decoding the deviation_count.
            bit_values = [(deviation_count >> bit_index) & 1 for bit_index in range(num_bits)]
            return bit_values    

       

        # Decode each row in the original DataFrame and add the bit columns.
        for bit_index, bit_column in enumerate(bit_columns):
            data_frame[bit_column] = data_frame['deviation_count'].apply(lambda x: (x >> bit_index) & 1)

        data_frame.to_csv(self.exp_path + "/prerequest_decoded.csv", index=False)
        
        #self.create_stacked_bar_chart(data_frame)
        

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
        result_df.to_csv(self.exp_path + "/deviations_mean.csv", index=False)
        colors = ['#9B59BB', '#2ECC77', '#F1C400', '#E74C33', '#3498DD', '#344955']
        fig, ax = mpl.subplots(figsize=(10, 10))

        bottom = 0

        for i, col in enumerate(result_df.columns[1:]):
            ax.bar(result_df['Bit Name'], result_df[col], label=col, bottom=bottom, color=colors[i])
            bottom += result_df[col]

        ax.set_xlabel('Bit Name')
        ax.set_ylabel('Statuscodes Share (%)')
        ax.set_title('Stacked Bar Diagram of 2xx Rates by Bit Name')
        ax.legend(title='2xx Rates', loc='upper right')
        mpl.xticks(rotation=90)
        mpl.tight_layout()
        mpl.savefig(self.exp_path+'/discrete_deviation_response_rates.png', dpi=300)
        return result_df

    
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
        #CC3 Exp19
        bins = [-1, 20, 40, 60, 80, 100, result['deviation_count'].max() + 1]
        labels = ['0-20', '20-40', '40-60', '60-80', '80-100', '1000-Max']              
        #result['deviation_group'] = pandas.cut(result['deviation_count'], bins=bins, labels=labels)
        result['deviation_group'] = pandas.cut(result['deviation_count'], bins=bins, labels=labels)

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
                # Assuming status_code is a string with 3 digits
                if status_code not in status_code_counts:
                    status_code_counts[status_code] = 1
                else:
                    status_code_counts[status_code] += 1

        return status_code_counts
    
    def format_status_codes(self, status_code_counts):
        # Create a table with 6 columns for each group
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
            leading_digit = str(int(code))[0]  # Extract the leading digit as a string
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
        \end{tabular} 
        \\
        \hline
        \textbf{Response Statuscodes:}\\
        
        \multicolumn{2}{c}{%
        \begin{minipage}{\dimexpr\linewidth-2\tabcolsep}""" + self.format_status_codes(status_codes)+ r"""
        \end{minipage}
        } \\
        \hline
\end{tabular}  
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












    def quadplot(self):
        """Create 2x2 Plot Matrix"""
        # Create a figure with subplots

        self.font_size_axis=16
        self.font_size_title=18
        self.font_size_label=8
        
        fig, axs = mpl.subplots(2, 2, figsize=(15, 15))
        gs = GridSpec(2, 2, figure=fig)
        mpl.subplots_adjust(wspace=0.3, hspace=0.3)
        
        # Top Left
        self.plot_deviation_count_distribution(self.data_frame_prerequest_stats, ax=axs[0, 0])
        
        # Bottom Left
        self.cluster_prerequest(self.data_frame_prerequest_stats, ax=axs[1, 0])

        # Top Right
        self.cluster_domains(self.data_frame_exp_stats, ax=axs[0, 1])

        # Bottom Right
        self.plot_2xx_over_attempt_no(self.data_frame_prerequest_stats, ax=axs[1, 1])

        # Adjust spacing between subplots
        #mpl.tight_layout()
        
        # Save the figure as a single PNG file
        mpl.savefig(self.exp_path+'/combined_plots.png', dpi=300)

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
        # Assuming 'no', 'deviation_count', and '2xx' are columns in the DataFrame
        df_2xx = data_frame[['no', 'deviation_count', '2xx']]

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
        }

        return prereq_statistics


    def plot_2xx_over_attempt_no(self, data_frame, ax):
        """Plot 5 Bottom right"""
        # Calculate the share of '200x' values over the total attempt number
        data_frame['Share_2xx'] = (data_frame['2xx'] / self.experiment_configuration["max_targets"]) * 100
        data_frame = data_frame.sort_values(by='no')
        # Create a plot
        #mpl.figure(figsize=(10, 8))
        
        # Create a subplot
        #ax = mpl.gca()
        
        
        
        ax.plot(data_frame['no'], data_frame['Share_2xx'], marker='', linestyle='-')
        
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
        definition = f'Regression Line: y = {slope:.4f}x + {intercept:.4f}\nR-squared: {r_value ** 2:.2f}'
        #ax.text(400, (intercept_start+intercept_end)/2, definition, fontsize=12, color='black')
        ax.text(1-int(0.08*max_x), intercept_start, intercept_start_str, fontsize=12, color='black')
        ax.text(int(1.01*max_x), intercept_end, intercept_end_str, fontsize=12, color='black')
       
        slope=str(round(slope*(-max_x),1))  ##Request count??
        # Customize labels and title
        ax.set_xlabel('Request Index', fontsize=self.font_size_axis)
        ax.set_ylabel('2xx Response Rate per Request (%)', fontsize=self.font_size_axis)  # Updated y-axis label
        ax.set_title(f'Development of 2xx Response Rate\n over Request Index\n (blocking rate delta: '+slope+'%)' , fontsize=self.font_size_title, fontweight='bold')

        # Set y-axis limits to range from 0% to 100%
        #mpl.ylim(0, 100)

        # Show the plot
        ax.grid(True)
        #ax.tight_layout()

        #mpl.savefig(self.exp_path+'/exp_stats_2xx_no_development.png', dpi=300, bbox_inches='tight')
        #mpl.show()
        return ax
#
    
    def plot_deviation_count_distribution(self, data_frame, ax):
        """Plot 4 Top Left"""
        deviation_count = data_frame['deviation_count'].values

        # Create a histogram
        #mpl.figure(figsize=(10, 8))
        #ax = mpl.gca()
        sns.histplot(x=deviation_count, stat='percent', kde=True, color='blue', bins=100, label='Data Distribution', ax=ax)
        #mpl.ylim(0, (relative_deviation_count))
        
        ax.set_xlabel('Steganographic Payload', fontsize=self.font_size_axis)
        ax.set_ylabel("Share of all Requests (%)", fontsize=self.font_size_axis)
        ax.set_title("Histogram:\n Distribution of Steganographic Payload\n among Requests", fontsize=self.font_size_title, fontweight='bold')
        #mpl.legend()
        ax.grid(True)       
        #ax.savefig(self.exp_path+'/exp_stats_deviation_distribution.png', dpi=300, bbox_inches='tight')

        return ax
    
    def export_latex_to_report(self, latex_code, report_filename):
        with open(report_filename, 'w') as report_file:
            report_file.write(latex_code)
        return    

 
    """def plot_deviation_count_distribution(self, data_frame):
        #Plot 4
        deviation_count = data_frame['deviation_count'].values

        # Create a histogram
        mpl.figure(figsize=(10, 8))
        sns.histplot(x=deviation_count, stat='percent', kde=True, color='blue', bins=100, label='Data Distribution')
        #mpl.ylim(0, (relative_deviation_count))
        
        mpl.xlabel('Amount of difference to original Request')
        mpl.ylabel("Share of all Request")
        mpl.title("Histogram: Distribution of steganographic Payload over Requests")
        #mpl.legend()
        mpl.grid(True)       
        mpl.savefig(self.exp_path+'/exp_stats_deviation_distribution.png', dpi=300, bbox_inches='tight')"""
        
        
        
        
        
        # Show the plot or save it to a file
        #mpl.show()
        # Overlay a normal distribution curve
        #x = numpy.linspace(deviation_count.min(), deviation_count.max(), 100)
        #x = numpy.linspace(deviation_count.min(), deviation_count.max(), 30)
        #x = numpy.linspace(deviation_count.min() - 3 * std_dev, deviation_count.max() + 3 * std_dev, 100)
        #pdf = norm.pdf(x, mean, std_dev)*1000 #TODO? max_targets?
        #mpl.plot(x, pdf, 'r-', lw=2, label='Normal Distribution')
    
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
    
    def plot_rel_uri_deviation_distribution(self, data_frame):
        """Plot 4.2"""
        
        deviation_counts = data_frame['Relative Deviation'].values
        sums=data_frame['Sum'].values
        frequency = sums / data_frame['Sum'].values.sum()*100

        # Create a histogram
        mpl.figure(figsize=(10, 8))
        mpl.bar(deviation_counts, frequency, color='blue', label='Data Distribution')

        mpl.xlabel('Relative Modification (%) from original URI')
        mpl.ylabel('Share of Requests (%)')
        mpl.title('Relative Modifications URI Distribution')
        mpl.legend()
        mpl.grid(True)

        
        mpl.savefig(self.exp_path+'/exp_stats_rel_uri_deviation_distribution.png', dpi=300, bbox_inches='tight')
    
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
        
    def plot_hosts_responses(self, dataframe, num_clusters=100):
        
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

    def status_code_curves_over_deviation(self, data_frame, ax=None):

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
            data_frame[f'{code}_percentage'] = data_frame[code] /self.experiment_configuration["max_targets"]  * 100
            #Curves
            ax.plot(data_frame['deviation_count'], data_frame[f'{code}_percentage'], label=code, color=colors[i])
            
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
        ax.legend()
        #mpl.show()

        mpl.savefig(self.exp_path+'/status_code_curves_over_deviation.png', dpi=300, bbox_inches='tight')
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
    path = f"{log_dir}/extracted_logs/EOW/experiment_15"
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