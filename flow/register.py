import sys,os
sys.path.append(os.pardir)
from flask import Flask, request, abort, g
from init import *          # get constants
from img_s3 import img_s3   # for handling image
from template_wrapper.button import generate_button_message # original template message wrapper
from geo_handler import geo_handler

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, LocationMessage
)

class RegisterFlow:

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api

    # session initializer
    def initialize( self, session ):
            session['next_input'] = IMAGE # set first input
            print( 'session initialized' )
            return True

    def register_guest_item( self, guestId, description, imgUrl, location ):
        latlng = geo_handler.addr2latlng(location)
        params = {
                "guest"       : guestId,
                "description" : description,
                "imgUrl"      : imgUrl,
                "latitude"    : latlng[0],
                "longitude"   : latlng[1]
                }
        response = api_client.register_guest_item( params )
        return( response )

    def basic_reply( self, reply_token, next_input ):
        session = getattr(g, 'session', None)

        # set reply_text
        if next_input == START:
            reply_text = 'sequence start'
            reply_msg  = TextSendMessage( text = reply_text )
        elif next_input == ALL_SET:
            # if everything set then display demo
            reply_msg = generate_button_message(
                        text = session.get('DESCRIPTION'),
                        thumbnail_image_url = session.get('IMAGE')
                    )
        else:
            reply_text = 'please input ' + next_input + ' next !'
            reply_msg  = TextSendMessage( text = reply_text )

        # reply
        self.line_bot_api.reply_message(
            reply_token,
            reply_msg
        )

    def handle_text_message( self, event, session ):
        text = event.message.text

        # when session is not initialized
        if 'next_input' not in session:
            self.initialize( session )

        elif session.get('next_input') == DESCRIPTION:
            # set input value to session
            session['DESCRIPTION'] = text
            # set next input
            session['next_input']  = LOCATION
            self.basic_reply( event.reply_token, session.get('next_input') )

        else:
            # when get wrong input value
            self.basic_reply( event.reply_token, session.get('next_input') )

    def handle_image_message( self, event, session ):
        msgId = event.message.id
        message_content = self.line_bot_api.get_message_content(msgId)

        # when session is not initialized
        if 'next_input' not in session or session.get('next_input') == IMAGE:
            # upload s3
            presigned_url  = img_s3.upload_to_s3( message_content.content, bucket )
            print( presigned_url )

            # set input value to session
            session['IMAGE'] = presigned_url
            session['next_input'] = DESCRIPTION
            self.basic_reply( event.reply_token, session.get('next_input') )

        else:
            # when get wrong input value
            self.basic_reply( event.reply_token, session.get('next_input') )

    def handle_location_message( self, event, session ):
        location = event.message.address

        # when session is not initialized
        if 'next_input' not in session:
            self.initialize( session )

        elif session.get('next_input') == LOCATION:
            # location
            print( location )

            # set input value
            session['LOCATION']   = location
            session['next_input'] = ALL_SET

            # register
            # session.get('LOCATION') does not work in this time
            r = self.register_guest_item(session.get('guestId'), session.get('DESCRIPTION'),
                    session.get('IMAGE'), location)
            print( r.status_code )

            # reset flow value
            session.pop('flow')
            self.basic_reply( event.reply_token, session.get('next_input') )

        else:
            # when get wrong input value
            self.basic_reply( event.reply_token, session.get('next_input') )
