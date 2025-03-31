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

if MANUAL_TEST:
    from finra_client import finra_client
    finra_client_instance = finra_client

    data_group = "Fixed Income"
    groupName = list(finra_client_instance.dataset_dict.get(data_group).keys())[0]
    datasetName = finra_client_instance.dataset_dict.get(data_group).get(groupName)[0]

    # Starting point: Request the metadata for a dataset to explore what (data-) fields are available
    metadata = finra_client_instance.get_dataset_metadata(groupName=groupName, datasetName=datasetName)
    print(f"Metadata for groupName: {groupName} and datasetName: {datasetName}\n{metadata}")