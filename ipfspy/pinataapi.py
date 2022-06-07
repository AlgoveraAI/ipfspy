# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03_pinataapi.ipynb (unless otherwise specified).

__all__ = ['upload_file', 'pin', 'unpin', 'edit_hash', 'pin_policy', 'globalpin_policy', 'get_pinned_jobs',
           'get_pinned_files', 'get_datausage']

# Cell
#hide

import requests
import json

# Cell
#upload file
def upload_file(cred:str,
                path:str,
                pinataMetadata=None):

    base_url = 'https://api.pinata.cloud/pinning/pinFileToIPFS'

    header = {'Authorization': f'Bearer {cred}',
             'Content Type':'multipart/form-data'}

    f_bytes = {'file':open(path,'rb')}

    response = requests.post(base_url, headers=header,files=f_bytes)

    return response,response.json()

# Cell
#pin ipfs cid
def pin(cred:str,
        cid:str,
        fn=None,
        pinataMetadata=None):

    base_url = 'https://api.pinata.cloud/pinning/pinByHash'

    header = {'Authorization': f'Bearer {cred}'}

    data = {
                # The 'pinataMetadata' object will not be part of your content added to IPFS
                # Pinata simply stores the metadata provided to help you easily query the content you've pinned with Pinata
                'pinataMetadata': {
                    'name': fn,
                    'keyvalues': {}
                },
                'hashToPin': cid,


        }



    response = requests.post(base_url, headers=header,json=data)

    return response,response.json()

# Cell
#unpin ipfs cid
def unpin(cred:str,
          cid:str):

    base_url = 'https://api.pinata.cloud/pinning/unpin/'

    header = {'Authorization': f'Bearer {cred}'}

    params = {'hashToUnpin':cid}

    response = requests.delete(base_url + cid,headers=header,params=params)

    return response,response.status_code

# Cell
#edit metadata of cid
def edit_hash(cred:str,
              cid:str,
              pinataMetaData=None
             ):

    base_url = 'https://api.pinata.cloud/pinning/hashMetadata'

    header = {'Authorization': f'Bearer {cred}'}

    data = pinataMetaData

    data['ipfsPinHash'] = cid

    response = requests.put(base_url, headers=header,json=data)

    return response,response.status_code

# Cell
#change pin policy of ipfs cid
def pin_policy(cred:str,
               cid:str,
               replications=int,
               region='NYC1',
                ):

    '''
    FRA1 - Frankfurt, Germany (max 2 replications)
    NYC1 - New York City, USA (max 2 replications)
    '''

    base_url = 'https://api.pinata.cloud/pinning/hashPinPolicy'

    header = {'Authorization': f'Bearer {cred}'}

    data = {'ipfsPinHash': cid,
            'newPinPolicy': {
                'regions':[{'id': region,'desiredReplicationCount': replications}]
            }
        }


    response = requests.put(base_url, headers=header,json=data)

    return response

# Cell
#set pin policy for all pins
def globalpin_policy(cred:str,
                     replications:int,
                     migratepins:bool,
                    region='NYC1'
                    ):

    '''
    FRA1 - Frankfurt, Germany (max 2 replications)
    NYC1 - New York City, USA (max 2 replications)
    '''

    base_url = 'https://api.pinata.cloud/pinning/userPinPolicy'

    header = {'Authorization': f'Bearer {cred}'}

    data = {
            'newPinPolicy': {
                'regions': [
                    {
                        'id': region,
                        'desiredReplicationCount': replications
                    },
                ],
                'migratePreviousPins':migratepins
            }
        }


    response = requests.put(base_url, headers=header,data=data)

    return response

# Cell
#list pinned jobs
def get_pinned_jobs(cred:str,
                    params=None):

    '''
    'sort' - Sort the results by the date added to the pinning queue (see value options below)
    'ASC' - Sort by ascending dates
    'DESC' - Sort by descending dates
    'status' - Filter by the status of the job in the pinning queue (see potential statuses below)
    'prechecking' - Pinata is running preliminary validations on your pin request.
    'searching' - Pinata is actively searching for your content on the IPFS network. This may take some time if your content is isolated.
    'retrieving' - Pinata has located your content and is now in the process of retrieving it.
    'expired' - Pinata wasn't able to find your content after a day of searching the IPFS network. Please make sure your content is hosted on the IPFS network before trying to pin again.
    'over_free_limit' - Pinning this object would put you over the free tier limit. Please add a credit card to continue pinning content.
    'over_max_size' - This object is too large of an item to pin. If you're seeing this, please contact us for a more custom solution.
    'invalid_object' - The object you're attempting to pin isn't readable by IPFS nodes. Please contact us if you receive this, as we'd like to better understand what you're attempting to pin.
    'bad_host_node' - You provided a host node that was either invalid or unreachable. Please make sure all provided host nodes are online and reachable.
    'ipfs_pin_hash' - Retrieve the record for a specific IPFS hash
    'limit' - Limit the amount of results returned per page of results (default is 5, and max is 1000)
    'offset' - Provide the record offset for records being returned. This is how you retrieve records on additional pages (default is 0)
    '''

    base_url = 'https://api.pinata.cloud/pinning/pinJobs/'

    header = {'Authorization': f'Bearer {cred}'}

    response = requests.get(base_url, headers=header,params=params)

    return response,response.json()

# Cell
#list pinned files
def get_pinned_files(cred:str,
                     params=None):

    '''
    Query Parameters = params

    hashContains: (string) - Filter on alphanumeric characters inside of pin hashes. Hashes which do not include the characters passed in will not be returned.
    pinStart: (must be in ISO_8601 format) - Exclude pin records that were pinned before the passed in 'pinStart' datetime.
    pinEnd: (must be in ISO_8601 format) - Exclude pin records that were pinned after the passed in 'pinEnd' datetime.
    unpinStart: (must be in ISO_8601 format) - Exclude pin records that were unpinned before the passed in 'unpinStart' datetime.
    unpinEnd: (must be in ISO_8601 format) - Exclude pin records that were unpinned after the passed in 'unpinEnd' datetime.
    pinSizeMin: (integer) - The minimum byte size that pin record you're looking for can have
    pinSizeMax: (integer) - The maximum byte size that pin record you're looking for can have
    status: (string) -
        * Pass in 'all' for both pinned and unpinned records
        * Pass in 'pinned' for just pinned records (hashes that are currently pinned)
        * Pass in 'unpinned' for just unpinned records (previous hashes that are no longer being pinned on pinata)
    pageLimit: (integer) - This sets the amount of records that will be returned per API response. (Max 1000)
    pageOffset: (integer) - This tells the API how far to offset the record responses. For example,
    if there's 30 records that match your query, and you passed in a pageLimit of 10, providing a pageOffset of 10 would return records 11-20.
    '''

    base_url = 'https://api.pinata.cloud/data/pinList?'

    header = {'Authorization': f'Bearer {cred}'}

    response = requests.get(base_url, headers=header,params=params)

    return response,response.json()

# Cell
#get data usage stats
def get_datausage(cred:str,params=None):

    header = {'Authorization': f'Bearer {cred}'}

    base_url = 'https://api.pinata.cloud/data/userPinnedDataTotal'

    response = requests.get(base_url, headers=header,params=params)

    return response,response.json()