# Welcome to ReDU

![](https://github.com/mwang87/ReDU-MS2-GNPS/workflows/production-integration/badge.svg)
![unit test](https://github.com/mwang87/ReDU-MS2-GNPS/workflows/unit%20test/badge.svg)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3924422.svg)](https://doi.org/10.5281/zenodo.3924422)


## Reanalysis of Data User Interface

[ReDU](https://redu.ucsd.edu/) is a community-minded approach to find and reuse public data containing tandem MS data at the repository scale. ReDU is a launchpad for co- or re-analysis of public data via the Global Natural Product Social Molecular Networking Platform [(GNPS)](https://gnps.ucsd.edu/ProteoSAFe/static/gnps-splash.jsp). Our aim is to empower researchers to put their data in the context of public data as well as explore questions using public data at the repository scale.

**This is a community effort and everyone is encouraged to participate by submitting their own data and sample information [instructions](https://mwang87.github.io/ReDU-MS2-Documentation/HowtoContribute). The sharing of new applications (and code) which use ReDU is highly encouraged.**

## Testing Procedure

To get ReDU up and running on your local system, it should be as easy as

```
server-compose-interactive
```

## Unit Testing

We have unit tests to test the validators. There are several naming conventions:

1. ```valid_*``` - These are valid files implying passing validation and finding the same number of files in MassIVE
1. ```invalid_*``` - These are invalid files that fail validation
1. ```invaliddata_*``` - These are valid files that pass validation but fail to match with data in MassIVE

To run all unit tests, we are using [act](https://github.com/nektos/act) to run github actions locally:

```make test-push```

to simulate a push to the repository and run the full suite of unit tests exactly as we'd run at github. 

To simulate selenium and production integration tests:

```make test-schedule```

## Manual Validation

1. Check number of files avaliable in the File Selector
1. Check the humber of unique chemical annotated in Chemical Explorer.
1. Check that graphs in Chemical Explorer are functional, available after clicking an example chemical's 'view assocations' button. (e.g. ```/compoundenrichmentdashboard?compound=Spectral%20Match%20to%20Sulfachloropyridazine%20from%20NIST14```)
1. Test all buttons to ensure links are correct.


## Updating ReDU Data Procedure

One of the key steps in ReDU is the updating of the database to include the latest identifications for files within ReDU. These are the following steps:

1. Download batch template for GNPS at ```https://redu.ucsd.edu/metabatchdump```
1. Run [Batch Workflow for Spectral Library Search](https://github.com/mwang87/ReDU-MS2-GNPS/blob/master/code/search_all_data.py)
1. Get the set of tasks as tsv and save to [here](https://github.com/mwang87/ReDU-MS2-GNPS/blob/master/database/global_tasks.tsv). 
1. Remove database [here](https://github.com/mwang87/ReDU-MS2-GNPS/tree/master/database)
1. Remove all untracked files in temp, this will be for the global pca
1. Start ReDU back up and it will autopopulate
1. Wait Until full autopopulate before going to global PCA views

