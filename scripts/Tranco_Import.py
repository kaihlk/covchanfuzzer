import csv
from tranco import Tranco

t = Tranco(cache=True, cache_dir='.tranco')
latest_list = t.list()
custom_list = t.list(list_id="X53QN")

#Extract Top 1xxx
# 
target_list = custom_list.top(100)

path=f"target_list_subdomain.csv"

# Save the list to a CSV file
with open(path, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    
    csv_writer.writerow(["Rank", "Domain"])
    for rank, domain in enumerate(target_list, start=1):
        csv_writer.writerow([rank, domain])

print("List saved as"+path)
