
import sys
sys.path.insert(0, "..")

from collections import defaultdict

from app import db
import os
import metadata_validator
import ming_fileio_library
import ming_proteosafe_library
import populate_metadata
import ftputil
import pandas as pd
import argparse
from models import *
import csv

def find_dataset_metadata(dataset_accession, useftp=False, massive_host=None):
    print("Finding Files", dataset_accession, flush=True)
    if useftp:
        try:
            list_names = massive_host.listdir("/")
        except Exception as e:
            print("MassIVE connection broken, reconnecting", e)
            massive_host = ftputil.FTPHost("massive.ucsd.edu", "anonymous", "")
            
        all_other_files = []
        all_update_files = ming_proteosafe_library.get_all_files_in_dataset_folder_cache(dataset_accession, "updates", includefilemetadata=True, massive_host=massive_host)
    else:
        import credentials
        all_other_files = ming_proteosafe_library.get_all_files_in_dataset_folder(dataset_accession, "other", credentials.USERNAME, credentials.PASSWORD, includefilemetadata=True)
        all_update_files = ming_proteosafe_library.get_all_files_in_dataset_folder(dataset_accession, "updates", credentials.USERNAME, credentials.PASSWORD, includefilemetadata=True)

    print(dataset_accession, len(all_other_files), len(all_update_files))

    #Finding gnps_metadata.tsv files
    metadata_files = [fileobject for fileobject in all_other_files if os.path.basename(fileobject["path"]) == "gnps_metadata.tsv" ]
    metadata_files += [fileobject for fileobject in all_update_files if os.path.basename(fileobject["path"]) == "gnps_metadata.tsv" ]

    metadata_files = sorted(metadata_files, key=lambda myfile: myfile["timestamp"], reverse=True)

    if len(metadata_files) > 0:
        return metadata_files[0]

    return None

def process_metadata_import(dataset_accession, dryrun=False, massive_host=None):
    print("Processing Import")
    dataset_metadatum = find_dataset_metadata(dataset_accession, useftp=True, massive_host=massive_host)

    if dataset_metadatum == None:
        print("Not Importing %s, no metadata" % dataset_accession)
        return -2, -2
    else:
        print("Importing %s" % dataset_accession, dataset_metadatum)

    #Save files Locally
    local_metadata_path = os.path.join("tempuploads", dataset_accession + ".tsv")

    try:
        massive_host.download(dataset_metadatum["path"], local_metadata_path)
    except:
        print("CANT DOWNLOAD", dataset_metadatum["path"])
        raise

    metadata_validator.rewrite_metadata(local_metadata_path)
    
    #Validate
    pass_validation, failures, errors_list, valid_rows, total_rows_count = metadata_validator.perform_validation(local_metadata_path)

    #Filtering out lines that are not valid
    local_filtered_metadata_path = os.path.join("tempuploads", "filtered_" + dataset_accession + ".tsv")
    if len([error for error in errors_list if error["error_string"].find("Missing column") != -1]) > 0:
        print("Missing Columns, Rejected")
        return -1, -1

    #Filtering out lines that do not match the dataset accession
    metadata_df = pd.DataFrame(valid_rows)
    try:
        metadata_df = metadata_df[metadata_df['MassiveID'] == dataset_accession]
    except:
        metadata_df = pd.DataFrame(valid_rows)

    metadata_df.to_csv(local_filtered_metadata_path, sep="\t", index=False)

    try:
        pass_validation, failures, errors_list, valid_rows, total_rows_count = metadata_validator.perform_validation(local_filtered_metadata_path)
    except:
        pass_validation = False

    added_files_count = 0
    if pass_validation:
        print("Importing Data")
        if not dryrun:
            added_files_count = populate_metadata.populate_dataset_metadata(local_filtered_metadata_path, massive_host=massive_host)
    else:
        print("Filtered File is not valid")

    return len(metadata_df), added_files_count

def import_identification(task_filename, output_identifications_filename, force=False):
    number_of_compounds = Compound.select().count()
    
    if number_of_compounds > 0 and force is False:
        print("Compounds Already Imported")
        return

    # Download Identifications
    print("Downloading Identifications")
    df = pd.read_csv(task_filename, sep="\t")
    all_tasks = df.to_dict(orient="records")
    all_data_df = []
    for task in all_tasks:
        taskid = task["taskid"]
        url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=DB_result/" % (taskid)
        try:
            data_df = pd.read_csv(url, sep="\t")
            print(taskid, len(data_df))
            all_data_df.append(data_df)
        except KeyboardInterrupt:
            raise
        except:
            pass

    merged_df = pd.concat(all_data_df)
    print("Total Identifications", len(merged_df))
    merged_df.to_csv(output_identifications_filename, sep="\t", index=False)

    # Populating Database
    all_files_in_db = Filename.select()
    all_files_in_db_set = set([filename.filepath for filename in all_files_in_db])

    processed_key = set()

    with open(output_identifications_filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        line_count = 0
        for row in reader:
            line_count += 1

            if line_count % 1000 == 0:
                print(line_count)

            try:
                original_path = "f." + row["full_CCMS_path"]

                if not original_path in all_files_in_db_set:
                    continue

                key = original_path + ":" + row["Compound_Name"]

                if key in processed_key:
                    continue

                filename_db = Filename.get(filepath=original_path)
                compound_db, status = Compound.get_or_create(compoundname=row['Compound_Name'])
                join_db = CompoundFilenameConnection.get_or_create(filename=filename_db, compound=compound_db)

                processed_key.add(key)
            except KeyboardInterrupt:
                raise
            except:
                print("ERROR")
                continue

def main():
    parser = argparse.ArgumentParser(description='Importing Database')
    parser.add_argument('--importmetadata', default=None, help='Imports metadata, options are all, dataset, file')
    parser.add_argument('--metadatafile', help='Imports metadata filename')
    parser.add_argument('--metadataaccession', help='Imports metadata accession')

    parser.add_argument('--importidentifications', default=None, help='Imports identifications, from task file')
    parser.add_argument('--identifications_output', help='identifications_output')

    massive_host = ftputil.FTPHost("massive.ucsd.edu", "anonymous", "")

    args = parser.parse_args()

    # Importing Metadata First
    if args.importmetadata == "all":
        summary_list = []

        print("Getting all Datasets")
        all_datasets = ming_proteosafe_library.get_all_datasets()
        for dataset in all_datasets:
            print(dataset["dataset"])

            if not "GNPS" in dataset["title"].upper():
                continue

            # Checking the FTP host
            try:
                list_names = massive_host.listdir("/")
            except Exception as e:
                print("MassIVE connection broken, reconnecting", e)
                massive_host = ftputil.FTPHost("massive.ucsd.edu", "anonymous", "")
                
            try:
                print("Importing, ", dataset["dataset"])
                total_valid_metadata_entries, files_added = process_metadata_import(dataset["dataset"], dryrun=False, massive_host=massive_host)
            except KeyboardInterrupt:
                raise
            except:
                total_valid_metadata_entries = -1
                files_added = -1

            summary_dict = {}
            summary_dict["total_valid_metadata_entries"] = total_valid_metadata_entries
            summary_dict["files_added"] = files_added
            summary_dict["accession"] = dataset["dataset"]

            summary_list.append(summary_dict)

            try:
                pd.DataFrame(summary_list).to_csv("/app/database/add_metadata_summary.tsv", sep="\t", index=False)
            except:
                continue
        
    elif args.importmetadata == "dataset":
        total_valid_metadata_entries, files_added = process_metadata_import(args.metadataaccession, massive_host=massive_host)
        print(total_valid_metadata_entries, files_added)

    elif args.importmetadata == "file":
        populate_metadata.populate_dataset_metadata(args.metadatafile, massive_host=massive_host)


    # Import Library Identifications
    if args.importidentifications is not None:
        import_identification(args.importidentifications, args.identifications_output, force=True)


if __name__ == "__main__":
    main()
