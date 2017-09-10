from flask import Flask, request, abort, g
from init import *          # get constants
from img_s3 import img_s3   # for handling image
import boto3                # for handling aws s3
s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKET_NAME) # BUCKET_NAME is defined in init.py
from template_wrapper.button import generate_button_message # original template message wrapper

class RegisterFlow:

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api

    def sequence_is_not_initialized( session ):
        if 'next_input' not in session:
            # set first input
            session['next_input'] = IMAGE
            print( 'sequence initialized' )
            return True
        else:
            return False

    def basic_reply( reply_token, next_input ):
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

        if self.sequence_is_not_initialized( session ):
            # sequence initialized
            pass

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
        message_content = line_bot_api.get_message_content(msgId)

        if self.sequence_is_not_initialized( session ) or session.get('next_input') == IMAGE:
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

        if self.sequence_is_not_initialized( session ):
            # session initialized
            pass

        elif session.get('next_input') == LOCATION:
            # location
            print( location )

            # set input value
            session['LOCATION']   = location
            session['next_input'] = ALL_SET
            self.basic_reply( event.reply_token, session.get('next_input') )

        else:
            # when get wrong input value
            self.basic_reply( event.reply_token, session.get('next_input') )