import os
import sys
import datetime as dt
import pandas as pd

# Testing related variables
MANUAL_TEST = False
FIRST_TIME_USER_TEST = False
SAVE_FILES = False
USE_PREDEFINED_SETTING = True
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import config as cfg
# settings
CLIENT_ID = cfg.CLIENT_ID
CLIENT_SECRET = cfg.CLIENT_SECRET
CLIENT_CREDENTIAL_PATH = cfg.CLIENT_CREDENTIAL_PATH
CLIENT_CREDENTIAL_FILE_NAME = cfg.CLIENT_CREDENTIAL_FILE_NAME
BASE_URL = cfg.BASE_URL
OAUTH_URL = cfg.OAUTH_URL
REQUEST_TIMEOUT = cfg.REQUEST_TIMEOUT
DATA_ENDPOINT = cfg.DATA_ENDPOINT
METADATA_ENDPOINT = cfg.METADATA_ENDPOINT
PARTITIONS_ENDPOINT = cfg.PARTITIONS_ENDPOINT
MOCK_DATA_ENDING = cfg.MOCK_DATA_ENDING
USE_MOCK = cfg.USE_MOCK
HISTORIC_DATA_ENDING = cfg.HISTORIC_DATA_ENDING
ERROR_CODES_DICT = cfg.ERROR_CODES_DICT
SUCCESS_CODES_DICT = cfg.SUCCESS_CODES_DICT
DATASET_DICT = cfg.DATASET_DICT
REPORTING_FACILITY_DICT_TXT_FILES = cfg.REPORTING_FACILITY_DICT_TXT_FILES

if MANUAL_TEST:
    if FIRST_TIME_USER_TEST:
        print("First time user test")
        from finra_client import FinraClient
        # For the fist time use, specify a place and a name for the credentials and set the override parameter to True
        finra_client_instance = FinraClient(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                override_credentials=True,
                client_credential_path=CLIENT_CREDENTIAL_PATH,
                client_credential_file_name=CLIENT_CREDENTIAL_FILE_NAME
                )
        # the loaded and saved credentials have been automatically set as
        # attributes for the client instance, the client instance can therefore
        # be directly used to load data:
        # display the expiry
        # Credential expiry
        print(dt.datetime.fromtimestamp(finra_client_instance.credentials["expires_in"]).strftime("%Y-%m-%d %H:%M:%S"))
        # explore metadata of a dataset
        groupName = "fixedIncomeMarket"
        datasetName = "treasuryWeeklyAggregates" # daily blocked by authorization
        # Starting point: Request the metadata for a dataset to explore what (data-) fields are available
        metadata = finra_client_instance.get_dataset_metadata(groupName=groupName, datasetName=datasetName)
        print(f"Metadata for groupName: {groupName} and datasetName: {datasetName}: \n{metadata}")
    else:
        # Either directly use the finished specified client
        # from the finra_client.py file
        # or load the general class and set the needed credential relevant
        # settings here in the scripting file
        if USE_PREDEFINED_SETTING:
            # First variant
            from finra_client import finra_client
            finra_client_instance = finra_client
        else:
            # Second variant
            from finra_client import FinraClient
            finra_client_instance = FinraClient(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                client_credential_file_name=CLIENT_CREDENTIAL_FILE_NAME, # NEEDS TO BE PROVIDED
                client_credential_path=CLIENT_CREDENTIAL_PATH   # NEEDS TO BE PROVIDED
            )
        # What datasets are available
        # See the DATASET_DICT, for example pick a data group (i.e.) Fixed Income and pick a dataset name
        print(f"Available Groups:\n{DATASET_DICT.keys()}")
        # dict_keys(['Equity', 'FINRA Content', 'Firm', 'Fixed Income', 'Registration'])
        data_group = "Fixed Income"
        print(f"Available Datasets for the group: {data_group}\n{DATASET_DICT.get(data_group).get(list(DATASET_DICT.get(data_group).keys())[0])}")
        groupName = list(DATASET_DICT.get(data_group).keys())[0]
        datasetName = DATASET_DICT.get(data_group).get(groupName)[0]

        # Starting point: Request the metadata for a dataset to explore what (data-) fields are available
        metadata = finra_client_instance.get_dataset_metadata(groupName=groupName, datasetName=datasetName)
        print(f"Metadata for groupName: {groupName} and datasetName: {datasetName}\n{metadata}")
        # Next we can retrieve the available partitions for a dataset
        datasetName = "treasuryweeklyaggregates"
        partitions = finra_client_instance.get_dataset_partitions(groupName=groupName, datasetName=datasetName)
        print(f"Partitions for groupName: {groupName} and datasetName: {datasetName}\n{partitions}")
        # Next we want to request a specific dataset and add some filters but fitst we just want to load a basic dataset
        groupName = "fixedIncomeMarket"
        datasetName = "treasuryWeeklyAggregates" # daily blocked by authorization
        dataset = finra_client_instance.get_dataset(groupName=groupName, datasetName=datasetName)
        print(f"Data for groupName: {groupName} and datasetName: {datasetName}\n{pd.DataFrame.from_dict(dataset)}")
        datasetName = "treasuryDailyAggregates"
        dataset = finra_client_instance.get_dataset(groupName=groupName, datasetName=datasetName)

        # Next apply some filters for a dataset
        # How does one know what filters are available for a dataset?
        groupName = "otcMarket"
        datasetName = "regShoDaily"
        metadata = finra_client_instance.get_dataset_metadata(groupName=groupName, datasetName=datasetName)

        asset_category = "Equity"
        print(finra_client_instance.dataset_dict.get(asset_category))
        
        # The available Metadata shows the attributes (columns) that can be used for filtering
        ticker = "GOOG"
        fieldName = "securitiesInformationProcessorSymbolIdentifier"
        compareType = "equal"
        compareFilters = [{"compareType": compareType,
                        "fieldName": fieldName,
                        "fieldValue": ticker}]
        startDate = "2020-01-01" # YYYY-MM-DD
        endDate = "2023-05-10" # YYYY-MM-DD
        fieldName = "tradeReportDate"
        dateRangeFilters = [
            {"startDate": startDate,
            "endDate": endDate,
            "fieldName": fieldName
            }
            ]
        fieldName = "MarketCenter"
        values = ["A", "B", "C", "J"]
        domainFilters = [
            {"fieldName": fieldName,
            "values": values 
            }
        ]
        limit = 5000
        groupName = "otcMarket"
        datasetName = "regShoDaily"

        dataset = finra_client_instance.get_dataset(
            groupName=groupName,
            datasetName=datasetName,
            limit=limit,
            compareFilters=compareFilters,
            dateRangeFilters=dateRangeFilters
            )
        pd.DataFrame.from_dict(dataset)
        # Try to access paid data - not really a paid subscription needed, only valid credentials that can be obtained for free
        groupName = "fixedIncomeMarket"
        datasetName = "corporate144AMarketSentiment"

        dataset = finra_client_instance.get_dataset(
            groupName=groupName,
            datasetName=datasetName)
        pd.DataFrame.from_dict(dataset)
        # pd.DataFrame.from_dict(dataset).to_csv(f"data_{groupName}_{datasetName}.csv")

        # Additionally compare the data from the API with the daily .txt files
        # that can be viewed here: https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data/daily-short-sale-volume-files
        startDate = "2020-01-01" # YYYY-MM-DD
        endDate = "2025-03-10" # YYYY-MM-DD
        ReportingFacility = "FINRA Consolidated NMS"

        dataset_txt, error_list = finra_client_instance.get_single_txt_files(
                    startDate=startDate,
                    endDate=endDate,
                    ReportingFacility=ReportingFacility)
        # dataset_txt.to_csv("master_df_single_txt_files.csv")

        limit = 5000
        groupName = "otcMarket"
        datasetName = "regShoDaily"
        fieldName = "tradeReportDate"
        dateRangeFilters = [
            {"startDate": startDate,
            "endDate": endDate,
            "fieldName": fieldName
            }
            ]
        dataset = finra_client_instance.get_dataset(
            groupName=groupName,
            datasetName=datasetName,
            dateRangeFilters=dateRangeFilters
            )
        dataset = pd.DataFrame.from_dict(dataset)
