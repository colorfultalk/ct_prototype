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

from linebot import (
    LineBotApi, WebhookHandler, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage
)
from botsession import BotSessionInterface

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

def sequence_is_not_started( session ):
    if 'next_input' not in session:
        # set first input
        session['next_input'] = IMAGE
        return True
    else:
        return False

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text    = event.message.text
    session = getattr(g, 'session', None)

    if sequence_is_not_started:
        # sequence initialized
        pass

    elif session.get('next_input') == DESCRIPTION:
        # set input value to session
        session['DESCRIPTION'] = text
        # set next input
        session['next_input']  = LOCATION

    else:
        # when get wrong input value
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='your input is wrong, please retry!'))

# image handler
@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    session = getattr(g, 'session', None)

    # get message_content
    msgId = event.message.id
    message_content = line_bot_api.get_message_content(msgId)

    # upload s3
    response  = img_s3.upload_to_s3( message_content.content, bucket )
    print( response )

    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='you sent me an image'))

if __name__ == "__main__":
    app.run()
