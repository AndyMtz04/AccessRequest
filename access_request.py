import logging
import logging.config
import requests
import json.decoder


ACCESS_REQUEST_URL = "" # Add access request posting site
SERVICENOW_URL = "https://dev19075.service-now.com/api/now/v2/table/sc_task?sysparm_limit=500&sysparm_query=short_descriptionLIKE-%20Access%20Request%20-^active=false^ORactive=true^ORDERBYDESCnumber"
POST_URL = "https://dev19075.service-now.com/api/now/v2/table/sc_task"
SERVICENOW_USER = ""
SERVICENOW_PASSWORD = ""


def main():

    access_results = get_access_tasks(ACCESS_REQUEST_URL)
    servicenow_results = get_servicenow_tasks(SERVICENOW_URL, SERVICENOW_USER, SERVICENOW_PASSWORD)
    extract_results = extract_tasks(access_results, servicenow_results)
    post_tasks(extract_results, POST_URL, SERVICENOW_USER, SERVICENOW_PASSWORD)

    logging.info("Done!")


def get_access_tasks(access_url):
    """Function gets access request tasks in json"""
    logging.info("Pulling from Access Request!")
    response = requests.get(access_url, timeout=(3.5, 60))
    json_results = response.json()["results"]

    return json_results


def get_servicenow_tasks(servicenow_url, username, password):
    """Function gets posted servicenow tasks in json."""
    logging.info("Pulling from ServiceNow!")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = requests.get(servicenow_url, auth=(username, password), headers=headers, timeout=(3.5, 60))
    json_results = response.json()["result"]

    return json_results


def extract_tasks(access_results, service_results):
    """Function loops through access request tasks, which have not been posted,
    and returns non-duplicates"""
    logging.info("Extracting non-duplicate tasks!")
    final_results = []
    for x in access_results:
        in_servicenow = False
        for i in service_results:
            request_id = i["short_description"].split(" ")[0]
            if request_id.isnumeric():
                if x["requestId"] == int(request_id):
                    in_servicenow = True
        if not in_servicenow:
            final_results.append(x)

    return final_results


def post_tasks(results, servicenow_url, username, password):
    """Function loops through access request tasks and posts them to the ServiceNow instance."""
    logging.info("Posting tasks to ServiceNow!")
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    for x in results:
        request_id = x["requestId"]
        recipient_name = x["recipientName"]
        short_description = "{0} - Access Request - {1}".format(request_id, recipient_name)
        description = "{}".format(request_id) # Add link to access request
        data = ("{{'short_description':'{0}','description':'{1}',\
                'assignment_group':'d625dccec0a8016700a222a0f7900d06',\
                'urgency':'3','impact':'3','priority':'4'}}").format(short_description, description)
        requests.post(servicenow_url, auth=(username, password), headers=headers, data=data)

    logging.info("Posted {} task/s!".format(len(results)))


logging.config.fileConfig("logging.ini")

try:
    main()
except json.decoder.JSONDecodeError:
    logging.error("ServiceNow is down!", exc_info=True)
except requests.exceptions.ConnectionError:
    logging.error("No network connection or one of the sites is down!", exc_info=True)
except requests.exceptions.ReadTimeout:
    logging.error("Access request or ServiceNow took too long to respond!", exc_info=True)
