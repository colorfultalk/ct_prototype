import ast
from flask import Flask, request, abort, g
from init import *          # get constants
from img_s3 import img_s3   # for handling image
from template_wrapper.button import generate_button_message # original template message wrapper
from template_wrapper.carousel import generate_carousel_message_for_item # original template message wrapper
from models import Item
import static_message

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, LocationMessage
)

class EditFlow:

    def __init__(self, line_bot_api, api_client):
        self.line_bot_api = line_bot_api
        self.api_client   = api_client

    def basic_reply(self, reply_token, edit_target):
        session = getattr(g, 'session', None)

        # set reply_text
        if edit_target is None:
            reply_text = static_message.SELECT_EDIT_TARGET
            reply_msg = TextSendMessage(text=reply_text)

        else:
            reply_text = ''
            if edit_target == IMAGE:
                reply_text = static_message.EDIT_IMAGE
            elif edit_target == DESCRIPTION:
                reply_text = static_message.EDIT_DESCRIPTION
            elif edit_target == LOCATION:
                reply_text = static_message.EDIT_LOCATION
            else :
                print( 'error' )
            reply_msg  = TextSendMessage( text = reply_text )

        # reply
        self.line_bot_api.reply_message(reply_token, reply_msg)

    def show_items(self, reply_token, session):
        # convert dict to item object
        items = []
        for element in session.get('items'):
            item = Item.__new__(Item)
            item.__dict__.update(element)
            items.append(item)

        reply_msg = generate_carousel_message_for_item(items)
        self.line_bot_api.reply_message(reply_token, reply_msg)

    def reset(self, session):
        session.pop('flow')
        session.pop('edit_target')

    def edit_item_detail(self, key, new_data, session):
        index = int(session.get('edit_item_index'))
        if index is None:
            print("ERROR: no index of edit item")
            return

        session['items'][index][key] = new_data

        # send new data to api server
        params = {
            'itemId': session['items'][index]['id'],
            key: new_data
        }
        response = self.api_client.edit_my_guest_item(params)
        print(response)


    def handle_text_message(self, event, session):
        text = event.message.text

        if text == 'image':
            session['edit_target'] = IMAGE

        elif text == 'description':
            session['edit_target'] = DESCRIPTION

        elif text == 'location':
            session['edit_target'] = LOCATION

        elif 'edit_target' not in session:
            session['edit_target'] = None

        elif session.get('edit_target') == DESCRIPTION:
            # set a new value to session
            self.edit_item_detail('description', text, session)
            self.show_items(event.reply_token, session)

            # reset flow and edit_target
            self.reset(session)
            return

        self.basic_reply( event.reply_token, session.get('edit_target') )

    def handle_image_message(self, event, session):
        msgId = event.message.id
        message_content = self.line_bot_api.get_message_content(msgId)

        if session.get('edit_target') == IMAGE:
            # upload s3
            presigned_url  = img_s3.upload_to_s3(message_content.content, bucket)
            print(presigned_url)

            # set a new value to session
            self.edit_item_detail('image_url', presigned_url, session)
            self.show_items(event.reply_token, session)

            # reset flow and edit_target
            self.reset(session)

        else:
            # when get wrong input value
            self.basic_reply(event.reply_token, session.get('edit_target'))

    def handle_location_message(self, event, session):
        location = event.message.address

        if session.get('edit_target') == LOCATION:
            # location
            print( location )

            # set a new value to session
            self.edit_item_detail('address', location, session)
            self.show_items(event.reply_token, session)

            # reset flow and edit_target
            self.reset(session)

        else:
            # when get wrong input value
            self.basic_reply(event.reply_token, session.get('edit_target'))

    def handle_postback(self, event, session):
        postback_data = ast.literal_eval(event.postback.data)
        session['edit_item_index'] = postback_data['edit_item_index']

        self.basic_reply(event.reply_token, None)

