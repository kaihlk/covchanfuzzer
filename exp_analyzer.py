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


class Domain_Response_Analyzator():
    def __init__(self, path):
        self.exp_path = path
        self.data_frame_exp_stats = pandas.read_csv(
            path+"/experiment_stats.csv")
        self.data_frame_prerequest_stats = pandas.read_csv(
            path+"/prerequests.csv")
        self.experiment_configuration=self.load_exp_outcome(self.exp_path)
        self.dra_logging=logging.getLogger("main.runner.dra_logger")
        
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
        return experiment_configuration

    def start(self):
        self.plot_unsorted_data(self.data_frame_exp_stats)
        self.cluster_domains(self.data_frame_exp_stats)
        self.cluster_prerequest(self.data_frame_prerequest_stats)
        host_statistics=self.host_stats(self.data_frame_exp_stats)
        prerequest_statistics=self.prerequest_stats(self.data_frame_prerequest_stats)
        
        self.save_exp_analyzer_results(host_statistics, prerequest_statistics)
        self.plot_deviation_count_distribution(self.data_frame_prerequest_stats)
        self.plot_2xx_over_attempt_no(self.data_frame_prerequest_stats)
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


    def plot_2xx_over_attempt_no(self, data_frame):
        """Plot 5"""
        # Calculate the share of '200x' values over the total attempt number
        data_frame['Share_2xx'] = (data_frame['2xx'] / self.experiment_configuration["max_targets"]) * 100
        data_frame = data_frame.sort_values(by='no')
        # Create a plot
        mpl.figure(figsize=(10, 6))
        mpl.plot(data_frame['no'], data_frame['Share_2xx'], marker='', linestyle='-')
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(data_frame['no'], data_frame['Share_2xx'])
        regression_line = slope * data_frame['no'] + intercept
        mpl.plot(data_frame['no'], regression_line, 'r--', label='Regression Line')

        # Customize labels and title
        mpl.xlabel('Message Index')
        mpl.ylabel('Share of 2xx Responses (%)')  # Updated y-axis label
        mpl.title('Development of 2xx Statuscodes over Message No.')

        # Set y-axis limits to range from 0% to 100%
        mpl.ylim(0, 100)

        # Show the plot
        mpl.grid(True)
        mpl.tight_layout()

        mpl.savefig(self.exp_path+'/exp_stats_2xx_no_development.png', dpi=300, bbox_inches='tight')
        mpl.show()
        return

    
    def plot_deviation_count_distribution(self, data_frame):
        """Plot 4"""
        #deviation_count = data_frame['deviation_count']
        
        deviation_count = data_frame['deviation_count'].values
        relative_deviation_count = deviation_count / self.experiment_configuration["num_attempts"]*100
        # Calculate mean and standard deviation
        mean = deviation_count.mean()
        std_dev = deviation_count.std()
        # Create a histogram
        mpl.figure(figsize=(10, 6))
        sns.histplot(deviation_count, kde=True, color='blue', bins=100, label='Data Distribution')

        # Overlay a normal distribution curve
        x = numpy.linspace(deviation_count.min(), deviation_count.max(), 100)
        #x = numpy.linspace(deviation_count.min(), deviation_count.max(), 30)
        #x = numpy.linspace(deviation_count.min() - 3 * std_dev, deviation_count.max() + 3 * std_dev, 100)
        #pdf = norm.pdf(x, mean, std_dev)*1000 #TODO? max_targets?
        #mpl.plot(x, pdf, 'r-', lw=2, label='Normal Distribution')

        mpl.xlabel('Deviation Count')
        mpl.ylabel('Share %')
        mpl.title('Histogram: Deviation Count Distribution')
        mpl.legend()
        mpl.grid(True)

        # Show the plot or save it to a file
        #mpl.show()
        mpl.savefig(self.exp_path+'/exp_stats_deviation_distribution.png', dpi=300, bbox_inches='tight')
        

  
    
    def plot_unsorted_data(self, df):
        # Daten in NumPy-Arrays umwandeln
        data_frame = df.sort_values(by=['1xx','3xx', '4xx', '5xx', '9xx', '2xx'], ascending=[False,False, False, False, False, True])

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

    def cluster_domains(self, data_frame):
        """Figure 2"""
        selected_column = data_frame['2xx']

       
        num_clusters = 10

 
        mpl.figure(figsize=(12, 6))
        mpl.style.use('fivethirtyeight')
        #Weight percentage
        bins=[0,10,20,30,40,50,60,70,80,90,100]
        data=data_frame['2xx']
        values, bins, bars=mpl.hist(data,weights = [1/len(data)] * len(data), bins=bins, color='blue', edgecolor='black', alpha=0.7, label='2xx Frequency', orientation='vertical')
        mpl.gca().yaxis.set_major_formatter(PercentFormatter(1))
        # Customize x-axis ticks and labels

        mpl.xticks(bins)
        
        mpl.xlabel('Domain Cluster (10%)')
        mpl.ylabel('Percentage of 2xx Status Codes (%)')
        mpl.title('Histogramm: Success Rate Distribution Among Domains')
         # Add labels above each bar

        mpl.bar_label(bars, labels = [f'{x.get_height():.0%}' for x in bars], fontsize=15, color='black')
        mpl.savefig(self.exp_path+'/exp_stats_2xx_histogramm.png',
                    dpi=300, bbox_inches='tight')
        #mpl.show() 
        return
        
    def cluster_prerequest(self, data_frame):
        """Figure 3"""
        mpl.figure(figsize=(8, 6))
        mpl.scatter(data_frame['deviation_count'], data_frame['2xx'] / self.experiment_configuration["max_targets"] * 100, alpha=0.5, s=500)  # Alpha for transparency

        # Add labels and title
        mpl.xlabel('Deviation Count per Message')
        mpl.ylabel('2xx Responses (%)')
        mpl.title('Scatter Plot of Deviation Count vs. 2xx Responses')

        # Set y-axis limits to 0% and 100%
        mpl.ylim(0, 100)

        # Set y-tick locations and format labels as percentages
        yticks = mpl.gca().get_yticks()
        mpl.gca().set_yticks(yticks)
        mpl.gca().set_yticklabels(['{:.1f}%'.format(ytick) for ytick in yticks])

        # Show the plot
        mpl.grid(True)
        mpl.tight_layout()
        mpl.savefig(self.exp_path+'/exp_stats_prerequest_statuscodes.png', dpi=300, bbox_inches='tight')
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
    path = f"{log_dir}/experiment_28"
    dra = Domain_Response_Analyzator(path)
    dra.start()
