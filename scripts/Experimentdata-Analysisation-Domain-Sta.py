#Experimentdata-Analysisation-Domain-Statuscode
import pandas as pandas
import matplotlib.pyplot as mpl
import numpy as numpy
from sklearn.cluster import KMeans


class Domain_Response_Analyzator():
    def __init__(self, path):
        self.exp_path=path
        self.data_frame_exp_stats=pandas.read_csv(path+"experiment_stats.csv")

    def start(self):
        self.plot_unsorted_data(self.data_frame_exp_stats)
        self.cluster_domains(self.data_frame_exp_stats)

    def plot_unsorted_data(self, df):
        # Daten in NumPy-Arrays umwandeln
        data_frame = df.sort_values(by=['2xx','3xx','4xx'], ascending=[True, False, False])

        hosts = numpy.array(data_frame['Host'])
        statuscode_1xx = numpy.array(data_frame['1xx'])
        statuscode_2xx = numpy.array(data_frame['2xx'])
        statuscode_3xx = numpy.array(data_frame['3xx'])
        statuscode_4xx = numpy.array(data_frame['4xx'])
        statuscode_5xx = numpy.array(data_frame['5xx'])
        statuscode_9xx = numpy.array(data_frame['9xx'])
        
        # Ungeclusterte Visualisierung der Statuscodes für Domains
        mpl.figure(figsize=(12, 6))
        mpl.plot(hosts, statuscode_1xx, label='Statuscode 1xx', marker='o')
        mpl.plot(hosts, statuscode_2xx, label='Statuscode 2xx', marker='o')
        mpl.plot(hosts, statuscode_3xx, label='Statuscode 3xx', marker='o')
        mpl.plot(hosts, statuscode_4xx, label='Statuscode 4xx', marker='o')
        mpl.plot(hosts, statuscode_5xx, label='Statuscode 5xx', marker='o')
        mpl.plot(hosts, statuscode_9xx, label='Statuscode 9xx', marker='o')
        
        mpl.xlabel('Hosts')
        mpl.ylabel('Statuscodes Frequency')
        mpl.title('Distibution of Statuscodes per Host')
        mpl.legend()
        mpl.xticks(rotation=90)  # Für bessere Lesbarkeit der Host-Namen
        mpl.grid(True)
        mpl.tight_layout()
        
        mpl.savefig(self.exp_path+'exp_stats_host_statuscode.png', dpi=300, bbox_inches='tight')
        #mpl.show()

    def cluster_domains(self,data_frame):
        # Die Statuscode-Spalten auswählen (ohne die Domain-Spalte)
        selected_column = data_frame['2xx']

        # Anzahl der Cluster festlegen (Anzahl der Gruppen, in die Sie die Domains aufteilen möchten)
        num_clusters = 3

        # K-Means-Modell erstellen und auf die ausgewählte Spalte anwenden
        kmeans = KMeans(n_clusters=num_clusters)
        data_frame['Cluster'] = kmeans.fit_predict(selected_column.values.reshape(-1, 1))

        # Histogramm erstellen, um die Verteilung der Cluster zu visualisieren
        mpl.figure()
        mpl.hist(data_frame['2xx'], bins=20, color='blue', alpha=0.7, label='2xx Frequency', orientation='horizontal')
        mpl.xlabel('Number of Domains')
        mpl.ylabel('2xx Frequency')
        mpl.title('Distribution of Domains Based on 2xx Frequency')
        mpl.legend()
        mpl.show()
        return

    
if __name__ == "__main__":
    path="logs/experiment_82/"
    dra=Domain_Response_Analyzator(path)
    dra.start()