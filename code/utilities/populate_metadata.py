
import sys
sys.path.insert(0, "..")
from collections import defaultdict
import json
import pandas as pd


from models import *
import ming_fileio_library
import ming_proteosafe_library
import metadata_validator
import ftputil

try:
    import redis
    redis_client = redis.Redis("redis://dorresteinappshub.ucsd.edu:6378")
except:
    print("no redis")



def get_dataset_files(dataset_accession, collection_name, massive_host=None):
    dataset_files = None

    try:
        dataset_files = json.loads(redis_client.get(dataset_accession))
        print("Read from Redis", len(dataset_files))
    except:
        dataset_files = None

    if dataset_files is None:
        dataset_files = ming_proteosafe_library.get_all_files_in_dataset_folder_cache(dataset_accession, collection_name, massive_host=massive_host)
        try:
            redis_client.set(dataset_accession, json.dumps(dataset_files), ex=3600)
        except:
            x = 1

    print(dataset_accession, len(dataset_files))

    return dataset_files


def resolve_metadata_filename_to_all_files(filename, all_files):
    stripped_extension = ming_fileio_library.get_filename_without_extension(filename)

    acceptable_filenames = ["f." + dataset_filename for dataset_filename in all_files if dataset_filename.find(stripped_extension) != -1]

    if len(acceptable_filenames) != 1:
        return None

    return acceptable_filenames[0]

def add_metadata_per_accession(dataset_accession, metadata_list, massive_host=None):
    whitelist_columns = ["SampleType", 
    "SampleTypeSub1", 
    "NCBITaxonomy", 
    "YearOfAnalysis", 
    "SampleCollectionMethod", 
    "SampleExtractionMethod", 
    "InternalStandardsUsed", 
    "MassSpectrometer", 
    "IonizationSourceAndPolarity", 
    "ChromatographyAndPhase", 
    "SubjectIdentifierAsRecorded", 
    "AgeInYears", 
    "BiologicalSex", 
    "UBERONBodyPartName", 
    "TermsofPosition", 
    "HealthStatus", 
    "DOIDCommonName", 
    "ComorbidityListDOIDIndex", 
    "SampleCollectionDateandTime", 
    "Country", 
    "HumanPopulationDensity", 
    "LatitudeandLongitude", 
    "DepthorAltitudeMeters", 
    "UniqueSubjectID",
    "LifeStage", 
    "UBERONOntologyIndex", 
    "DOIDOntologyIndex"]

    added_files = 0

    ###Make sure we line these datasets up
    print("Get All Files Per Dataset")
    all_files = get_dataset_files(dataset_accession, "ccms_peak", massive_host=massive_host)

    for result in metadata_list:
        filename = result["filename"].rstrip()

        dataset_filename = resolve_metadata_filename_to_all_files(filename, all_files)

        if dataset_filename == None:
            continue

        added_files += 1

        filename_db, status = Filename.get_or_create(filepath=dataset_filename, datasetaccession=dataset_accession)

        #Adding Default Attribute of Dataset Accession
        attribute_db, status = Attribute.get_or_create(categoryname="ATTRIBUTE_DatasetAccession")
        attribute_value_db, status = AttributeTerm.get_or_create(term=dataset_accession)
        join_db = FilenameAttributeConnection.get_or_create(filename=filename_db, attribute=attribute_db, attributeterm=attribute_value_db)

        for key in result:
            if not key in whitelist_columns:
                continue

            attribute_name = key
            attribute_value = result[key]

            attribute_db, status = Attribute.get_or_create(categoryname=attribute_name)
            attribute_value_db, status = AttributeTerm.get_or_create(term=attribute_value)

            join_db = FilenameAttributeConnection.get_or_create(filename=filename_db, attribute=attribute_db, attributeterm=attribute_value_db)

    if added_files == 0:
        print(dataset_accession, "No Files Found")

    return added_files

def populate_dataset_metadata(input_metadata_filename, massive_host=None):
    Filename.create_table(True)
    Attribute.create_table(True)
    AttributeTerm.create_table(True)
    Compound.create_table(True)
    CompoundFilenameConnection.create_table(True)
    FilenameAttributeConnection.create_table(True)
    CompoundTag.create_table(True)
    CompoundTagFilenameConnection.create_table(True)

    #Check if dataset metadata is in the database already
    included_accessions = []
    # try:
    #     accession_attribute = Attribute.select().where(Attribute.categoryname == "ATTRIBUTE_DatasetAccession")[0]
    #     for joined in FilenameAttributeConnection.select().where(FilenameAttributeConnection.attribute == accession_attribute).group_by(FilenameAttributeConnection.attributeterm):
    #         included_accessions.append(joined.attributeterm.term)
    # except:
    #     print("No Accessions")


    result_list = ming_fileio_library.parse_table_with_headers_object_list(input_metadata_filename, "\t")

    metadata_by_accession = defaultdict(list)

    for result in result_list:
        massive_accession = result["MassiveID"]
        metadata_by_accession[massive_accession].append(result)

    total_added_files = 0

    for dataset_accession in metadata_by_accession:
        print("Attempting Import", dataset_accession)
        if dataset_accession in included_accessions:
            print("Skipping %s, already imported" % (dataset_accession))
            continue
        added_files = add_metadata_per_accession(dataset_accession, metadata_by_accession[dataset_accession], massive_host=massive_host)
        total_added_files += added_files
        print(dataset_accession, len(metadata_by_accession[dataset_accession]), added_files)

    return total_added_files
