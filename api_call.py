import requests, json
from init import *
client_params = {'appname' : APPNAME, 'username' : USERNAME, 'password' : PASSWORD}
base_url = "https://" + client_params['appname'] + ".herokuapp.com/"

def get_token(client_params = client_params):

    # extract parameters
    appname  = client_params['appname']
    username = client_params['username']
    password = client_params['password']

    # set base url
    url = base_url + "token/"

    # set headers and obj
    headers = {"Content-Type" : "application/json"}
    obj = { "username" : username, "password" : password }
    json_data = json.dumps(obj).encode("utf-8")

    # api call
    response = requests.post(url, json_data, headers=headers)
    token = response.json()['token']
    return token

def register_guest(params , client_params = client_params):

    # extract parameters
    lineId = params['lineId']
    name   = params['name']

    # get jwt token
    token = get_token(client_params)

    # check given lineId is already registered or not

    # if not, then create new guest
    url = base_url + "api/guests/"
    headers = { "Content-Type" : "application/json" ,
                "Authorization" : 'JWT {}'.format(token) }
    obj = { "lineId" : lineId, "name" : name }
    json_data = json.dumps(obj).encode("utf-8")
    response = requests.post(url, json_data, headers = headers)
    print( response )

def register_guest_image(params, client_params = client_params):
    # extract parameters
    guest  = 1   # test sample
    description = params['description']
    imgUrl      = params['imgUrl']
    longitude   = params['longitude']
    latitude    = params['latitude']

    # get jwt token
    token = get_token(client_params)

