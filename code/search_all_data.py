import sys
#sys.path.insert(0, "..")
from collections import defaultdict
import json
import pandas as pd
import util
import credentials
from models import *


def parse_metabatch_dump():
    metabatch_filename = '../database/metabatchdump.tsv'
    all_filenames = pd.read_table(metabatch_filename)
   
    task_id_list = []
    parallelism = len(all_filenames)

    for index, row in all_filenames.iterrows():
        filenames = row.filename
        id = row.id
        
        taskid = util.launch_GNPS_librarysearchworkflow(filenames, "ReDU-MS2 Global Analysis Populate %d of %d" % (id, parallelism), \
        credentials.USERNAME, credentials.PASSWORD, "christineaceves22@gmail.com")
       
        task_id_list.append(taskid)
    
    df = pd.DataFrame()
    df["taskid"] = task_id_list
    df.to_csv("../database/global_tasks.tsv", sep="\t", index=False)

if __name__ == '__main__':
    parse_metabatch_dump()
