import hub
import requests

from requests.exceptions import HTTPError
from ipfspy.utils import GATEWAYS_API_READ, GATEWAYS_API_WRITE, parse_error_message, parse_response, get_coreurl
from ipfspy.ipfsspec import IPFSGateway, IPFSFileSystem

class IPFSProvider(hub.core.storage.provider.StorageProvider):
    def __init__(
        self,
        coreurl:str, # Core URL to use
        storage_type:str, # specify type of gateway (e.g. Infura, Estuary, Web3.Storage, local node...)
        api_key:str=None, # if applicable, api key for access to storage service
    ) -> None:
        """Initialize the object, assign credentials if required."""
        super().__init__()
        self.coreurl = coreurl
        self.fs = IPFSFileSystem(local=False, coreurl=self.coreurl)
        self.storage_type = storage_type
        self.api_key = api_key

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
        # test = f"/pinning/pins/{path}"

        params = {
            'arg': path,
        }

        response = requests.post('https://ipfs.infura.io:5001/api/v0/pin/rm', params=params)
        return response