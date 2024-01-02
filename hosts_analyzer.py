import os
import pandas 
import seaborn as sns
import matplotlib.pyplot as plt
from urllib.parse import urlparse


def get_logs_directory():
    """Get or create local log directory"""
    script_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(script_directory)

    # Check if directory for experiment_logs exist
    logs_directory = os.path.join(parent_directory, "logs")
   
    return logs_directory


def extract_host_column(experiment_numbers, machine_name, base_path='extracted'):
    columns = []
    log_dir=get_logs_directory()
    for exp_no in experiment_numbers:
        file_path= f"{log_dir}/extracted_logs/{machine_name}/experiment_{exp_no}/experiment_stats.csv"
        if os.path.exists(file_path):
            df = pandas.read_csv(file_path, usecols=['Host'])
            df_sorted = df.sort_values(by='Host').reset_index(drop=True)
            df_sorted.rename(columns={'Host': f'Host_{machine_name}_{exp_no}'}, inplace=True)
            columns.append(df_sorted)
        else:
            print(f"File not found: {file_path}")
    return columns

def extract_base_name(url):
    try:
        hostname = urlparse(url).hostname
        if hostname:
            parts = hostname.split('.')
            return parts[-2] if len(parts) >= 2 else None
    except:
        return None


def extract_full_hostname(url):
    try:
        hostname = urlparse(url).hostname
        if hostname:
            parts = hostname.split('.')
            return '.'.join(parts[-2:]) if len(parts) > 1 else None
    except:
        return None

if __name__ == "__main__":
    log_dir=get_logs_directory()
    #experiment numbers for EOW and ATTIC
    eow_experiment_numbers = [ 7, 17, 18, 20,  21, 22, 24, 25,26,27,28]  
    attic_experiment_numbers = [ 29, 30, 32, 33, 34, 36, 37,38]  #29, #'Host_ATTIC_38': 'Exp. 3.1',#To
    name_mapping = {
        'Host_EOW_7': 'Exp. 1',
        'Host_EOW_25': 'Exp. 2',
        'Host_attic_38': 'Exp. 3', 
        'Host_EOW_27': 'Exp. 3.1',#Replaced attic 29
        'Host_EOW_17': 'Exp. 3.2',
        'Host_attic_36': 'Exp. 4',
        'Host_attic_30': 'Exp. 5',
        'Host_EOW_28': 'Exp. 5.1',
        'Host_EOW_18': 'Exp. 6',
        'Host_EOW_20': 'Exp. 6.1',
        'Host_EOW_24': 'Exp. 7',
        'Host_attic_33': 'Exp. 7.1',
        'Host_EOW_21': 'Exp. 8',
        'Host_attic_34': 'Exp. 8.1',
        'Host_EOW_22': 'Exp. 9',
        'Host_attic_37': 'Exp. 9.1',
        }
    order = [
        'Exp. 1',
        'Exp. 2',
        'Exp. 3',
        'Exp. 3.1',
        'Exp. 3.2',
        'Exp. 4',
        'Exp. 5',
        'Exp. 5.1',
        'Exp. 6',
        'Exp. 6.1',
        'Exp. 7',
        'Exp. 7.1',
        'Exp. 8',
        'Exp. 8.1',
        'Exp. 9',
        'Exp. 9.1',
       ]

    
    # Extract columns
    eow_columns = extract_host_column(eow_experiment_numbers, 'EOW')
    attic_columns = extract_host_column(attic_experiment_numbers, 'attic')

    # Combine all columns into a single DataFrame
    combined_df = pandas.concat(eow_columns + attic_columns, axis=1)
    combined_df.rename(columns=name_mapping, inplace=True)
    combined_df=combined_df.reindex(columns=order)
    common_entries_count = {}
    for col1 in combined_df.columns:
        for col2 in combined_df.columns:
            if col1 != col2:
                # Convert columns to sets
                set1 = set(combined_df[col1].dropna())
                set2 = set(combined_df[col2].dropna())

                # Find the intersection and count common entries
                common_entries = set1.intersection(set2)
                common_entries_count[(col1, col2)] = len(common_entries)
    
    all_unique_entries = set()

    # Count and extract all unique entries across all columns
    for col in combined_df.columns:
        unique_entries = set(combined_df[col].dropna())
        all_unique_entries.update(unique_entries)

    
   

    total_unique_count = len(all_unique_entries)
   

    unique_entries_df = pandas.DataFrame(list(all_unique_entries), columns=['Unique Entries'])
    unique_entries_df['Base Name'] = unique_entries_df['Unique Entries'].apply(extract_base_name)
    unique_entries_df['Full Hostname'] = unique_entries_df['Unique Entries'].apply(extract_full_hostname)

    base_name_counts = unique_entries_df['Base Name'].value_counts()
    full_hostname_counts = unique_entries_df['Full Hostname'].value_counts()
    
    unique_entries_df.to_csv(f'{log_dir}/extracted_logs/unique_entries.csv', index=False)

    # Output the common entries count
    for pair, count in common_entries_count.items():
        print(f"Common entries between {pair[0]} and {pair[1]}: {count}")
    sorted_common_counts = sorted(common_entries_count.items(), key=lambda x: x[1], reverse=True)

    # Print the ranking
    print("Ranking of columns based on common entries with others:")
    for rank, (col, count) in enumerate(sorted_common_counts, start=1):
        print(f"{rank}. {col} - {count} common entries")
    
    
    combined_df.to_csv(f'{log_dir}/extracted_logs/combined_experiment_data.csv', index=False)

    print("Total unique entries: ",total_unique_count)
    print("Hostnames: ")
    print(base_name_counts)
    print("Hostnames +TLD") 
    print(full_hostname_counts)
    
    similarity_matrix = pandas.DataFrame(index=combined_df.columns, columns=combined_df.columns, dtype=int)

    for col1 in combined_df.columns:
        for col2 in combined_df.columns:
            if col1 != col2:
                set1 = set(combined_df[col1].dropna())
                set2 = set(combined_df[col2].dropna())
                # Ensure the value is stored as an integer
                length=len(set1.intersection(set2))
                similarity_matrix.at[col1, col2] = int(length)
            else:
                similarity_matrix.at[col1, col2] = 1000  # No self-comparison
    
    
    similarity_matrix = similarity_matrix.astype(int)
    # Generate a heatmap
    plt.figure(figsize=(10, 10))
    # The 'fmt' parameter can be omitted if all values are integers
    sns.heatmap(similarity_matrix, annot=True, fmt='d' ,cmap='coolwarm')

    plt.tight_layout()
    #plt.title('Heatmap of Common Entries Between Experiments')
    plt.show()