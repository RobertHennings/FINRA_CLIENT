CLIENT_ID = "8q74qbbfbfkar8o3q"
CLIENT_SECRET = "oiww-bkaarg38-fgiq73r"
PROJECT_PATH = r'path/to/FinraProject'
CLIENT_CREDENTIAL_PATH = PROJECT_PATH
CLIENT_CREDENTIAL_FILE_NAME = r'credentials.json'
BASE_URL = "https://api.finra.org"
OAUTH_URL = "https://ews.fip.finra.org/fip/rest/ews/oauth2/access_token"
REQUEST_TIMEOUT = 90
DATA_ENDPOINT = "/data"
METADATA_ENDPOINT = "/metadata"
PARTITIONS_ENDPOINT = "/partitions"
MOCK_DATA_ENDING = "MOCK"
USE_MOCK = False
HISTORIC_DATA_ENDING = "/HISTORIC"
REPORTING_FACILITY_DICT_TXT_FILES = {
    "FINRA Consolidated NMS": "CNMS",
    "FINRA/NASDAQ TRF Chicago": "FNQC",
    "ADF": "FNRA",
    "FINRA/NASDAQ TRF Carteret": "FNSQ",
    "FINRA/NYSE TRF": "FNYX",
    "ORF": "FORF",
}
ERROR_CODES_DICT = {
        400: {
            "message": "Bad request",
            "return_": None
        },
        401: {
            "message": "Failed to authenticate, check your authenticat…",
            "return_": None
        },
        410: {
            "message": "Unauthorized",
            "return_": None
        },
        403: {
            "message": "Forbidden",
            "return_": None
        },
        404: {
            "message": "Not Found",
            "return_": None
        },
        405: {
            "message": "Method not allowed",
            "return_": None
        },
        406: {
            "message": "Not acceptable",
            "return_": None
        },
        409: {
            "message": "Conflict",
            "return_": None
        },
        415: {
            "message": "Unsopprted Media Type",
            "return_": None
        },
        500: {
            "message": "Internal Server Error",
            "return_": None
        },
        502: {
            "message": "Bad Gateway",
            "return_": None
        },
        503: {
            "message": "Service Unavailable",
            "return_": None
        },
        504: {
            "message": "Gateway Timeout",
            "return_": None
        }
    }
SUCCESS_CODES_DICT = {
    200: {
        "message": "OK",
        "return_": "Success"
        },
    201: {
    "message": "Created",
    "return_": "Success"
    },
    204: {
        "message": "No content",
        "return_": "Success"
        }
}
DATASET_DICT = {
    "Equity": {
        "otcMarket": ["blocksSummary", "consolidatedShortInterest", "monthlySummary"
                      "otcBlocksSummary", "regShoDaily", "thresholdList", "weeklySummary",
                      ]
    },
    "FINRA Content": {
        "finra": ["finraRulebook", "industrySnapshotFirmsByRegistrationType"]
    },
    "Firm": {
        "firm": ["4530filings"]
    },
    "Fixed Income": {
        "fixedIncomeMarket": ["agencyMarketBreadth", "agencyMarketSentiment",
                              "corporate144AMarketBreadth", "corporate144AMarketSentiment",
                              "corporatesAndAgenciesCappedVolume", "corporateMarketBreadth",
                              "corporateMarketSentiment", "securitizedProductsCappedVolume",
                              "treasuryDailyAggregates", "treasuryDailyAggregates",
                              "treasuryMonthlyAggregates"]
    },
    "Registration": {
        "registration": ["accounting"]
    }
}
