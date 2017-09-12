from flask import Flask, request, abort, g
from init import *          # get constants
from img_s3 import img_s3   # for handling image
from template_wrapper.button import generate_button_message # original template message wrapper

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, LocationMessage
)

class EditFlow:

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api

    def basic_reply(self, reply_token, edit_target):
        session = getattr(g, 'session', None)

        # set reply_text
        if edit_target is None:
            reply_text = "Select a edit target\n image / description / location"
            reply_msg = TextSendMessage(text=reply_text)

        else:
            reply_text = 'please input a new ' + edit_target
            reply_msg  = TextSendMessage( text = reply_text )

        # reply
        self.line_bot_api.reply_message(reply_token, reply_msg)

    def show_item(self, reply_token):
        session = getattr(g, 'session', None)

        # if everything set then display demo
        if session.get('next_input') == ALL_SET:
            reply_msg = generate_button_message(
                text = session.get('DESCRIPTION'),
                thumbnail_image_url = session.get('IMAGE')
            )
            self.line_bot_api.reply_message(reply_token, reply_msg)



    def handle_text_message(self, event, session):
        text = event.message.text
        if session.get('edit_target') == DESCRIPTION:
            # set a new value to session
            session['DESCRIPTION'] = text
            self.show_item(event.reply_token)

            # reset flow and edit_target
            session.pop('flow')
            session.pop('edit_target')
        else:
            if 'edit_target' not in session:
                session['edit_target'] = None

            elif text == 'image':
                session['edit_target'] = IMAGE

            elif text == 'description':
                session['edit_target'] = DESCRIPTION

            elif text == 'location':
                session['edit_target'] = LOCATION

            self.basic_reply( event.reply_token, session.get('edit_target') )

    def handle_image_message(self, event, session):
        msgId = event.message.id
        message_content = self.line_bot_api.get_message_content(msgId)

        # TODO 編集するアイテムを選択する必要あり
        old_image = session.get(IMAGE)
        if old_image is not None and session.get('edit_target') == IMAGE:
            # upload s3
            presigned_url  = img_s3.upload_to_s3( message_content.content, bucket )
            print( presigned_url )

            # set a new value to session
            session['IMAGE'] = presigned_url
            self.show_item(event.reply_token)

            # reset flow and edit_target
            session.pop('flow')
            session.pop('edit_target')

        else:
            # when get wrong input value
            self.basic_reply( event.reply_token, session.get('edit_target') )

    def handle_location_message( self, event, session ):
        location = event.message.address

        if session.get('edit_target') == LOCATION:
            # location
            print( location )

            # set a new value to session
            session['LOCATION'] = location
            self.show_item(event.reply_token)

            # reset flow and edit_target
            session.pop('flow')
            session.pop('edit_target')

        else:
            # when get wrong input value
            self.basic_reply( event.reply_token, session.get('edit_target') )
