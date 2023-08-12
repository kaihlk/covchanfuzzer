import csv
from tranco import Tranco

t = Tranco(cache=True, cache_dir='.tranco')
latest_list = t.list()
date_list = t.list(date='2023-08-01')

#Extract Top 1xxx
# 
target_list = latest_list.top(100)



# Save the list to a CSV file
with open('target_list.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Rank", "Domain"])
    for rank, domain in enumerate(target_list, start=1):
        csv_writer.writerow([rank, domain])

print("List saved to target_list.csv")
