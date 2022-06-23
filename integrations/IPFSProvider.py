import hub
import requests

from requests.exceptions import HTTPError
from ipfspy.utils import GATEWAYS_API_READ, GATEWAYS_API_WRITE, parse_error_message, parse_response, get_coreurl
from ipfspy.ipfsspec import IPFSGateway, IPFSFileSystem

class IPFSProvider(hub.core.storage.provider.StorageProvider):
    def __init__(self) -> None:
        """Initialize the object, assign credentials if required."""
        super().__init__()
        self.fs = IPFSFileSystem(local=False, coreurl='https://ipfs.infura.io:5001')


    def __getitem__(self, cid, **kwargs):
        """Gets the object present at the path."""
        params = {}
        params['arg'] = cid
        params.update(kwargs)

        res = self.session.post(f'{self.url}/get', params=params)

        if res.status_code == 200:
            return res, parse_response(res)

        else:
            raise HTTPError (parse_error_message(res))


    def __setitem__(self, path, value):
        """Sets the object present at the path with the value"""
        return self.fs.gw.apipost("add", path)


    def __delitem__(self, path):
        """Delete the object present at the path."""

        params = {
            'arg': path,
        }

        response = requests.post('https://ipfs.infura.io:5001/api/v0/pin/rm', params=params)
        return response


    def __iter__(self, path):
        """Generator function that iterates over the keys of the mapper"""
        params = {
            'arg': path,
            'long': 'false',
            'U': 'false',
        }

        response = requests.post('http://127.0.0.1:5001/api/v0/files/ls', params=params)
        return response



    def __len__(self, path):
        """Returns the the information of a raw IPFS block"""
        params = {
            'arg': path,
        }

        response = requests.post('http://127.0.0.1:5001/api/v0/block/stat', params=params)