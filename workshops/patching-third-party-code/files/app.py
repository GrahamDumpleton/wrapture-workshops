"""The application: one request through the vendored client.

It knows nothing about wrapture. The last page of the workshop
patches it from a config file without changing a line here.
"""

from transports import echo
from vendored_client import Client

client = Client("https://api.example", echo)
print(client.request("GET", "/orders"))
