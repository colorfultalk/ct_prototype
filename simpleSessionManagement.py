from flask import Flask, request, abort, g
import os
import sys

from linebot import (
    LineBotApi, WebhookHandler, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text    = event.message.text
    session = getattr(g, 'session', None)

    if session.get('next') == 1:
        # set next phase
        session['next'] = 2

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='phase1'))

    elif session.get('next') == 2:
        # set next phase
        session['next'] = 1

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='phase2'))

    else:
        # set next phase
        session['next'] = 1

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='start'))


if __name__ == "__main__":
    app.run()
