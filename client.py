# -*- coding: utf-8 -*-
import requests, json
from init import *
client_params = {'appname' : APPNAME, 'username' : USERNAME, 'password' : PASSWORD}
base_url = "https://" + client_params['appname'] + ".herokuapp.com/"
# base_url = "http://localhost:8000/"

class Client:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_token(self):
        """
        CALL /token
        """
        # set base url
        url = base_url + "token/"

        # set headers and obj
        headers = {"Content-Type" : "application/json"}
        obj  = { "username" : self.username, "password" : self.password }
        data = json.dumps(obj).encode("utf-8")
        # api call
        response = requests.post(url, data, headers=headers)
        token = response.json()['token']
        return token

    def register_host(params):
        """
        CALL api/hosts
        """
        name      = params["name"]
        shopName  = params["shopName"]

        token   = get_token()
        url     = base_url + "api/hosts/"
        headers = { "Content-Type" : "application/json" ,
                    "Authorization" : 'JWT {}'.format(token) }
        obj = {
                "name": name,
                "shopName": shopName
                }
        data = json.dumps(obj).encode("utf-8")
        # check given lineId is already registered or not
        response = requests.post(url, data, headers=headers)
        return response

    def verify_host(self, params):
        """
        CALL api/hosts/${pk}
        """
        pk         = params["pk"]
        verifyPass = params["verifyPass"]
        lineId     = params["lineId"]

        token    = self.get_token()
        url      = base_url + "api/hosts/" + str(pk) + "/"
        obj      = {"verifyPass" : verifyPass, "lineId": lineId}
        response = requests.post(url, headers=headers)
        return response

    def retrieve_host(self, params):
        """
        CALL api/hosts/${pk}
        """
        lineId = params["lineId"]
        # get jwt token
        token   = self.get_token()
        url     = base_url + "api/hosts/" + lineId + "/"
        headers = { "Content-Type" : "application/json" ,
                    "Authorization" : 'JWT {}'.format(token) }
        # check given lineId is already registered or not
        response = requests.get(url, headers=headers)
        return response

    def retrieve_guest(self, params):
        """
        CALL api/guests/${pk}
        """
        lineId = params['lineId']
        token = self.get_token()
        url     = base_url + "api/guests/" + lineId + "/"
        headers = { "Content-Type" : "application/json" ,
                    "Authorization" : 'JWT {}'.format(token) }
        # check given lineId is already registered or not
        response = requests.get(url, headers=headers)
        return response

    def register_guest(self, params):
        """
        CALL api/guests/
        """
        lineId = params['lineId']
        name   = params['name']

        # get jwt token
        token = self.get_token()

        url      = base_url + "api/guests/"
        headers  = { "Content-Type" : "application/json" ,
                    "Authorization" : 'JWT {}'.format(token) }
        obj      = {"lineId": lineId, "name": name }
        data     = json.dumps(obj).encode("utf-8")
        response = requests.post(url, data, headers = headers)
        return response

    def register_item(self, params):
        """
        CALL /api/items
        """
        name        = params["name"]
        price       = params["price"]
        description = params["description"]
        imgUrl      = params["imgUrl"]
        host        = params["host"]
        longitude   = params["longitude"]
        latitude    = params["latitude"]
        address     = params["address"]
        # get jwt token
        token = self.get_token()

        url      = base_url + "api/items/"
        headers  = { "Content-Type" : "application/json" ,
                    "Authorization" : 'JWT {}'.format(token) }
        obj      = {
                "name":        name,
                "price":       price,
                "description": description,
                "imgUrl":      imgUrl,
                "host":        host,
                "longitude":   longitude,
                "latitude":    latitude,
                "address":     address
                }
        data     = json.dumps(obj).encode("utf-8")
        response = requests.post(url, data, headers = headers)
        return response

    def retrieve_items(self, params):
        """
        CALL /api/searchitems
        """
        latitude  = params["latitude"]
        longitude = params["longitude"]
        # get jwt token
        token = self.get_token()

        url      = base_url + "api/searchitems/"
        headers  = { "Content-Type" : "application/json" ,
                    "Authorization" : 'JWT {}'.format(token) }
        obj      = {
                "latitude": latitude,
                "longitude": longitude
                }
        data     = json.dumps(obj).encode("utf-8")
        response = requests.get(url, data, headers = headers)
        return response

    def register_guest_item(self, params):
        """
        CALL /api/guest-items
        """
        # extract parameters
        guest       = params['guest']
        description = params['description']
        imgUrl      = params['imgUrl']
        longitude   = params['longitude']
        latitude    = params['latitude']
        address     = params["address"]

        # get jwt token
        token = self.get_token()

        url     = base_url + "api/guest-items/"
        headers = { "Content-Type" : "application/json" ,
                    "Authorization" : 'JWT {}'.format(token) }
        obj      = {
                "guest":       guest,
                "description": description,
                "imgUrl":      imgUrl,
                "latitude":    latitude,
                "longitude":   longitude
                "address":     address
                }
        data     = json.dumps(obj).encode("utf-8")
        response = requests.post(url, data, headers = headers)
        return response

    def retrieve_guest_items(self, params):
        """
        CALL /api/guest-searchitems
        """
        latitude  = params["latitude"]
        longitude = params["longitude"]
        # get jwt token
        token = self.get_token()

        url      = base_url + "api/guest-searchitems/"
        headers  = { "Content-Type" : "application/json" ,
                    "Authorization" : 'JWT {}'.format(token) }
        obj      = {
                "latitude": latitude,
                "longitude": longitude
                }
        # data     = json.dumps(obj).encode("utf-8")
        response = requests.get(url, params = obj, headers = headers)
        return response
