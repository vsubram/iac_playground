import datetime
import os
import sys
import requests
from requests.exceptions import HTTPError

from project_variables import QUERY_URL, LIMIT_RESULTS_PER_PAGE, LOCATION_NAME, JOB_POSITION_KEYWORD
from etl import extract_date
import requests

params = {
    "ResultsPerPage": LIMIT_RESULTS_PER_PAGE,
    "LocationName": LOCATION_NAME,
    "Keyword": JOB_POSITION_KEYWORD
}

headers = {
    "Host": "data.usajobs.gov",
    "User-Agent": os.environ.get("USA_JOBS_API_USER_AGENT"),
    "Authorization-Key": os.environ.get("USA_JOBS_API_KEY")
}


def api_results()-> list[tuple]:
    
    """
    Capture the results from the USA Jobs API Keywords Responses

    :return: list(tuple) List of tuples with records to be inserted to the database
    """

    rows_to_be_inserted: list[tuple] = []

    try:
        response = api_call(query=QUERY_URL, params=params)

        response_json = response["SearchResult"]["SearchResultItems"]
        
        page_count = int(
            response["SearchResult"]["UserArea"]["NumberOfPages"]
        )

        rows_to_be_inserted = create_record(response_json=response_json, params=params)

        for page in range(2, page_count + 1):
                    params["Page"] = page

                    page_json_response = api_call(QUERY_URL, params=params)
                    
                    if page_json_response:
                        page_content_json = page_json_response["SearchResult"][
                            "SearchResultItems"
                        ]
                        
                        # Add the current page job postings
                        rows_to_be_inserted += create_record(response_json=page_content_json, params=params)


    except IndexError:
        print("Index error probably observed in Location or Remuneration")

    return rows_to_be_inserted


def create_record(response_json: dict, params: dict)-> list[tuple]:
    
    """
    Read the USA Job API Response's Dictionary values and extract the indivdual fields

    :param response_json dict: USA Job API Response's Dictionary values
    :param params dict: Parameters to be sent with the API request, which I'd like to capture in my dataset for analysis
    :return: list[tuple] Records ready to be inseretd into Postgres DB
    """

    values: list[tuple] = []

    # Iterate over each item in the dictionary
    for item in response_json:
            
            descriptor = item.get("MatchedObjectDescriptor")

            _id = item.get("MatchedObjectId")   # Unique Identifier Value
            _title = str(descriptor.get('PositionTitle'))
            _publishDate = extract_date(descriptor.get("PositionStartDate"))
            _orgName = descriptor.get("OrganizationName")
            _jobUrl = descriptor.get('PositionURI')
            
            # Extracting location
            _locationType = descriptor.get('PositionLocationDisplay')
            location_name = descriptor.get('PositionLocation')[0]
            _cityLocation = location_name.get("LocationName")
            
            _inMultipleLocations = extract_chicago_loaction(descriptor.get('PositionLocation'))

            # Extracting Salary Range
            remuneration = descriptor.get("PositionRemuneration")[0]
            _minSalaryRange = remuneration.get("MinimumRange")
            _maxSalaryRange = remuneration.get("MaximumRange")

            # Capturing user search parameters
            _recordCreationDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _searchParameters = f"Keyword: {params.get('Keyword')}, Location: {params.get('LocationName')}" # Unique Identifier Value

            values.append(
                (
                    _id,
                    _title,
                    _publishDate,
                    _orgName,
                    _locationType,
                    _cityLocation,
                    _inMultipleLocations,
                    _jobUrl,
                    _minSalaryRange,
                    _maxSalaryRange,
                    _recordCreationDate,
                    _searchParameters,
                    os.environ.get('USER')
                )
            )

    return values


def extract_chicago_loaction(multiple_locations)-> bool:
    
    """
    Extract the list of dictionaries to identify if the city of Chicago is aavailable as a part of the position

    :param multiple_locations list(dict): List of Dictionary Key Value pair for a Job Position, if the the job is displayed in multiple positions
    :return: bool Boolean value returned to be inserted into the table
    """
    
    city_to_check = 'Chicago, Illinois'
    
    list_of_bool = [True for location in multiple_locations
                if city_to_check in location.values()]

    _isInChicagoLocation: bool = False
    
    if any(list_of_bool):
        _isInChicagoLocation = True

    return _isInChicagoLocation


def api_call(query: str, params=None) -> dict:
    """
    Sends a GET request to the API with the provided parameters.
    Checks if the API is running properly.

    :param query str: Base query URL
    :param params dict: Parameters to be sent with the API request
    :return: dict from the JSON-response
    """

    try:
        response = requests.request("GET", query, params=params, headers=headers)

        if (
            response
            and response.status_code == 200
            and "application/hr+json" in response.headers.get("content-type")
        ):
            return response.json()
        else:
            sys.exit("Invalid API, non-JSON response. ")

    except HTTPError as http_err:
        print(f"HTTP Error: {http_err}")
    except Exception as err:
        print(f"Error: {err}")