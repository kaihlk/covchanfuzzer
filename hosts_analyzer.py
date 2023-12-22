import os
import pandas 
import seaborn as sns
import matplotlib.pyplot as plt



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



if __name__ == "__main__":
   
    #experiment numbers for EOW and ATTIC
    eow_experiment_numbers = [ 7, 17, 18, 20,  21, 22, 24, 25,26]  
    attic_experiment_numbers = [ 29, 30, 32, 33, 34, 36, 37]  #29, #'Host_ATTIC_38': 'Experiment 3.1',#To
    name_mapping = {
        'Host_EOW_7': 'Experiment 1',
        'Host_EOW_25': 'Experiment 2',
        'Host_EOW_26': 'Experiment 3',
        'Host_attic_29': 'Experiment 3.1',#Replace
        'Host_EOW_17': 'Experiment 3.2',
        'Host_attic_36': 'Experiment 4',
        'Host_attic_30': 'Experiment 5',
        'Host_attic_32': 'Experiment 5.1',
        'Host_EOW_18': 'Experiment 6',
        'Host_EOW_20': 'Experiment 6.1',
        'Host_EOW_24': 'Experiment 7',
        'Host_attic_33': 'Experiment 7.1',
        'Host_EOW_21': 'Experiment 8',
        'Host_attic_34': 'Experiment 8.1',
        'Host_EOW_22': 'Experiment 9',
        'Host_attic_37': 'Experiment 9.1',
        }
    order = [
        'Experiment 1',
        'Experiment 2',
        'Experiment 3',
        'Experiment 3.1',
        'Experiment 3.2',
        'Experiment 4',
        'Experiment 5',
        'Experiment 5.1',
        'Experiment 6',
        'Experiment 6.1',
        'Experiment 7',
        'Experiment 7.1',
        'Experiment 8',
        'Experiment 8.1',
        'Experiment 9',
        'Experiment 9.1',
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

    # Output the common entries count
    for pair, count in common_entries_count.items():
        print(f"Common entries between {pair[0]} and {pair[1]}: {count}")
    sorted_common_counts = sorted(common_entries_count.items(), key=lambda x: x[1], reverse=True)

    # Print the ranking
    print("Ranking of columns based on common entries with others:")
    for rank, (col, count) in enumerate(sorted_common_counts, start=1):
        print(f"{rank}. {col} - {count} common entries")

    log_dir=get_logs_directory()
    combined_df.to_csv(f'{log_dir}/extracted_logs/combined_experiment_data.csv', index=False)

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
    plt.figure(figsize=(10, 8))
    # The 'fmt' parameter can be omitted if all values are integers
    sns.heatmap(similarity_matrix, annot=True, fmt='d' ,cmap='coolwarm')
    plt.title('Heatmap of Common Entries Between Experiments')
    plt.show()