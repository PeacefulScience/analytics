"""A simple example of how to access the Google Analytics API."""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import json
import numpy as np
import os

def get_service(api_name, api_version, scopes, key_dict):
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            key_dict, scopes=scopes)

    service = build(api_name, api_version, credentials=credentials)

    return service


def get_first_profile_id(service):
    return '125738398' 


def get_results(service, profile_id):
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


_redirects = {}

def load_redirects():
  for line in open("_redirects"):
    line = line.split()
    if len(line) == 2:
      u0 = normalize_url(line[0])
      u1 = normalize_url(line[1])
      _redirects[u0] = u1


def normalize_url(url):
  p = url.split("?")[0]
  p = p.split()[0]
  p = p.rstrip("/")
  p = _redirects.get(p, p)

  return p

load_redirects()

def clean_up_table(rows):
  R = []
  for r in rows:
    p = normalize_url(r[0])
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
