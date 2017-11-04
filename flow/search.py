from flask import Flask, request, abort, g
from init import *          # get constants
from template_wrapper.carousel import generate_carousel_message_for_item # original template message wrapper
from models import Item

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, LocationMessage
)
from pprint import pprint
import static_message

class SearchFlow:

    def __init__(self, line_bot_api, api_client):
        self.line_bot_api   = line_bot_api
        self.api_client     = api_client

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
        reply_text = static_message.REQUEST_CURRENT_LOCATION
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

        response    = self.api_client.retrieve_guest_items(params)
        datas       = eval( response.json() )[-5:]
        print()
        print("response:")
        pprint( datas )

        if len( datas ) > 0:
            # when at least one data is found around input location
            items = []
            for json in datas:
                items.append(self.json_to_item(json))
            self.show_items(event.reply_token, items)

        else:
            # when no data is found
            reply_text = static_message.NO_ITEM_FOUND
            reply_msg  = TextSendMessage(text=reply_text)
            self.line_bot_api.reply_message(
                    event.reply_token,
                    reply_msg
            )
