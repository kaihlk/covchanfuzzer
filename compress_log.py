###Compress and save Log Files
import os
import zipfile
import json


def compress_folder_with_exclusions(input_folder, output_zip, exclude_extensions):
    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(input_folder):
                for file in files:
                    if not any(file.lower().endswith(ext) for ext in exclude_extensions):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, input_folder)
                        zipf.write(file_path, arcname=arcname)

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_logs_directory():
    """Get or create local log directory"""
    script_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(script_directory)

    # Check if directory for experiment_logs exist
    logs_directory = os.path.join(parent_directory, "logs")
    export_directory= os.path.join(script_directory, "export_logs")


    return logs_directory, export_directory

def read_cc_no(path):
    file_name="experiment_outcome.json"
    json_file_path=f"{path}/{file_name}"
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            experiment_configuration = data.get('Experiment_Configuration', {})
            return experiment_configuration["covertchannel_request_number"]
    except Exception as e:
        print(f"Error: {e}")
        return {}

# Example usage:
json_file_path = 'exp_stats.json'

if __name__ == "__main__":
    
    # Example usage:
    log_dir, export_dir=get_logs_directory()
    experiment_no="98"
    experiment_maschine="ATTIC"
   
    input_folder = f"{log_dir}/experiment_{experiment_no}"
    covert_channel_no=read_cc_no(input_folder)   
    output_file_name=f"CC{covert_channel_no}_{experiment_maschine}_Experiment_{experiment_no}"
    output_zip = f"{export_dir}/{output_file_name}.zip"
    
    #Exclude to big raw data files
    exclude_extensions = ['.pcap', '.pcapng']

    if compress_folder_with_exclusions(input_folder, output_zip, exclude_extensions):
        print(f"Compression completed successfully to {output_zip}")
    else:
        print("Compression failed.")