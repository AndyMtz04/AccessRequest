# Access Request to ServiceNow

Python automation tool automates the creation of ServiceNow tickets from internal access request tasks by utilizing the ServiceNow API

## Download Source Code

To downlaod the source code, use the following command.

```git clone git@github.com:AndyMtz04/access_request.git```

## Installation

The script is only compatible with Python 3.x and only uses one module. 


1. Install requests with ```pip requests```

2. Then set the constants in access_request.py to the proper ServiceNow instance

3. Set the username and password of the ServiceNow instance


For the script to work, the access request page should output json in the format below.

```{'results': ["requestId":1000, "recipientName": "Sam Smith"]}```