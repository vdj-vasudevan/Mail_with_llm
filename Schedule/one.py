import requests
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import ct_to_one_fmt 

HEADERS_TEMPLATE = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://ecomm.one-line.com/',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
}

def get_one_schedule(origin, destination, from_date=None, to_date=None):
    current_date = datetime.now()
    ct_tm = ct_to_one_fmt()

    from_date = from_date or current_date.strftime('%Y-%m-%d')
    to_date = to_date or (current_date + timedelta(weeks=2)).strftime('%Y-%m-%d')

    por_code_list = get_one_port_code_with_name(origin)
    del_code_list = get_one_port_code_with_name(destination)
    if not por_code_list or not del_code_list:
        return None
    try:
      por_code = [i["code"]for i in por_code_list["points"]if origin.lower() in i["name"].lower() and i["termCd"]=="Y"][0]
      del_code = [i["code"]for i in del_code_list["points"]if destination.lower() in i["name"].lower()and i["termCd"]=="Y"][0]
    except IndexError:
      return None
    url = (
        f"https://ecomm.one-line.com/api/v1/schedule/point-to-point?"
        f"porCode={por_code}&delCode={del_code}&rcvTermCode=Y&deTermCode=Y"
        f"&tsFlag=&fromDate={from_date}&toDate={to_date}"
        f"&polCode=&podCode=&cargoNature=GP&searchType=List"
    )

    headers = {**HEADERS_TEMPLATE, 'request-date': ct_tm}
    response = requests.get(url, headers=headers)
    
    return response.json()

def get_one_port_code_with_name(port_name):
    """Fetches port code for a given port name."""
    url = f"https://ecomm.one-line.com/api/v1/schedule/point-to-point/search?pointName={port_name}&sortType=origin"
    headers = {**HEADERS_TEMPLATE, 'request-date': ct_to_one_fmt()}

    response = requests.get(url, headers=headers)
    
    return response.json()

# Example Usage:
# print(get_one_schedule("Hamburg", "Shanghai"))
