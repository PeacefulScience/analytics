"""A simple example of how to access the Google Analytics API."""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import json
import numpy as np
import os

def get_service(api_name, api_version, scopes, key_dict):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            key_dict, scopes=scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=credentials)

    return service


def get_first_profile_id(service):
    # Use the Analytics service object to get the first profile id.

    # Get a list of all Google Analytics accounts for this user
    accounts = service.management().accounts().list().execute()

    if accounts.get('items'):
        # Get the first Google Analytics account.
        account = accounts.get('items')[0].get('id')

        # Get a list of all the properties for the first account.
        properties = service.management().webproperties().list(
                accountId=account).execute()

        if properties.get('items'):
            # Get the first property id.
            property = properties.get('items')[0].get('id')

            # Get a list of all views (profiles) for the first property.
            profiles = service.management().profiles().list(
                    accountId=account,
                    webPropertyId=property).execute()

            if profiles.get('items'):
                # return the first view (profile) id.
                return profiles.get('items')[0].get('id')

    return None


def get_results(service, profile_id):
    # Use the Analytics Service Object to query the Core Reporting API
    # for the number of sessions within the past seven days.
    
    params = {
      "ids":'ga:' + profile_id,
      "start_date": '7daysAgo',
      "end_date": 'today',
      "dimensions":"ga:pagePath",
      "filters": "ga:hostname==peacefulscience.org",
      "metrics":'ga:pageviews,ga:sessions',
      "sort": "ga:pagePath"
    }
    
    R1 = get_all_rows(service, params)
    
    params["start_date"] = '2015-01-01'
    
    R2 = get_all_rows(service, params)

    return R1, R2



def get_all_rows(service, params):
    rows = []
    params = dict(params)
    params["start_index"] = -999
    params["max_results"] = 1000
    R = {"nextLink": None}
    
    while "nextLink" in R:
      
      params["start_index"] += 1000
      
      R = service.data().ga().get(**params).execute()
      rows += R['rows']     
      
    return rows
       
import itertools
import functools

def clean_up_table(rows):
  R = []
  for r in rows:
    p = r[0].split("?")[0]
    p = p.split(" ")[0]
    p = p.rstrip("/")
    if not p: continue
    
    R.append((p, np.array([int(x) for x in r[1:]])))
      
 
  R.sort(key=lambda x: x[0])
 
  D = []
  for k, g in itertools.groupby(R, key=lambda x: x[0]):
    S = functools.reduce(lambda x,y: (x[0], x[1] + y[1]), g)
    D.append( [k] + [int(i) for i in S[1]] )
    
  D.sort(key=lambda x: -x[1])
 
  return D
 

def print_results(results):
    # Print data nicely for the user.
    if results:
        print ('Results:', results.get('rows'))

    else:
        print ('No results found')


def main():
    # Define the auth scopes to request.
    scope = 'https://www.googleapis.com/auth/analytics.readonly'
    key_file_location = 'client_secrets.json'
    
    
    try:
      key_dict = json.load(open(key_file_location))
    except: 
      key_dict = json.loads(os.environ['GA_SERVICE'])

    
    # Authenticate and construct service.
    service = get_service(
            api_name='analytics',
            api_version='v3',
            scopes=[scope],
            key_dict=key_dict)

    profile_id = get_first_profile_id(service)
    R = get_results(service, profile_id)
    
    json.dump(clean_up_table(R[0]), open("trending.json", 'w'), indent=1)
    json.dump(clean_up_table(R[1]), open("mostread.json", 'w'), indent=1)


if __name__ == '__main__':
    R = main()
