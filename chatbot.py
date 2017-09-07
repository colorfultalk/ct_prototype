from flask import Flask, request, abort, g
import os
import sys

# get constants
from init import *

# for handling image
from img_s3 import img_s3

# for handling aws s3
import boto3
bucketName = 'ct-prototype'
s3 = boto3.resource('s3')
bucket = s3.Bucket(bucketName)

# for api_call
import api_call

from linebot import (
    LineBotApi, WebhookHandler, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, LocationMessage
)
from botsession import BotSessionInterface

# original template message wrapper
from template_wrapper.button import generate_button_message

app = Flask(__name__)
botSessionInterface = BotSessionInterface()

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
parser  = WebhookParser(channel_secret)

# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        events = parser.parse(body, signature)
        user_id = events.pop().source.user_id
        g.user_id = user_id
        session = botSessionInterface.open_session(app, request)
        g.session = session
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@app.after_request
def after_request(response):
    session = getattr(g, 'session', None)
    print("after_request")
    print(session)
    botSessionInterface.save_session(app, session, response)
    return response

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
    line_bot_api.reply_message(
        reply_token,
        reply_msg
    )

# text handler
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text    = event.message.text
    session = getattr(g, 'session', None)

    if text == 'clear':
        # clear session key
        del session['next_input']
        print( 'session cleared' )

    elif sequence_is_not_initialized( session ):
        # sequence initialized
        pass

    elif session.get('next_input') == DESCRIPTION:
        # set input value to session
        session['DESCRIPTION'] = text
        # set next input
        session['next_input']  = LOCATION
        basic_reply( event.reply_token, session.get('next_input') )

    else:
        # when get wrong input value
        basic_reply( event.reply_token, session.get('next_input') )

# image handler
@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    session = getattr(g, 'session', None)
    msgId = event.message.id
    message_content = line_bot_api.get_message_content(msgId)

    if sequence_is_not_initialized( session ) or session.get('next_input') == IMAGE:
        # upload s3
        presigned_url  = img_s3.upload_to_s3( message_content.content, bucket )
        print( presigned_url )

        # set input value to session
        session['IMAGE'] = presigned_url
        session['next_input'] = DESCRIPTION
        basic_reply( event.reply_token, session.get('next_input') )

    else:
        # when get wrong input value
        basic_reply( event.reply_token, session.get('next_input') )

# location handler
@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    session  = getattr(g, 'session', None)
    location = event.message.address

    if sequence_is_not_initialized( session ):
        # session initialized
        pass

    elif session.get('next_input') == LOCATION:
        # location
        print( location )

        # set input value
        session['LOCATION']   = location
        session['next_input'] = ALL_SET
        basic_reply( event.reply_token, session.get('next_input') )

    else:
        # when get wrong input value
        basic_reply( event.reply_token, session.get('next_input') )

if __name__ == "__main__":
    app.run()
