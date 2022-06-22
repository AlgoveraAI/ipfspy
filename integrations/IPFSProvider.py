import hub

from requests.exceptions import HTTPError
from ipfspy.utils import GATEWAYS_API_READ, GATEWAYS_API_WRITE, parse_error_message, parse_response, get_coreurl
from ipfspy.ipfsspec import IPFSGateway, IPFSFileSystem

class IPFSProvider(hub.core.storage.provider.StorageProvider):
    def __init__(self) -> None:
        """Initialize the object, assign credentials if required."""
        super().__init__()
        self.gateway = IPFSGateway()
        self.fs = IPFSFileSystem()


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
        return self.gateway.apipost("add", path)


    def __delitem__(self, path):
        """Delete the object present at the path."""
        return


    def __iter__(self):
        """Generator function that iterates over the keys of the mapper"""
        return self.fs.ls() # which cid to use here?


    def __len__(self):
        """Returns the number of files present in the directory at the root of the mapper"""
        return