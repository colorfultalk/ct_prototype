import sys,os
sys.path.append(os.pardir)
from flask import Flask, request, abort, g
from init import *          # get constants
from models import Item
from template_wrapper.carousel import generate_carousel_message_for_item # original template message wrapper

class ShowFlow:

    # set sample item
    sample = Item(
            image_url = "https://s3.us-east-2.amazonaws.com/test-boto.mr-sunege.com/tmp/5qv16iyopm6idqq.jpg",
            description = "you have not registered an item yet",
            address = "8916-5 Takayama-cho, Ikoma, Nara 630-0192",
            latitude = 34.732128,
            longitude = 135.732925
    )

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api

    # this means ShowFlow.showItems() function
    def show_items(self, event, session):
        params      = {"guestId" : session.get('guestId')}
        response    = api_client.search_my_guest_items( params )
        items       = []

        if response.status_code is not 200:
            # when search failed
            items.append(sample)

        elif len( eval(response.json()) ) == 0:
            # when search success but no item found
            items.append(sample)

        else:
            # when search success and some items found
            data        = eval( response.json() )
            data        = data[0:5] # extract latest five items
            for i in range(len(data)):
                item = Item(
                    image_url   = data[i]['imgUrl'],
                    description = data[i]['description'],
                    address     = "8916-5 Takayama-cho, Ikoma, Nara 630-0192",
                    latitude    = data[i]['latitude'],
                    longitude   = data[i]['longitude']
                )
                items.append(item)

        # show items
        # session['items'] = list(map(lambda item: item.__dict__, items))
        reply_msg = generate_carousel_message_for_item(items)
        line_bot_api.reply_message(event.reply_token, reply_msg)