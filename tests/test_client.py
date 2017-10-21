import unittest
import sys, os
sys.path.append(os.pardir)
from client import Client
from init import *

class TestClient(unittest.TestCase):
    def setUp(self):
        username  = USERNAME
        password  = PASSWORD
        self.c = Client(username, password)

    def test_get_token(self):
        token = self.c.get_token()
        self.assertEqual(type(token), str)

    # def test_register_host(self):
    #     name      = "fooo"
    #     shopName  = "foooShop"
    #     longitude = 132.213
    #     latitude  = 53.2123
    #     params    = {
    #             "name": name,
    #             "shopName": shopName,
    #             "longitude": longitude,
    #             "latitude": latitude
    #             }
    #     response = self.c.register_host(params)
    #     self.assertEqual(response.status_code, 201)

    def test_register_guest(self):
        lineId   = "exk123244"
        name      = "fooo"
        params   = {
                "lineId": lineId,
                "name": "fooo"
                }
        response = self.c.register_guest(params)
        self.assertEqual(response.status_code, 201)

    def test_retrieve_guest(self):
        lineId   = "u123457"
        params   = {"lineId": lineId}
        response = self.c.retrieve_guest(params)
        self.assertEqual(response.status_code, 200)

    def test_register_item(self):
        """
        CALL /api/items
        """
        name        = "fuga"
        price       = 200
        description = "Let's go"
        imgUrl      = "https://hogehoge.com/hogehoge.png"
        host        = 1
        latitude    = 34.733038
        longitude   = 135.732624
        address     = "Takayama-cho 8916-5, Ikoma, Nara"
        params      = {
                "name":        name,
                "price":       price,
                "description": description,
                "imgUrl":      imgUrl,
                "host":        host,
                "latitude":    latitude,
                "longitude":   longitude,
                "address":     address
                }
        response = self.c.register_item(params)
        self.assertEqual(response.status_code, 201)

#    def test_retrieve_items(self):
#        latitude  = 123.123
#        longitude = 54.432
#        params    = {
#                "latitude": latitude,
#                "longitude": longitude
#                }
#        response = self.c.retrieve_items(params)
#        self.assertEqual(response.status_code, 200)

    def test_register_guest_item(self):
        guest       = 1
        description = "Let it go"
        imgUrl      = "https://hogehoge.com/hogehgoe.png"
        latitude    = 34.733038
        longitude   = 135.732624
        address     = "Takayama-cho 8916-5, Ikoma, Nara"
        params      = {
                "guest":       guest,
                "description": description,
                "imgUrl":      imgUrl,
                "latitude":    latitude,
                "longitude":   longitude,
                "address":     address
                }
        response = self.c.register_guest_item(params)
        self.assertEqual(response.status_code, 201)

#    def test_retrieve_guest_items(self):
#        latitude  = 123.123
#        longitude = 54.432
#        params    = {
#                "latitude": latitude,
#                "longitude": longitude
#                }
#        response = self.c.retrieve_guest_items(params)
#        self.assertEqual(response.status_code, 200)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
