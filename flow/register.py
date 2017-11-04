import sys,os
sys.path.append(os.pardir)
from flask import Flask, request, abort, g
from init import *          # get constants
from img_s3 import img_s3   # for handling image
from template_wrapper.button import generate_button_message # original template message wrapper
import static_message

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, LocationMessage
)

class RegisterFlow:

    def __init__(self, line_bot_api, api_client):
        self.line_bot_api   = line_bot_api
        self.api_client     = api_client

    # session initializer
    def initialize( self, event, session ):
            FIRST_INPUT = IMAGE # set first input
            session['next_input'] = FIRST_INPUT
            self.basic_reply( event.reply_token, FIRST_INPUT )

    def register_guest_item( self, guestId, description, imgUrl, latitude, longitude, address):
        params = {
            "guest"       : guestId,
            "description" : description,
            "imgUrl"      : imgUrl,
            "latitude"    : latitude,
            "longitude"   : longitude,
            "address"     : address
        }
        response = self.api_client.register_guest_item( params )
        return( response )

    def basic_reply( self, reply_token, next_input ):
        # select reply message
        reply_text = ''
        if next_input == IMAGE:
            reply_text = static_message.BASIC_REPLY_IMAGE
        elif next_input == DESCRIPTION:
            reply_text = static_message.BASIC_REPLY_DESCRIPTION
        elif next_input == LOCATION:
            reply_text = static_message.BASIC_REPLY_LOCATION
        else :
            print( 'error' )
        # reply
        reply_msg  = TextSendMessage( text = reply_text )
        self.line_bot_api.reply_message(
            reply_token,
            reply_msg
        )

    # call when all inputs are set properly
    def show_demo( self, reply_token, session):
        # if everything set then display demo
        reply_msg = generate_button_message(
                    text = session.get('DESCRIPTION'),
                    thumbnail_image_url = session.get('IMAGE')
                )
        # reply
        self.line_bot_api.reply_message(
            reply_token,
            reply_msg
        )

    def handle_text_message( self, event, session ):
        text = event.message.text

        # when session is not initialized
        if 'next_input' not in session:
            self.initialize( event, session )
        else:
            next_input = session.get('next_input')
            if next_input == DESCRIPTION:
                # set input value to session
                session['DESCRIPTION'] = text
                # set next input
                session['next_input']  = LOCATION
                self.basic_reply( event.reply_token, session.get('next_input') )
            else:
                # when get wrong input value
                self.basic_reply( event.reply_token, next_input )

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
        latitude = event.message.latitude
        longitude = event.message.longitude
        address = event.message.address

        # when session is not initialized
        if 'next_input' not in session:
            self.initialize( event, session )

        elif session.get('next_input') == LOCATION:
            # location
            print( address )

            # set input value
            session['LOCATION']   = {
                'latitude': latitude,
                'longitude': longitude,
                'address': address,
            }
            session['next_input'] = ALL_SET

            # register
            # session.get('LOCATION') does not work in this time
            r = self.register_guest_item(
                guestId     = session.get('guestId'),
                description = session.get('DESCRIPTION'),
                imgUrl      = session.get('IMAGE'),
                latitude    = latitude,
                longitude   = longitude,
                address     = address
            )
            print( r.status_code )

            self.show_demo( event.reply_token, session)
            session.pop('flow')
            session.pop('next_input')

        else:
            # when get wrong input value
            self.basic_reply( event.reply_token, session.get('next_input') )
