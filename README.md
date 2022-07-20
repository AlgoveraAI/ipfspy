# Welcome to IPFSPy by Algovera
> A python library by Algovera to interact with IPFS and IPFS ecosystem such as the common pinning services


## What is IPFSPy?

IPFSPy is a python library by Algovera to interact with IPFS and IPFS ecosystem such as the common pinning services. It is designed by data scientists for data scientists to interact with the IPFS ecosystem without leaving the comfort of python and jupyter notebook.

You can learn more about IPFS [here](https://ipfs.io/#why).

IPFS is built using the go-lang or javascript. With IPFSPy, you can interact with IPFS using the exposed [HTTP RPC API](https://docs.ipfs.io/reference/http/api/#getting-started). 

With IPFSPy, you can either use local, infura or public nodes. In order to use local node, you will need a IPFS deamon running in the form of IPFS Desktop, IPFS Campanion on IPFS CLI. As an alternative, you can connect via the [Infura](https://infura.io/product/ipfs)'s dedicated IPFS gateway. 

## Installing

to do: instructions on how to install library goes here

## How to use

To adda file to IPFS, simply

```python
from ipfspy.ipfshttpapi import IPFSApi

api = IPFSApi()
response, json = api.add_items(url, "path/to/file")
```
