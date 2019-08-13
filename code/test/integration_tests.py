import os
import sys
import requests
import json

BASE_URL = "https://redu.ucsd.edu/"
URL_ONE = "displayglobalmultivariate"
URL_TWO = "processcomparemultivariate"
SAMPLE_TASK_ID = "ffa003f6c4d844188f1f751d34c649b0"
URL_THREE = "ReDUValidator" #optional
URL_FIVE = "compoundfilename"
TEST_COMPOUND = "2,5-Dimethoxyphenethylamine"
URL_SIX = "compoundenrichment"


def test_file_enrichment():
    query_url = BASE_URL + URL_FIVE
    params = {'compoundname' :  TEST_COMPOUND}
    response = requests.get(query_url, params = params)
    data = json.loads(response.content)

    key_value = next(iter(data[0]))

    if (key_value == 'filepath'):
        exit(0)
    else:
        exit(1)


def test_compound_enrichment():
   query_url = BASE_URL + URL_SIX  
   params = {'compoundname' : TEST_COMPOUND}
   response = requests.post(query_url, params )
   data = json.loads(response.content)
   key_value = data[0]
   
   if key_value == 'attribute_name':
       exit(0)
   else:
       exit(1)

def test_your_pca():
   params = {'task': SAMPLE_TASK_ID}
   query_url = BASE_URL + URL_TWO
   response = requests.get(query_url, params = params)
   data = response.content
   file_size = sys.getsizeof(data) 
      
   if (file_size < 28000000):
       exit(1)
   else:
       exit(0)   


def test_global_pca():
    response = requests.get(BASE_URL + URL_ONE)
    data = response.content
    file_size = sys.getsizeof(data)
            
    if (file_size < 27762100):
        exit(1)
    
    else:
        exit(0)
 
def main(): 
    test_global_pca()
    test_your_pca()
    test_compound_enrichment()   
    test_file_enrichment()

if __name__ == "__main__":
   main()