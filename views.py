#views.py
from flask import abort, jsonify, send_from_directory, render_template, request, redirect, url_for, send_file, make_response

from app import app
from models import *

import os
import csv
import json
import uuid
import util
import pandas as pd
import requests
#import requests_cache

import metadata_validator
#GLOBALS
GLOBAL_REDU_LIBRARY_SEARCH_TASK = "058564829a434277a5899f92fe4825a9"

#requests_cache.install_cache('demo_cache', allowable_codes=(200, 404, 500))

black_list_attribute = ["SubjectIdentifierAsRecorded", "UniqueSubjectID", "UBERONOntologyIndex", "DOIDOntologyIndex", "ComorbidityListDOIDIndex"]

"""Resolving ontologies only if they need to be"""
def resolve_ontology(attribute, term):
    if attribute == "ATTRIBUTE_BodyPart":
        url = "https://www.ebi.ac.uk/ols/api/ontologies/uberon/terms?iri=http://purl.obolibrary.org/obo/%s" % (term.replace(":", "_"))
        print(url)
        try:
            requests.get(url)
            ontology_json = json.loads(requests.get(url).text)
            #print(json.dumps(ontology_json))
            return ontology_json["_embedded"]["terms"][0]["label"]
        except KeyboardInterrupt:
            raise
        except:
            return term

    if attribute == "ATTRIBUTE_Disease":
        url = "https://www.ebi.ac.uk/ols/api/ontologies/doid/terms?iri=http://purl.obolibrary.org/obo/%s" % (term.replace(":", "_"))
        print(url)
        try:
            ontology_json = requests.get(url).json()
            #print(json.dumps(ontology_json))
            return ontology_json["_embedded"]["terms"][0]["label"]
        except KeyboardInterrupt:
            raise
        except:
            return term

    print((attribute, term))
    if attribute == "ATTRIBUTE_DatasetAccession":
        try:
            url = "https://massive.ucsd.edu/ProteoSAFe/proxi/datasets?resultType=full&accession=%s" % (term)
            dataset_information = requests.get(url).json()
            return dataset_information[0]["title"]
        except:
            raise
            return term


    return term

def count_compounds_in_files(filelist1, filelist2, filelist3, filelist4, filelist5, filelist6):
    output_list = []
    input_fileset1 = set(filelist1)
    input_fileset2 = set(filelist2)
    input_fileset3 = set(filelist3)
    input_fileset4 = set(filelist4)
    input_fileset5 = set(filelist5)
    input_fileset6 = set(filelist6)

    all_compounds = Compound.select()
    for my_compound in all_compounds:
        my_files = Filename.select().join(CompoundFilenameConnection).where(CompoundFilenameConnection.compound==my_compound)

        my_files_set = set([one_file.filepath for one_file in my_files])
        intersection_set1 = input_fileset1.intersection(my_files_set)
        intersection_set2 = input_fileset2.intersection(my_files_set)
        intersection_set3 = input_fileset3.intersection(my_files_set)
        intersection_set4 = input_fileset4.intersection(my_files_set)
        intersection_set5 = input_fileset5.intersection(my_files_set)
        intersection_set6 = input_fileset6.intersection(my_files_set)

        output_dict = {}
        output_dict["compound"] = my_compound.compoundname

        include_row = False

        output_dict["count1"] = len(intersection_set1)
        if len(filelist1) > 0:
            output_dict["count1_norm"] = int(float(len(intersection_set1)) / float(len(filelist1)) * 100.0)
        else:
            output_dict["count1_norm"] = 0

        output_dict["count2"] = len(intersection_set2)
        if len(filelist2) > 0:
            output_dict["count2_norm"] = int(float(len(intersection_set2)) / float(len(filelist2)) * 100.0)
        else:
            output_dict["count2_norm"] = 0

        output_dict["count3"] = len(intersection_set3)
        if len(filelist3) > 0:
            output_dict["count3_norm"] = int(float(len(intersection_set3)) / float(len(filelist3)) * 100.0)
        else:
            output_dict["count3_norm"] = 0

        output_dict["count4"] = len(intersection_set4)
        if len(filelist4) > 0:
            output_dict["count4_norm"] = int(float(len(intersection_set4)) / float(len(filelist4)) * 100.0)
        else:
            output_dict["count4_norm"] = 0

        output_dict["count5"] = len(intersection_set5)
        if len(filelist5) > 0:
            output_dict["count5_norm"] = int(float(len(intersection_set5)) / float(len(filelist5)) * 100.0)
        else:
            output_dict["count5_norm"] = 0

        output_dict["count6"] = len(intersection_set6)
        if len(filelist6) > 0:
            output_dict["count6_norm"] = int(float(len(intersection_set6)) / float(len(filelist6)) * 100.0)
        else:
            output_dict["count6_norm"] = 0

        counts_total = output_dict["count1"] + output_dict["count2"] + output_dict["count3"] + output_dict["count4"] + output_dict["count5"] + output_dict["count6"]
        if counts_total > 0:
            output_list.append(output_dict)

    return output_list

def count_tags_in_files(filelist1, filelist2, filelist3, filelist4, filelist5, filelist6):
    output_list = []
    input_fileset1 = set(filelist1)
    input_fileset2 = set(filelist2)
    input_fileset3 = set(filelist3)
    input_fileset4 = set(filelist4)
    input_fileset5 = set(filelist5)
    input_fileset6 = set(filelist6)

    all_tags = CompoundTag.select()
    for my_tag in all_tags:
        my_files = Filename.select().join(CompoundTagFilenameConnection).where(CompoundTagFilenameConnection.compoundtag==my_tag)

        my_files_set = set([one_file.filepath for one_file in my_files])
        intersection_set1 = input_fileset1.intersection(my_files_set)
        intersection_set2 = input_fileset2.intersection(my_files_set)
        intersection_set3 = input_fileset3.intersection(my_files_set)
        intersection_set4 = input_fileset4.intersection(my_files_set)
        intersection_set5 = input_fileset5.intersection(my_files_set)
        intersection_set6 = input_fileset6.intersection(my_files_set)

        output_dict = {}
        output_dict["compound"] = my_tag.tagname

        include_row = False

        output_dict["count1"] = len(intersection_set1)
        if len(filelist1) > 0:
            output_dict["count1_norm"] = int(float(len(intersection_set1)) / float(len(filelist1)) * 100.0)
        else:
            output_dict["count1_norm"] = 0

        output_dict["count2"] = len(intersection_set2)
        if len(filelist2) > 0:
            output_dict["count2_norm"] = int(float(len(intersection_set2)) / float(len(filelist2)) * 100.0)
        else:
            output_dict["count2_norm"] = 0

        output_dict["count3"] = len(intersection_set3)
        if len(filelist3) > 0:
            output_dict["count3_norm"] = int(float(len(intersection_set3)) / float(len(filelist3)) * 100.0)
        else:
            output_dict["count3_norm"] = 0

        output_dict["count4"] = len(intersection_set4)
        if len(filelist4) > 0:
            output_dict["count4_norm"] = int(float(len(intersection_set4)) / float(len(filelist4)) * 100.0)
        else:
            output_dict["count4_norm"] = 0

        output_dict["count5"] = len(intersection_set5)
        if len(filelist5) > 0:
            output_dict["count5_norm"] = int(float(len(intersection_set5)) / float(len(filelist5)) * 100.0)
        else:
            output_dict["count5_norm"] = 0

        output_dict["count6"] = len(intersection_set6)
        if len(filelist6) > 0:
            output_dict["count6_norm"] = int(float(len(intersection_set6)) / float(len(filelist6)) * 100.0)
        else:
            output_dict["count6_norm"] = 0

        counts_total = output_dict["count1"] + output_dict["count2"] + output_dict["count3"] + output_dict["count4"] + output_dict["count5"] + output_dict["count6"]
        if counts_total > 0:
            output_list.append(output_dict)

    return output_list

@app.route('/filename', methods=['GET'])
def getfilename():
    query_filename = request.args["query"].replace("/spectrum/", "/ccms_peak/")
    expanded_attributes = request.args.get("expanded", "false")

    filepath_db = Filename.select().where(Filename.filepath == query_filename)

    if len(filepath_db) == 0:
        return "[]"

    all_connections = FilenameAttributeConnection.select().where(FilenameAttributeConnection.filename == filepath_db)
    resolved_terms = []
    for connection in all_connections:
        attribute_name = connection.attribute.categoryname
        attribute_term = connection.attributeterm.term
        resolved_term = resolve_ontology(attribute_name, attribute_term)

        if expanded_attributes == "false" and attribute_name:
            resolved_terms.append(resolved_term)

        if expanded_attributes == "true" and not(attribute_name):
            resolved_terms.append(resolved_term)

    return json.dumps(resolved_terms)

@app.route('/filenamedict', methods=['GET'])
def queryfilename():
    query_filename = request.args["query"].replace("/spectrum/", "/ccms_peak/")
    expanded_attributes = request.args.get("expanded", "false")
    all_attributes = request.args.get("allattributes", "false")

    filepath_db = Filename.select().where(Filename.filepath == query_filename)

    if len(filepath_db) == 0:
        return "[]"

    all_connections = FilenameAttributeConnection.select().where(FilenameAttributeConnection.filename == filepath_db)
    resolved_terms = []
    for connection in all_connections:
        attribute_name = connection.attribute.categoryname
        attribute_term = connection.attributeterm.term
        resolved_term = resolve_ontology(attribute_name, attribute_term)

        if all_attributes == "true":
            resolved_terms.append({"attribute_name": attribute_name, "attribute_term" : resolved_term})
        else:
            if expanded_attributes == "false" and attribute_name:
                resolved_terms.append({"attribute_name": attribute_name, "attribute_term" : resolved_term})

            if expanded_attributes == "true" and not(attribute_name):
                resolved_terms.append({"attribute_name": attribute_name, "attribute_term" : resolved_term})

    return json.dumps(resolved_terms)

@app.route('/attributes', methods=['GET'])
def viewattributes():
    all_attributes = Attribute.select()

    output_list = []
    for attribute in all_attributes:
        all_terms = AttributeTerm.select().join(FilenameAttributeConnection).join(Attribute).where(Attribute.categoryname == attribute.categoryname).group_by(AttributeTerm.term)
        output_dict = {}
        output_dict["attributename"] = attribute.categoryname
        output_dict["attributedisplay"] = attribute.categoryname.replace("ATTRIBUTE_", "").replace("Analysis_", "").replace("Subject_", "").replace("Curated_", "")
        output_dict["countterms"] = len(all_terms)

        if attribute.categoryname in black_list_attribute:
            continue
        else:
            output_list.append(output_dict)

    output_list = sorted(output_list, key=lambda x: x["attributedisplay"], reverse=False)

    return json.dumps(output_list)

#Returns all the terms given an attribute along with file counts for each term
@app.route('/attribute/<attribute>/attributeterms', methods=['GET'])
def viewattributeterms(attribute):
    attribute_db = Attribute.select().where(Attribute.categoryname == attribute)
    all_terms_db = AttributeTerm.select().join(FilenameAttributeConnection).where(FilenameAttributeConnection.attribute == attribute_db).group_by(AttributeTerm.term)

    filters_list = json.loads(request.args['filters'])

    output_list = []

    for attribute_term_db in all_terms_db:
        all_files_db = Filename.select().join(FilenameAttributeConnection).where(FilenameAttributeConnection.attributeterm == attribute_term_db).where(FilenameAttributeConnection.attribute == attribute)
        all_files = set([file_db.filepath for file_db in all_files_db])
        #Adding the filter
        all_filtered_files_list = [all_files]
        for filterobject in filters_list:
            new_db = Filename.select().join(FilenameAttributeConnection).where(FilenameAttributeConnection.attributeterm == filterobject["attributeterm"]).where(FilenameAttributeConnection.attribute == filterobject["attributename"])
            all_filtered_files_list.append(set([file_db.filepath for file_db in new_db]))

        intersection_set = set.intersection(*all_filtered_files_list)



        if len(intersection_set) > 0:
            output_dict = {}
            output_dict["attributename"] = attribute
            output_dict["attributeterm"] = attribute_term_db.term
            output_dict["ontologyterm"] = resolve_ontology(attribute, attribute_term_db.term)
            output_dict["countfiles"] = len(intersection_set)
            output_list.append(output_dict)

    return json.dumps(output_list)

#Returns all the terms given an attribute along with file counts for each term
@app.route('/attribute/<attribute>/attributeterm/<term>/files', methods=['GET'])
def viewfilesattributeattributeterm(attribute, term):
    all_files_db = Filename.select().join(FilenameAttributeConnection).where(FilenameAttributeConnection.attributeterm == term).where(FilenameAttributeConnection.attribute == attribute)
    all_files = set([file_db.filepath for file_db in all_files_db])

    filters_list = json.loads(request.args['filters'])
    all_filtered_files_list = [all_files]
    for filterobject in filters_list:
        new_db = Filename.select().join(FilenameAttributeConnection).where(FilenameAttributeConnection.attributeterm == filterobject["attributeterm"]).where(FilenameAttributeConnection.attribute == filterobject["attributename"])

        all_filtered_files_list.append(set([file_db.filepath for file_db in new_db]))
    intersection_set = set.intersection(*all_filtered_files_list)

    output_list = []

    for filepath in intersection_set:
        output_dict = {}
        output_dict["attribute"] = attribute
        output_dict["attributeterm"] = term
        output_dict["filename"] = filepath
        output_list.append(output_dict)

    return json.dumps(output_list)

#Summarize Files Per Comparison Group
@app.route('/explorer', methods=['POST'])
def summarizefiles():
    all_files_G1 = json.loads(request.form["G1"])
    all_files_G2 = json.loads(request.form["G2"])
    all_files_G3 = json.loads(request.form["G3"])
    all_files_G4 = json.loads(request.form["G4"])
    all_files_G5 = json.loads(request.form["G5"])
    all_files_G6 = json.loads(request.form["G6"])

    output = count_compounds_in_files(all_files_G1, all_files_G2, all_files_G3, all_files_G4, all_files_G5, all_files_G6)

    return json.dumps(output)

# Lists all Compounds
@app.route('/compounds', methods=['GET'])
def querycompounds():
    all_compounds = []

    all_compounds_db = CompoundFilenameConnection.select(CompoundFilenameConnection.compound, fn.COUNT(CompoundFilenameConnection.compound).alias('count')).join(Compound).group_by(CompoundFilenameConnection.compound).dicts()
    print(len(all_compounds_db))
    print(all_compounds_db[0])

    for compound in all_compounds_db:
        compound_dict = {}
        compound_dict["compound"] = compound["compound"]
        compound_dict["count"] = compound["count"]

        all_compounds.append(compound_dict)

    return json.dumps(all_compounds)

@app.route('/compoundfilename', methods=['GET'])
def queryfilesbycompound():
    compoundname = request.args['compoundname']
    compound_db = Compound.select().where(Compound.compoundname == compoundname)

    filenames_db = Filename.select().join(CompoundFilenameConnection).where(CompoundFilenameConnection.compound==compound_db)

    output_filenames = []
    for filename in filenames_db:
        output_filenames.append({"filepath" : filename.filepath})

    return json.dumps(output_filenames)

@app.route('/compoundenrichment', methods=['POST'])
def compoundenrichment():
    blacklist_attributes = ["ATTRIBUTE_DatasetAccession", "ATTRIBUTE_Curated_BodyPartOntologyIndex"]

    compoundname = request.form['compoundname']
    compound_db = Compound.select().where(Compound.compoundname == compoundname)

    compound_filenames = [filename.filepath for filename in Filename.select().join(CompoundFilenameConnection).where(CompoundFilenameConnection.compound==compound_db)]


    enrichment_list = []

    if "filenames" in request.form:
        filter_filenames = set(json.loads(request.form["filenames"]))
        if len(filter_filenames) == 0:
            filter_filenames = set([filename.filepath for filename in Filename.select()])
    else:
        filter_filenames = set([filename.filepath for filename in Filename.select()])

    all_metadata = FilenameAttributeConnection.select(Attribute.categoryname, AttributeTerm.term, fn.COUNT(FilenameAttributeConnection.filename).alias('ct')).join(Attribute).switch(FilenameAttributeConnection).join(AttributeTerm).group_by(Attribute.categoryname, AttributeTerm.term).dicts()

    print(len(all_metadata))
    print(all_metadata[0])

    for attribute_term_pair in all_metadata:
        if attribute_term_pair["categoryname"].find("ATTRIBUTE_") == -1:
            continue

        if attribute_term_pair["categoryname"] in blacklist_attributes:
            continue

        print(attribute_term_pair)

        attribute_files_db = Filename.select().join(FilenameAttributeConnection).where(FilenameAttributeConnection.attributeterm == attribute_term_pair["term"]).where(FilenameAttributeConnection.attribute == attribute_term_pair["categoryname"])
        attribute_filenames = set([filename.filepath for filename in attribute_files_db]).intersection(filter_filenames)

        if len(attribute_filenames) > 0:
            intersection_filenames = set(compound_filenames).intersection(set(attribute_filenames)).intersection(filter_filenames)

            enrichment_dict = {}
            enrichment_dict["attribute_name"] = attribute_term_pair["categoryname"]
            enrichment_dict["attribute_term"] = attribute_term_pair["term"]
            enrichment_dict["totalfiles"] = len(attribute_filenames)
            enrichment_dict["compoundfiles"] = len(intersection_filenames)
            enrichment_dict["percentage"] = len(intersection_filenames)/float(len(attribute_filenames))

            enrichment_list.append(enrichment_dict)

    enrichment_list = sorted(enrichment_list, key=lambda list_object: list_object["percentage"], reverse=True)

    return json.dumps(enrichment_list)

@app.route('/filesenrichment', methods=['POST'])
def filesenrichment():
    blacklist_attributes = ["ATTRIBUTE_DatasetAccession", "ATTRIBUTE_Curated_BodyPartOntologyIndex"]

    compound_filenames = set(json.loads(request.form["filenames"]))
    enrichment_list = []
        
    filter_filenames = set([filename.filepath for filename in Filename.select()])

    all_metadata = FilenameAttributeConnection.select(Attribute.categoryname, AttributeTerm.term, fn.COUNT(FilenameAttributeConnection.filename).alias('ct')).join(Attribute).switch(FilenameAttributeConnection).join(AttributeTerm).group_by(Attribute.categoryname, AttributeTerm.term).dicts()

    print(len(all_metadata))
    print(all_metadata[0])

    for attribute_term_pair in all_metadata:
        if attribute_term_pair["categoryname"].find("ATTRIBUTE_") == -1:
            continue

        if attribute_term_pair["categoryname"] in blacklist_attributes:
            continue

        print(attribute_term_pair)

        attribute_files_db = Filename.select().join(FilenameAttributeConnection).where(FilenameAttributeConnection.attributeterm == attribute_term_pair["term"]).where(FilenameAttributeConnection.attribute == attribute_term_pair["categoryname"])
        attribute_filenames = set([filename.filepath for filename in attribute_files_db]).intersection(filter_filenames)

        if len(attribute_filenames) > 0:
            intersection_filenames = set(compound_filenames).intersection(set(attribute_filenames)).intersection(filter_filenames)

            enrichment_dict = {}
            enrichment_dict["attribute_name"] = attribute_term_pair["categoryname"]
            enrichment_dict["attribute_term"] = attribute_term_pair["term"]
            enrichment_dict["totalfiles"] = len(attribute_filenames)
            enrichment_dict["compoundfiles"] = len(intersection_filenames)
            enrichment_dict["percentage"] = len(intersection_filenames)/float(len(attribute_filenames))

            enrichment_list.append(enrichment_dict)

    enrichment_list = sorted(enrichment_list, key=lambda list_object: list_object["percentage"], reverse=True)

    return json.dumps(enrichment_list)



@app.route('/tagexplorer', methods=['POST'])
def summarizetagfiles():
    all_files_G1 = json.loads(request.form["G1"])
    all_files_G2 = json.loads(request.form["G2"])
    all_files_G3 = json.loads(request.form["G3"])
    all_files_G4 = json.loads(request.form["G4"])
    all_files_G5 = json.loads(request.form["G5"])
    all_files_G6 = json.loads(request.form["G6"])

    output = count_tags_in_files(all_files_G1, all_files_G2, all_files_G3, all_files_G4, all_files_G5, all_files_G6)

    return json.dumps(output)

@app.route('/plottags', methods=['POST'])
def plottags():
    import os
    uuid_to_use = str(uuid.uuid4())
    input_filename = os.path.join("static", "temp", uuid_to_use + ".tsv")
    all_counts = json.loads(request.form["tagcounts"])
    sourcelevel = request.form["sourcelevel"]

    with open(input_filename, 'w') as csvfile:
        field_name = ["source information", "G1 number", "G1 percent", "G2 number", "G2 percent", "G3 number", "G3 percent", "G4 number", "G4 percent", "G5 number", "G5 percent", "G6 number", "G6 percent"]
        writer = csv.DictWriter(csvfile, fieldnames=field_name, delimiter="\t")

        writer.writeheader()

        for row in all_counts:
            new_dict = {}
            new_dict["source information"] = row["compound"]
            new_dict["G1 number"] = row["count1"]
            new_dict["G1 percent"] = row["count1_norm"]
            new_dict["G2 number"] = row["count2"]
            new_dict["G2 percent"] = row["count2_norm"]
            new_dict["G3 number"] = row["count3"]
            new_dict["G3 percent"] = row["count3_norm"]
            new_dict["G4 number"] = row["count4"]
            new_dict["G4 percent"] = row["count4_norm"]
            new_dict["G5 number"] = row["count5"]
            new_dict["G6 percent"] = row["count5_norm"]
            new_dict["G6 number"] = row["count6"]
            new_dict["G6 percent"] = row["count6_norm"]
            writer.writerow(new_dict)

    output_counts_png = os.path.join("static", "temp", uuid_to_use + "_count.png")
    output_percent_png = os.path.join("static", "temp", uuid_to_use + "_percent.png")

    cmd = "Rscript %s %s %s %s %s" % ("Meta_Analysis_Plot_Example.r", input_filename, output_counts_png, output_percent_png, sourcelevel)
    print(cmd)
    os.system(cmd)

    return json.dumps({"uuid" : uuid_to_use})


#Launch Job
import credentials



#Summarize Files Per Comparison Group
@app.route('/explorerdashboard', methods=['GET'])
def explorerdashboard():
    return render_template('explorerdashboard.html')

#Summarize Files Per Comparison Group
@app.route('/tagdashboard', methods=['GET'])
def tagdashboard():
    return render_template('tagdashboard.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')



""" Production Views """

@app.route('/', methods=['GET'])
def homepage():
    total_files = Filename.select().count()
    return render_template('homepage.html', total_files=total_files)

@app.route('/globalmultivariate', methods=['GET'])
def globalmultivariate():
    return render_template('globalmultivariate.html')

@app.route('/comparemultivariate', methods=['GET'])
def comparemultivariate():
    return render_template('comparemultivariate.html')


@app.route('/compoundslist', methods=['GET'])
def compoundslist():
    return render_template('compoundslist.html')

@app.route('/compoundenrichmentdashboard', methods=['GET'])
def compoundenrichmentview():
    return render_template('compoundenrichment.html')

@app.route('/metadataselection', methods=['GET'])
def metadataselection():
    return render_template('metadataselection.html')

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return "{'status' : 'up'}"

@app.route('/datalookup', methods=['GET'])
def datalookup():
    return render_template('datalookup.html')

@app.route('/addmetadata', methods=['GET'])
def addmetadata():
    return render_template('addmetadata.html')

@app.route('/dump', methods=['GET'])
def dump():
    return send_file('./all_metadata_dumps.tsv', cache_timeout=1, as_attachment=True, attachment_filename="all_sampleinformation.tsv")






# API End Points

def allowed_file_metadata(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ["tsv"]

@app.route('/validate', methods=['POST'])
def validate():
    request_file = request.files['file']

    #Invalid File Types
    if not allowed_file_metadata(request_file.filename):
        error_dict = {}
        error_dict["header"] = "Incorrect File Type"
        error_dict["line_number"] = "N/A"
        error_dict["error_string"] = "Please provide a tab separated file"

        validation_dict = {}
        validation_dict["status"] = False
        validation_dict["errors"] = [error_dict]
        validation_dict["stats"] = []
        validation_dict["stats"].append({"type":"total_rows", "value": 0})
        validation_dict["stats"].append({"type":"valid_rows", "value": 0})

        return json.dumps(validation_dict)

    local_filename = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()))
    request_file.save(local_filename)

    """Trying stuff out with pandas"""
    metadata_df = pd.read_csv(local_filename, sep="\t")
    metadata_df.to_csv(local_filename, index=False, sep="\t")

    metadata_validator.rewrite_metadata(local_filename)

    pass_validation, failures, errors_list, valid_rows, total_rows = metadata_validator.perform_validation(local_filename)

    validation_dict = {}
    validation_dict["status"] = pass_validation
    validation_dict["errors"] = errors_list
    validation_dict["stats"] = []

    validation_dict["stats"].append({"type":"total_rows", "value":total_rows})
    validation_dict["stats"].append({"type":"valid_rows", "value":len(valid_rows)})

    """Try to find datasets in public data"""
    try:
        dataset_success, result_string, valid_items = metadata_validator.perform_validation_against_massive(local_filename)
        validation_dict["stats"].append({"type":"massive_files_founds", "value": valid_items})

    except:
        print("Massive validation error")

    try:
        os.remove(local_filename)
    except:
        print("Cannot Remove File")

    return json.dumps(validation_dict)

@app.route('/analyzelibrarysearch', methods=['POST'])
def analyzelibrarysearch():
    all_files = json.loads(request.form["files"])
    taskid = util.launch_GNPS_librarysearchworkflow(all_files, "Meta-Analysis on GNPS", credentials.USERNAME, credentials.PASSWORD, "miw023@ucsd.edu")
    return json.dumps({"taskid": taskid})


import uuid
import redu_pca

@app.route('/processcomparemultivariate', methods=['GET'])
def processcomparemultivariate():

    #Making sure we have the local filenames
    if not os.path.isfile("component_matrix.csv"):
        print("Retrieving Global Identifications")
        
        remote_url = "http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=DB_result/" % (GLOBAL_REDU_LIBRARY_SEARCH_TASK)
        global_filename = "global_occurrences.tsv"
        r = requests.get(remote_url)
        with open(global_filename, 'wb') as f:
            f.write(r.content)
        redu_pca.calculate_master_projection(global_filename)

    task_id = request.args['task']
    new_analysis_filename = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()))
    print(os.listdir(app.config['UPLOAD_FOLDER']))
    #Making sure we have the local compound name
    remote_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=compound_filename_occurences/" % (task_id)
    
    r = requests.get(remote_url)
    with open(new_analysis_filename, 'wb') as f:
        f.write(r.content)
                                                             
   #output_png = os.path.join("./tempuploads", str(uuid.uuid4()))
    output_png = ("./tempuploads")
    redu_pca.project_new_data(new_analysis_filename, output_png)
    return send_file("./tempuploads/index.html")
