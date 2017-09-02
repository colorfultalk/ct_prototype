import requests, json
def get_token(appname, username, password):
    # set base url
    url = "https://" + appname + ".herokuapp.com/token/"

    # set headers and obj
    headers = {"Content-Type" : "application/json"}
    obj = { "username" : username, "password" : password }
    json_data = json.dumps(obj).encode("utf-8")

    # api call
    response = requests.post(url, json_data, headers=headers)
    token = response.json()['token']
    return token
