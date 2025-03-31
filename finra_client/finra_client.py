from typing import Dict, List
import os
import json
import datetime as dt
import base64
import requests
import pandas as pd

import config as cfg
# from . import config as cfg
# Set the static global variables
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

class FinraClient(object):
    def __init__(
            self,
            client_id: str=CLIENT_ID,
            client_secret: str=CLIENT_SECRET,
            override_credentials: bool=False,
            client_credential_path: str=None,
            client_credential_file_name: str=None,
            base_url: str=BASE_URL,
            oauth_url: str=OAUTH_URL,
            request_timeout: int=REQUEST_TIMEOUT,
            data_endpoint: str=DATA_ENDPOINT,
            metadata_endpoint: str=METADATA_ENDPOINT,
            partitions_endpoint: str=PARTITIONS_ENDPOINT,
            mock_data_ending: str=MOCK_DATA_ENDING,
            use_mock: str=USE_MOCK,
            historic_data_ending: str=HISTORIC_DATA_ENDING,
            error_codes_dict: Dict[int, Dict[str, str]]=ERROR_CODES_DICT,
            success_codes_dict: Dict[int, Dict[str, str]]=SUCCESS_CODES_DICT,
            dataset_dict:Dict[str, Dict[str, List[str]]]=DATASET_DICT,
            reporting_facility_dict_txt_files: Dict[str, str]=REPORTING_FACILITY_DICT_TXT_FILES,
            proxies: Dict[str, str]=None,
            verify: bool=None
            ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.override_credentials = override_credentials
        self.client_credential_path = client_credential_path
        self.client_credential_file_name = client_credential_file_name
        self.base_url=base_url
        self.oauth_url = oauth_url
        self.request_timeout = request_timeout
        self.data_endpoint = data_endpoint
        self.metadata_endpoint = metadata_endpoint
        self.partitions_endpoint = partitions_endpoint
        self.mock_data_ending = mock_data_ending
        self.use_mock = use_mock
        self.historic_data_ending = historic_data_ending
        self.error_codes_dict = error_codes_dict
        self.success_codes_dict = success_codes_dict
        self.dataset_dict = dataset_dict
        self.reporting_facility_dict_txt_files = reporting_facility_dict_txt_files
        self.proxies = proxies
        self.verify = verify
        if self.client_credential_path is not None and self.client_credential_file_name is not None:
            self.__check_path_existence(path=client_credential_path)
            # if client_credential_path and client_credential_file_name provided but it should be replaced
            if self.override_credentials:
                self.get_new_finra_credentials(
                    client_credential_file_name=self.client_credential_file_name,
                    client_credential_path=self.client_credential_path,
                    save_credentials=True
                    ) # obtain initial finra credentials and save in file

            # Check if credentials file is existend at provided location
            elif self.client_credential_file_name in os.listdir(self.client_credential_path):
                self.credentials = self.load_credentials()
            else:
                raise FileExistsError(f"{self.client_credential_file_name} not existend in location: {self.client_credential_path}")
        else:
            raise Exception(f"Provide arguments for loading the credentials, client_credential_file_name: {self.client_credential_file_name}\nclient_credential_path{self.client_credential_path}")

    def __resilient_request(
            self,
            response: requests.models.Response,
            ):
        """Internal helper method - serves as generous requests
           checker using the custom defined error and sucess code dicts
           for general runtime robustness

        Args:
            response (requests.models.Response): generous API response

        Raises:
            Exception: _description_

        """
        status_code = response.status_code
        response_url = response.url
        status_code_message = [
            dict_.get(status_code).get("message")
            for dict_ in [self.error_codes_dict, self.success_codes_dict]
            if status_code in dict_.keys()]
        # If status code is not present in the defined dicts
        if status_code_message == []:
            print(f"Status code: {status_code} not defined")
        else: # if status code is definded in the dicts
            # get the defined message for the status code
            status_code_message = f"{"".join(status_code_message)} for URL: {response_url}"
            # get the defined return (type) for the status code
            status_code_return = [
                dict_.get(status_code).get("return_")
                for dict_ in [self.error_codes_dict, self.success_codes_dict]
                if status_code in dict_.keys()]

            if status_code_return is not None:
                print(status_code_message)
            else:
                raise Exception("Error")


    def __check_path_existence(
        self,
        path: str
        ):
        """Internal helper method - serves as generous path existence
           checker when saving and reading of an kind of data from files
           suspected at the given location
           
           !!!!If given path does not exist it will be created!!!!

        Args:
            path (str): full path where expected data is saved
        """
        folder_name = path.split("/")[-1]
        path = "/".join(path.split("/")[:-1])
        # FileNotFoundError()
        # os.path.isdir()
        if folder_name not in os.listdir(path):
            print(f"{folder_name} not found in path: {path}")
            folder_path = f"{path}/{folder_name}"
            os.mkdir(folder_path)
            print(f"Folder: {folder_name} created in path: {path}")

    ########### credential and authorization related methods ###########
    def get_new_finra_credentials(
            self,
            client_credential_file_name: str,
            url: str=OAUTH_URL,
            save_credentials: bool=False,
            request_timeout: int=REQUEST_TIMEOUT,
            **kwargs
            ) -> Dict[str, str]:

        self.client_credential_file_name = client_credential_file_name

        base_string = f'{self.client_id}:{self.client_secret}'.encode(encoding="UTF-8")
        encoded_base_string = base64.b64encode(base_string)
        encoded_base_string = str(encoded_base_string).split("b")[1].replace("'", "")
        params = {
            "grant_type": "client_credentials"
        }
        headers = {
            "Authorization": f"Basic {encoded_base_string}"
        }
        response = requests.post(
            url=url,
            params=params,
            headers=headers,
            timeout=request_timeout,
            proxies=self.proxies,
            verify=self.verify)
        self.__resilient_request(response=response)
        # credentials = response.json()
        # access_token = credentials.get("access_token")
        credentials = None
        if response.status_code == 200:
            # Save json response as a variable
            credentials = response.json()
            # Manipulate the expiry parameter
            now = dt.datetime.now()
            expiry_seconds = credentials.get("expires_in")
            expiry_date = now + pd.offsets.Second(n=int(expiry_seconds))
            credentials["expires_in"] = expiry_date.timestamp()
            self.credentials = credentials # directly set the credentials to the active instance
            if save_credentials:
                # Save credentials to file
                client_credential_path = ""
                if kwargs:
                    client_credential_path = kwargs.get("client_credential_path")
                    # directly set the given path to the active instance
                    self.client_credential_path = client_credential_path
                    self.__check_path_existence(path=client_credential_path)
                    credentials_full_save_path = rf'{client_credential_path}/{client_credential_file_name}'
                else:
                    credentials_full_save_path = rf'{client_credential_file_name}'
                if credentials is not None:
                    with open(credentials_full_save_path, 'w', encoding="utf-8") as outfile:
                        json.dump(credentials, outfile)
                    print(f"Strava credentials saved at: {credentials_full_save_path}")
        else:
            raise Exception(f"Failed to load new credentials, strava_tokens: {credentials}")
        return credentials


    def refresh_credentials(
                  self,
                  credentials: Dict[str, str],
                  url: str=OAUTH_URL,
                  save_credentials: bool=True,
                  request_timeout: int=REQUEST_TIMEOUT
                  ) -> Dict[str, str]:
        expiry_timestamp = credentials.get("expires_in")
        if dt.datetime.now() > dt.datetime.fromtimestamp(expiry_timestamp):
            # a new access token must be retrived using the old ones refresh token
            print("Refreshing access token")
            credentials = self.get_new_finra_credentials(
                client_credential_file_name=self.client_credential_file_name,
                url=url,
                save_credentials=save_credentials,
                request_timeout=request_timeout,
                client_credential_path=self.client_credential_path
                )

            if save_credentials:
                # Save credentials to file
                client_credential_path = ""
                if self.client_credential_path:
                    client_credential_path = self.client_credential_path
                    self.__check_path_existence(path=client_credential_path)
                    credentials_full_save_path = rf'{client_credential_path}/{self.client_credential_file_name}'
                else:
                    credentials_full_save_path = rf'{self.client_credential_file_name}'
                if credentials is not None:
                    with open(credentials_full_save_path, 'w', encoding="utf-8") as outfile:
                        json.dump(credentials, outfile)
                    print(f"Strava credentials saved at: {credentials_full_save_path}")
            return credentials
        else:
            return credentials


    def load_credentials(
              self
              ):
        # First check if a secrets file is already present at the provided path
        if self.client_credential_file_name is not None and self.client_credential_path is not None:
            self.__check_path_existence(path=self.client_credential_path)
            if self.client_credential_file_name in os.listdir(self.client_credential_path):
                file_path_full = f"{self.client_credential_path}/{self.client_credential_file_name}"
                with open(file_path_full) as json_file:
                    credentials = json.load(json_file)
                return credentials
            else:
                raise KeyError(f"{self.client_credential_file_name} not found in path: {self.client_credential_path}")
        else:
            print("No credentials provided, obtaining initial credentials")
            credentials = self.get_new_finra_credentials(
                client_credential_file_name=self.client_credential_file_name,
                client_credential_path=self.client_credential_path
                )
            print(credentials)
            return credentials
    ########### API ENDPOINT INTERACTION ###########
    # Starting point: Request the metadata for a dataset to explore what (data-) fields are available
    def get_dataset_metadata(
            self,
            groupName: str,
            datasetName: str
            ) -> str:
        # get the access token from the credentials and check if they are still valid
        credentials = self.refresh_credentials(credentials=self.credentials)
        access_token = credentials["access_token"]

        if self.use_mock:
            datasetName = f"{datasetName}{self.mock_data_ending}"
        # Build the URL
        url = f"{self.base_url}{self.metadata_endpoint}/group/{groupName}/name/{datasetName}"
        headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}"
                }
        response = requests.get(url=url, headers=headers, timeout=self.request_timeout)
        self.__resilient_request(response=response)
        if response.status_code == 200:
            # Convert bytes to string
            data_str = response.content.decode('utf-8')
            data_dict = json.loads(data_str)
            return data_dict


    def get_dataset_partitions(
        self,
        groupName: str,
        datasetName: str
        ) -> str:
        # get the access token from the credentials and check if they are still valid
        credentials = self.refresh_credentials(credentials=self.credentials)
        access_token = credentials["access_token"]

        if self.use_mock:
            datasetName = f"{datasetName}{self.mock_data_ending}"
        # Build the URL
        url = f"{self.base_url}{self.partitions_endpoint}/group/{groupName}/name/{datasetName}"
        headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}"
                }
        response = requests.get(url=url, headers=headers, timeout=self.request_timeout)
        self.__resilient_request(response=response)
        if response.status_code == 200:
            # Convert bytes to string
            data_str = response.content.decode('utf-8')
            data_dict = json.loads(data_str)
            return data_dict


    def get_dataset(
        self,
        groupName: str,
        datasetName: str,
        fields: List[str]=None,
        limit: int=1000,
        offset: int=0,
        delimiter: str=",",
        quoteValues: str="true",
        async_: str="false",
        sortFields: List[str]=None,
        compareFilters: List[Dict[str, str]]=None,
        dateRangeFilters: List[Dict[str, str]]=None,
        domainFilters: List[Dict[str, str]]=None,
        ) -> str:
        # get the access token from the credentials and check if they are still valid
        credentials = self.refresh_credentials(credentials=self.credentials)
        access_token = credentials["access_token"]

        if self.use_mock:
            datasetName = f"{datasetName}{self.mock_data_ending}"
        # Build the URL
        url = f"{self.base_url}{self.data_endpoint}/group/{groupName}/name/{datasetName.lower()}"
        headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}"
                }
        request_payload = {
            "limit": limit,
            "offset": offset,
            "delimiter": delimiter,
            "async": async_,
            "quoteValues": quoteValues,
            # "fields": fields,
            # "sortFields": sortFields,
            # "compareFilters": compareFilters,
            # "dateRangeFilters": dateRangeFilters,
            # "domainFilters": domainFilters
        }
        # Add several parameters if they are not None
        none_default_dicts = [fields, sortFields, compareFilters, dateRangeFilters, domainFilters]
        for none_default_dict in none_default_dicts:
            if none_default_dict is not None:
                request_payload[str(none_default_dict)] = none_default_dict

        response = requests.post(url=url, headers=headers, json=request_payload, timeout=self.request_timeout)
        self.__resilient_request(response=response)
        if response.status_code == 200:
            # Convert bytes to string
            data_str = response.content.decode('utf-8')
            data_dict = json.loads(data_str)
            return data_dict


    def get_single_txt_files(
            self,
            startDate: str,
            endDate: str,
            ReportingFacility: str,
            groupName: str="equity",
            datasetName: str="regsho",
            url: str="https://cdn.finra.org/",
            save_local: bool=False,
            save_path: str=None,
            override_files: bool=False
            )-> pd.DataFrame:
        """Scrapes single .txt file from the Finra website and appends the single days to a msterdataframe
        that will be returned, optional saves the single files at the specified path
        The single .txt files can be viewed: https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data/daily-short-sale-volume-files
        """
        # get the access token from the credentials and check if they are still valid
        credentials = self.refresh_credentials(credentials=self.credentials)
        access_token = credentials["access_token"]
        if save_local:
            self.__check_path_existence(path=save_path)
        # create daterange for the start and end date
        date_range = pd.date_range(start=startDate, end=endDate, freq="B")
        ReportingFacility = self.reporting_facility_dict_txt_files.get(ReportingFacility)
        # Build the URL list
        url_list = [f"{url}{groupName}/{datasetName}/daily/{ReportingFacility}shvol{date.strftime("%Y%m%d")}.txt" for date in date_range]

        df_master = pd.DataFrame()
        error_list = []
        counter = 0
        for index_ in range(len(url_list)):
            url_df = pd.DataFrame()
            counter +=1

            date = date_range[index_]
            url_ = url_list[index_]
            try:
                print(f"Loading data for day: {date.strftime('%Y%m%d')}, progress: {round((counter/len(date_range)) * 100, 2)}%")
                response = requests.get(url=url_, timeout=self.request_timeout)
                self.__resilient_request(response=response)
                if response.status_code == 200:
                    response_txt = response.text
                    # Transfrom the response content to a string and remove leading bytes indicator
                    end_symbol = "\r\n"
                    column_end_index = response_txt.find(end_symbol)
                    column_list = response_txt[:column_end_index].split("|")
                    response_txt = response_txt[column_end_index+len(end_symbol):]
                    # split the data unto the single lines
                    lines_list = response_txt.split("\r\n")
                    # parse each individual line
                    parsed_lines_list = [line.split("|") for line in lines_list if "|" in line]
                    url_df = pd.DataFrame(data=parsed_lines_list, columns=column_list)
                    df_master = pd.concat([df_master, url_df], axis=0)

                    if save_local:
                        if override_files:
                            print(f"Saving file locally: {date.strftime('%Y%m%d')}.csv")
                            url_df.to_csv(save_path + "//" + date.strftime('%Y%m%d') + ".csv")
                        else:
                            if date.strftime('%Y%m%d') + ".csv" not in os.listdir(save_path):
                                url_df.to_csv(save_path + "//" + date.strftime('%Y%m%d') + ".csv")

                print(f"Finished loading and parsing data for day: {date.strftime('%Y%m%d')}")

            except:
                print(f"No txt file available for day or error at: {date.strftime('%Y%m%d')}")
                error_list.append(url_)

        print("Finished Data Loading")
        # Manipualate the index and transform it
        df_master = df_master.reset_index(drop=True)
        df_master["Date"] = df_master["Date"].str[:4] + "-" + df_master["Date"].str[4:6] + "-" + df_master["Date"].str[6:]
        df_master["Date"] = pd.to_datetime(df_master["Date"])
        return df_master, error_list

finra_client = FinraClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_credential_path=CLIENT_CREDENTIAL_PATH,
    client_credential_file_name=CLIENT_CREDENTIAL_FILE_NAME
    )
