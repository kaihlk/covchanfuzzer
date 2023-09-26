# Experimentdata-Analysisation-Domain-Statuscode
import pandas as pandas
import matplotlib
import matplotlib.pyplot as mpl
import numpy as numpy
from sklearn.cluster import KMeans
from matplotlib.ticker import PercentFormatter


class Domain_Response_Analyzator():
    def __init__(self, path):
        self.exp_path = path
        self.data_frame_exp_stats = pandas.read_csv(
            path+"/experiment_stats.csv")
        self.data_frame_prerequest_stats = pandas.read_csv(
            path+"/prerequests.csv")    

    def start(self):
        self.plot_unsorted_data(self.data_frame_exp_stats)
        self.cluster_domains(self.data_frame_exp_stats)
        self.cluster_prerequest(self.data_frame_prerequest_stats)

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

        # Ungeclusterte Visualisierung der Statuscodes für Domains
        mpl.style.use('fivethirtyeight')
        mpl.figure(figsize=(12, 6))
        mpl.plot(hosts, statuscode_1xx, label='Statuscode 1xx')
        mpl.plot(hosts, statuscode_2xx, label='Statuscode 2xx')
        mpl.plot(hosts, statuscode_3xx, label='Statuscode 3xx')
        mpl.plot(hosts, statuscode_4xx, label='Statuscode 4xx')
        mpl.plot(hosts, statuscode_5xx, label='Statuscode 5xx')
        mpl.plot(hosts, statuscode_9xx, label='Statuscode 9xx')

        mpl.xlabel('Hosts')
        mpl.ylabel('Statuscodes share')
        mpl.title('Distibution of statuscodes per Host')
        mpl.legend()
        mpl.xticks(rotation=90)  # Für bessere Lesbarkeit der Host-Namen
        mpl.grid(True)
        mpl.tight_layout()
        mpl.xticks([])    
        mpl.savefig(self.exp_path+'/exp_stats_host_statuscode.png',
                    dpi=300, bbox_inches='tight')
        #mpl.show()

    def cluster_domains(self, data_frame):
        # Die Statuscode-Spalten auswählen (ohne die Domain-Spalte)
        selected_column = data_frame['2xx']

        # Anzahl der Cluster festlegen (Anzahl der Gruppen, in die Sie die Domains aufteilen möchten)
        num_clusters = 10

        # K-Means-Modell erstellen und auf die ausgewählte Spalte anwenden
        kmeans = KMeans(n_clusters=num_clusters)
        data_frame['Cluster'] = kmeans.fit_predict(selected_column.values.reshape(-1, 1))

 
        mpl.figure(figsize=(12, 6))
        mpl.style.use('fivethirtyeight')
        #Weight percentage
        bins=[0,10,20,30,40,50,60,70,80,90,100]
        data=data_frame['2xx']
        values, bins, bars=mpl.hist(data,weights = [1/len(data)] * len(data), bins=bins, color='blue', edgecolor='black', alpha=0.7, label='2xx Frequency', orientation='vertical')
        mpl.gca().yaxis.set_major_formatter(PercentFormatter(1))
        
        mpl.xlabel('Share of domains')
        mpl.ylabel('Share of 2xx responses')
        mpl.title('Histogramm of domains based on 2xx share')
         # Add labels above each bar
          

       
        mpl.bar_label(bars, labels = [f'{x.get_height():.0%}' for x in bars], fontsize=15, color='black')
        mpl.savefig(self.exp_path+'/exp_stats_2xx_histogramm.png',
                    dpi=300, bbox_inches='tight')
        #mpl.show() 
        return
    def cluster_prerequest(self, data_frame):
        mpl.figure(figsize=(8, 6))
        mpl.scatter(data_frame['deviation_count'], data_frame['2xx'], alpha=0.5)  # Alpha for transparency

        # Add labels and title
        mpl.xlabel('Deviation Count')
        mpl.ylabel('2xx Value')
        mpl.title('Scatter Plot of Deviation Count vs. 2xx Value')

        # Show the plot
        mpl.grid(True)
        mpl.tight_layout()
        mpl.savefig(self.exp_path+'/exp_stats_prerequest_statuscodes.png', dpi=300, bbox_inches='tight')
       # mpl.show()
        
        return

if __name__ == "__main__":
    path = "logs/experiment_82/"
    dra = Domain_Response_Analyzator(path)
    dra.start()
