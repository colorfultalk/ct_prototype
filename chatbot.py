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
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, LocationMessage
)
from botsession import BotSessionInterface
from init import * # set constants

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

# import all flow
from flow.register import RegisterFlow
from flow.edit import EditFlow
# initialize all flow
register_flow = RegisterFlow( line_bot_api )
edit_flow = EditFlow( line_bot_api )

# import client for api_server
from client import Client
api_client = Client(USERNAME, PASSWORD)

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

# text handler
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    session = getattr(g, 'session', None)
    text    = event.message.text

    if text == 'clear':
        for key in list(session):
            session.pop(key, None)
        print( 'session cleared' )

    elif 'flow' not in session:
        # when flow is not set
        lineId   = event.source.user_id
        profile  = line_bot_api.get_profile(uId)
        uName    = profile.display_name

        # check user already registered or not
        params   = { "lineId": lineId }
        response = api_client.retrieve_guest(params)
        print( response.status_code )
        if reponse.status_code != 200:
            # when user is new
            params   = { "lineId": lineId, "name": uName }
            response = api_client.register_guest(params)

        # store guestId
        guestId = response.json()['id']
        session['guestId'] = guestId

        # set flow
        if text == 'register' :
            session['flow'] = REGISTER
        elif text == 'edit' :
            session['flow'] = EDIT
            edit_flow.handle_text_message( event, session )
        elif text == 'verify' :
            # TODO : implement verify mode function
            pass
        else:
            print( 'WARNING : no flow selected' )
            reply_text = "Select a flow\n register / edit / verify"
            reply_msg  = TextSendMessage(text=reply_text)
            line_bot_api.reply_message(
                event.reply_token,
                reply_msg
            )
    else:
        # when flow is set already
        flow = session.get('flow')
        if flow == REGISTER:
            register_flow.handle_text_message( event, session )
        elif flow == EDIT:
            edit_flow.handle_text_message( event, session )
            pass
        elif flow == VERIFY:
            # TODO : implement verify mode function
            pass
        else:
            print( 'ERROR : no flow matched' )

# image handler
@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    session = getattr(g, 'session', None)

    if 'flow' not in session:
        # when flow is not set
        print( 'WARNING : no flow selected' )
        reply_text = "Select a flow\n register / edit / verify"
        reply_msg  = TextSendMessage(text=reply_text)
        line_bot_api.reply_message(
            event.reply_token,
            reply_msg
        )

    else:
        # when flow is set already
        flow = session.get('flow')
        if flow == REGISTER:
            register_flow.handle_image_message( event, session )

        elif flow == EDIT:
            edit_flow.handle_image_message( event, session )

        elif flow == VERIFY:
            # TODO : implement verify mode function
            pass

        else:
            print( 'ERROR : no flow matched' )

# location handler
@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    session = getattr(g, 'session', None)

    if 'flow' not in session:
        # when flow is not set
        print( 'WARNING : no flow selected' )
    else:
        # when flow is set already
        flow = session.get('flow')
        if flow == REGISTER:
            register_flow.handle_location_message( event, session )

        elif flow == EDIT:
            edit_flow.handle_location_message( event, session )

        elif flow == VERIFY:
            # TODO : implement verify mode function
            pass

        else:
            print( 'ERROR : no flow matched' )

if __name__ == "__main__":
    app.run(port=8000)
