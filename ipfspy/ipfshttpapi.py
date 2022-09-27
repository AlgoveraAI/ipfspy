# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_ipfshttpapi.ipynb.

# %% auto 0
__all__ = ['IPFSApi', 'DownloadDir']

# %% ../nbs/01_ipfshttpapi.ipynb 4
from typing import Union, List

import requests
import json
from fastcore.all import *
import pandas as pd
import dag_cbor
from requests.exceptions import HTTPError
import time

from .utils import parse_error_message, parse_response, IPFSGateway, GATEWAY_MAP, make_infura_auth

from ipfshttpclient.multipart import stream_files, stream_directory

# %% ../nbs/01_ipfshttpapi.ipynb 5
class IPFSApi():
    def __init__(self,
        gateway_type='local', # Gateway to use - `public`, `infura`, `local` 
        timeout=10, # 
        **kwargs
    ):
        
        self.gateway = None
        self._gateways = None

        self.change_gateway_type = gateway_type, None
        self.timeout = timeout
        self.full_structure = None
    
    @property
    def change_gateway_type(self):
        return self.gateway_type, None

    @change_gateway_type.setter    
    def change_gateway_type(self, 
        value, 
        ):
        self.gateway_type = value[0]
        self._gateways = [IPFSGateway(g) for g in GATEWAY_MAP[self.gateway_type]] 
        if self.gateway_type == 'infura':
            self._gateways[0].auth = value[1]
        print(f"Changed to {self.gateway_type} node")
    
    def _find_gateway(self):
        backoff_list = []
        for gw in self._gateways:
            state, wait_time = gw.get_state()
            if state == "online":
                return gw, 0
            if state == "backoff":
                backoff_list.append((wait_time, gw))
        if len(backoff_list) > 0:
            return sorted(backoff_list)[0][::-1]
        else:
            raise RuntimeError("no working gateways could be found")

    def _run_on_any_gateway(self, f):
        timeout = time.monotonic() + self.timeout
        while time.monotonic() <= timeout:
            gw, wait_time = self._find_gateway()
            if wait_time > 0:
                time.sleep(wait_time)
            res = f(gw)
            if res is not None:
                break
        return res
        
    def _gw_get(self, path):
        return self._run_on_any_gateway(lambda gw: gw.get(path))

    def _gw_head(self, path, headers=None):
        return self._run_on_any_gateway(lambda gw: gw.head(path, headers))

    def _gw_apipost(self, call, **kwargs): 
        return self._run_on_any_gateway(lambda gw: gw.apipost(call, **kwargs))
    
    def add_items(self,
        filepath:Union[str, List[str]], # Path to the file/directory to be added to IPFS
        directory:bool=False, # Is filepath a directory
        wrap_with_directory:bool=False, # True if path is a directory
        chunker:str='size-262144', # Chunking algorithm, size-[bytes], rabin-[min]-[avg]-[max] or buzhash
        pin:bool=True, # Pin this object when adding
        hash_:str='sha2-256', # Hash function to use. Implies CIDv1 if not sha2-256
        progress:str='true', # Stream progress data
        silent:str='false', # Write no output
        cid_version:int=0, # CID version
        **kwargs,
        ):
        "add file/directory to ipfs"

        params = {}
        params['wrap-with-directory'] = 'true' if wrap_with_directory else 'false'
        params['chunker'] = chunker
        params['pin'] = 'true' if pin else 'false'
        params['hash'] = hash_
        params['progress'] = progress
        params['silent'] = silent
        params['cid-version'] = cid_version
        params.update(kwargs)
        
        chunk_size = int(chunker.split('-')[1])

        if not directory:
            data, headers = stream_files(filepath, chunk_size=chunk_size)

        else:
            data, headers = stream_directory(filepath, chunk_size=chunk_size, recursive=True)

        response = self._gw_apipost('add', 
                                    params=params, 
                                    data=data,
                                    headers=headers)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def ls_items(self,
        cid:str, # The path to the IPFS object(s) to list links from
        resolve_type:bool=True, # Resolve linked objects to find out their types
        size:bool=True, # Resolve linked objects to find out their file size
        **kwargs,
    ):
        'List directory contents for Unix filesystem objects'

        params = {}
        params['arg'] = cid
        params['resolve-type'] = 'true' if resolve_type else 'false'
        params['size'] = 'true' if size else 'false'
        params.update(kwargs)

        response = self._gw_apipost('ls', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def get_items(self,
        cid:str, # The path to the IPFS object(s) to be outputted
        output:str='', # The path where the output should be stored
        **kwargs
    ):
        'Download IPFS objects'

        params = {}
        params['arg'] = cid
        params['output'] = output
        params.update(kwargs)

        response = self._gw_apipost('get', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def cat_items(self,
        cid:str, # The path to the IPFS object(s) to be output
        **kwargs
    ):
        'Show IPFS object data'

        params = {}
        params['arg'] = cid
        params.update(kwargs)

        response = self._gw_apipost('cat', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))
    
    def dag_export(self,
        cid:str, #The path to the IPFS DAG node
        **kwargs,
    ):
        'Streams the selected DAG as a .car stream on stdout.'

        params = {}
        params['arg'] = cid
        params.update(kwargs)

        response = self._gw_apipost('dag/export', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def dag_get(self,
        cid:str, #The path to the IPFS DAG node
        output_codec:str='dag-json',
    ):
        'Get a DAG node from IPFS.'

        params = {}
        params['arg'] = cid
        params['output-codec'] = output_codec

        response = self._gw_apipost('dag/get', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def dag_stat(self,
        cid:str, #The path to the IPFS DAG node 
        **kwargs, 
    ):
        'Gets stats for a DAG.'

        params = {}
        params['arg'] = cid
        params.update(kwargs)

        response = self._gw_apipost('dag/stat', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))
    
    def pin_add(self,
        cid:str, # Path to IPFS object(s) to be pinned
        recursive:str='true', # Recursively pin the object linked to by the specified object(s)
    ):
        'Pin objects to local storage.'

        params = {}
        params['arg'] = cid
        params['recursive'] = recursive

        response = self._gw_apipost('pin/add', params=params)
        
        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def pin_ls(self,
        type_:str='all', # The type of pinned keys to list. Can be "direct", "indirect", "recursive", or "all"
        **kwargs,
    ):
        'List objects pinned to local storage.'    

        params = {}
        params['type'] = type_
        params.update(kwargs)

        response = self._gw_apipost('pin/ls', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def pin_rm(self,
        cid:str, # Path to object(s) to be unpinned
        recursive:str='true', #  Recursively unpin the object linked to by the specified object(s)
        **kwargs,
    ):
        'List objects pinned to local storage.'    

        params = {}
        params['arg'] = cid
        params['recursive'] = recursive
        params.update(kwargs)

        response = self._gw_apipost('pin/rm', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def rspin_add(self,
        service_name:str, # Name of the remote pinning service to use
        service_edpt:str, # Service endpoint
        service_key:str, # Service key
    ):
        'Pin object to remote pinning service.'

        params = {}
        params['arg'] = [service_name, service_edpt, service_key]

        response = self._gw_apipost('pin/remote/service/add', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def rspin_ls(self,
        **kwargs
    ):
        'List remote pinning services.'

        params = {}
        params.update(kwargs)

        response = self._gw_apipost('pin/remote/service/ls', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))


    def rspin_rm(self,
        service_name:str, # Name of pinning service to remove
    ):
        'Remove remote pinning service.'

        params = {}
        params['arg'] = service_name

        response = self._gw_apipost('pin/remote/service/rm', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))
    
    def rpin_add(self,
        cid:str, #  Path to IPFS object(s) to be pinned
        service:str, # Name of the remote pinning service to use
        background:str='false', # Add to the queue on the remote service and return immediately (does not wait for pinned status)
        **kwargs,
    ):
        'Pin object to remote pinning service.'

        params = {}
        params['arg'] = cid
        params['service'] = service
        params['background'] = background
        params.update(kwargs)

        response = self._gw_apipost('pin/remote/add', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))


    def rpin_ls(self,
        service:str, # Name of the remote pinning service to use
        **kwargs, 
    ):
        'List objects pinned to remote pinning service.'

        params = {}
        params['service'] = service
        params.update(kwargs)

        response = self._gw_apipost('pin/remote/ls', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def rpin_rm(self,
        service:str, # Name of the remote pinning service to use
        **kwargs, 
    ):
        'Remove pins from remote pinning service.'    

        params = {}
        params['service'] = service
        params.update(kwargs)

        response = self._gw_apipost('pin/remote/rm', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))
            
    def block_get(self,
        cid:str, # The base58 multihash of an existing block to get

    ):
        'Get a raw IPFS block.'

        params = {}
        params['arg'] = cid

        response = self._gw_apipost('block/get', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def block_put(self,
        filepath:str, # Path to file
        mhtype:str='sha2-256', # multihash hash function.
        mhlen:int=-1, # Multihash hash length
        pin:str=False, #  pin added blocks recursively
        **kwargs,
    ):
        'Store input as an IPFS block.'

        params = {}
        params['mhtype'] = mhtype
        params['mhlen'] = mhlen
        params['pin'] = 'true' if pin else 'false'
        params.update(kwargs)

        response = self._gw_apipost('block/put', params=params, files={'files':open(filepath, 'rb')})

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))
            
    def block_rm(self,
        cid:str, # Bash58 encoded multihash of block(s) to remove
        force:str='false', # Ignore nonexistent blocks.
        quiet:str='false', # Write minimal output.
    ):
        'Remove IPFS block(s).'

        params = {}
        params['arg'] = cid
        params['force'] = force
        params['quiet'] = quiet

        response = self._gw_apipost('block/rm', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def block_stat(self,
        cid:str, # Bash58 encoded multihash of block(s) to remove

    ):
        'Print information of a raw IPFS block.'

        params = {}
        params['arg'] = cid

        response = self._gw_apipost('block/stat', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))
            
    def mfs_chcid(self,
        path:str='/', # Path to change
        cid_version:int=0, # Cid version to use
        **kwargs,
    ):
        'Change the CID version or hash function of the root node of a given path.'

        params = {}
        params['arg'] = path
        params['cid-version'] = cid_version
        params.update(kwargs)

        response = self._gw_apipost("files/chcid", params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def mfs_cp(self,
        source_path:str, # Source IPFS or MFS path to copy
        dest_path:str, # Destination within MFS
        **kwargs
    ):
        'Add references to IPFS files and directories in MFS (or copy within MFS).'

        params = {}
        params['arg'] = [source_path, dest_path]
        params.update(kwargs)

        response = self._gw_apipost('files/cp', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def mfs_flush(self,
        path:str='/', # Path to flush
    ):
        "Flush a given path's data to disk"

        params['arg'] = path

        response = self._gw_apipost('files/flush',params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def mfs_ls(self, 
        path:str='/', # Path to show listing for 
        **kwargs
    ):
        "List directories in the local mutable namespace."

        params = {}
        params['arg'] = path
        params.update(kwargs)

        response = self._gw_apipost('files/ls', params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def mfs_mkdir(self,
        path:str, # Path to dir to make
        **kwargs,
    ):
        "Make directories."

        params = {}
        params['arg'] = path
        params.update(kwargs)

        response = self._gw_apipost("files/mkdir", params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def mfs_mv(self,
        source_path:str, # Source file to move
        dest_path:str,  # Destination path for file to be moved to
    ):
        "Move files."

        params = {}
        params['arg'] = [source_path, dest_path]

        response = self._gw_apipost("files/mv", params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def mfs_read(self,
        path, # Path to file to be read
        **kwargs,
    ):
        "Read a file in a given MFS."

        params = {}
        params['arg'] = path
        params.update(kwargs)

        response = self._gw_apipost("files/read",params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))
            
    def mfs_rm(self,
        path, # File to remove
        **kwargs,
    ):
        "Read a file in a given MFS."

        params = {}
        params['arg'] = path
        params.update(kwargs)

        response = self._gw_apipost("files/rm", params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def mfs_stat(self,
        path, # Path to node to stat
        **kwargs,
    ):
        "Display file status."    

        params = {}
        params['arg'] = path
        params.update(kwargs)

        response = self._gw_apipost("files/stat", params=params)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

    def mfs_write(self,
        path, # Path to write to
        filepath, # File to add
        create=True, # Create the file if it does not exist
        **kwargs,
    ):
        "Display file status."    

        files = {
            'file': open(filepath, 'rb')
        }

        params = {}
        params['arg'] = path
        params['create'] = 'true' if create else 'false'
        params.update(kwargs)

        response = self._gw_apipost("files/write", params=params, files=files)

        if response.status_code == 200:
            return response, parse_response(response)

        else:
            raise HTTPError (parse_error_message(response))

# %% ../nbs/01_ipfshttpapi.ipynb 55
class DownloadDir:
    'Download a IPFS directory to your local disk'
    def __init__(self,
        gateway_type:str, # Gateway to use - works on local and public 
        root_cid:str, # Root CID of the directory
        output_fol:str, # Path to save in your local disk
    ):
        
        self.api = IPFSApi(gateway_type=gateway_type)
        self.root = root_cid
        self.output = output_fol
        self.full_structure = None
    
    def _get_links(self,
        cid, 
        fol
    ):
        root_struct = {}
        struct = {}

        _, obj = self.api.ls_items(cid)
        
        for link in obj[0]['Objects'][0]['Links']:
            name = f'{fol}/{link["Name"]}'
            hash_ = str(link['Hash'])
            type_ = link['Type']

            if type_ != 2:
                details = self._get_links(hash_, name)

            else:
                details = {'Hash': hash_, 'type': type_}

            struct[name] = details

        root_struct[fol] = struct

        return root_struct
    
    
    def _save_links(self,
        links
    ):
        for k, v in links.items():
            if len(k.split('.')) < 2:
                if not os.path.exists(k): os.mkdir(k)
                self._save_links(v)

            else:
                res, data = self.api.cat_items(links[k]['Hash'])

                with open(k, 'wb') as f:
                    f.write(res.content)
                    
    def download(self
    ):
        self.full_structure = self._get_links(self.root, self.output)
        self._save_links(self.full_structure)
        
