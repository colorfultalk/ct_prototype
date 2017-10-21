from flask import Flask, request, abort, g
from init import *          # get constants
from template_wrapper.carousel import generate_carousel_message_for_item # original template message wrapper
from models import Item

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, LocationMessage
)
from pprint import pprint

class SearchFlow:

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api

    def show_items(self, reply_token, items):
        reply_msg = generate_carousel_message_for_item(items)
        self.line_bot_api.reply_message(reply_token, reply_msg)

    def reset(self, session):
        session.pop('flow')

    def json_to_item(self, json):
        item = Item(
            image_url=json['imgUrl'],
            description=json['description'],
            latitude=json['latitude'],
            longitude=json['longitude']
        )
        return item

    def handle_text_message(self, event, session):
        reply_token = event.reply_token
        reply_text = 'Please input your location.'
        reply_msg  = TextSendMessage(text=reply_text)

        # reply
        self.line_bot_api.reply_message(
            reply_token,
            reply_msg
        )


    def handle_location_message(self, event, session):
        params = {
            "latitude"    : event.message.latitude,
            "longitude"   : event.message.longitude
        }

        response = api_client.retrieve_guest_items(params)
        print()
        print("response:")
        pprint(eval(response.json()))

        items = []
        for json in eval(response.json()):
            items.append(self.json_to_item(json))

        self.show_items(event.reply_token, items)
