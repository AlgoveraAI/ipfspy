# Welcome to Immerse by Algovera
> A python library by Algovera to interact with IPFS and IPFS ecosystem such as the common pinning services


## What is Immerse?

Immerse is a python library by Algovera to interact with IPFS and IPFS ecosystem such as the common pinning services. It is designed by data scientists for data scientists to interact with the IPFS ecosystem without leaving the comfort of python and jupyter notebook.

You can learn more about IPFS [here](https://ipfs.io/#why)

IPFS is built using the go-lang and javascript. With Immerse, you can interact with IPFS using the exposed [HTTP RPC API](https://docs.ipfs.io/reference/http/api/#getting-started). 

You will need a local IPFS Node running to use the HTTP API (even when using Immerse). As an alternative, you can connect via the [Infura](https://infura.io/product/ipfs)'s dedicated IPFS gateway. Immerse provide both ways to interact with IPFS.

## Installing

to do: instructions on how to install library goes here

## How to use

To adda file to IPFS, simply

```python
from immerse import httpapi

url = get_coreurl()
response, json = add_items(url, "path/to/file")
```
