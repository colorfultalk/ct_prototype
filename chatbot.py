from flask import Flask, request, abort, g
import os
import sys
import ast
from linebot import (
    LineBotApi, WebhookHandler, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, LocationMessage, PostbackEvent
)
from botsession import BotSessionInterface
from init import * # set constants
from template_wrapper.carousel import generate_carousel_message_for_item # original template message wrapper
from models import Item
import static_message

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

# initialize client for api_server
from client import Client
api_client = Client(USERNAME, PASSWORD)

# import all flow
from flow.register  import RegisterFlow
from flow.edit      import EditFlow
from flow.search    import SearchFlow
from flow.show      import ShowFlow
# initialize all flow
register_flow   = RegisterFlow( line_bot_api, api_client )
edit_flow       = EditFlow( line_bot_api, api_client )
search_flow     = SearchFlow( line_bot_api, api_client )
show_flow       = ShowFlow( line_bot_api, api_client )

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

    # when guestId not set, check user
    if 'guestId' not in session:
        lineId   = event.source.user_id
        profile  = line_bot_api.get_profile(lineId)
        uName    = profile.display_name

        # api_client is defined in init.py
        # check user already registered or not
        params   = { "lineId": lineId }
        response = api_client.retrieve_guest(params)
        print( response.status_code )

        if response.status_code != 200:
            # when user is new
            params   = { "lineId": lineId, "name": uName }
            response = api_client.register_guest(params)

        # store guestId
        guestId = response.json()['id']
        session['guestId'] = guestId

    if text.count( 'clear' ):
        # clear function
        for key in list(session):
            session.pop(key, None)
        print( 'session cleared' )
        show_command(event)

    elif 'flow' not in session:
        if text.count( 'register' ) :
            session['flow'] = REGISTER
        elif text.count( 'search' ) :
            session['flow'] = SEARCH
        elif text.count( 'show' ) :
            session['flow'] = SHOW
        elif text.count( 'verify' ):
            # TODO : implement verify mode function
            pass
        else:
            print( 'WARNING : no flow selected' )
            show_command(event)
        # set flow
        flow_swicher(event, session)

    else:
        # when flow is set already
        if text.count( 'register' ) :
            session['flow'] = REGISTER
        elif text.count( 'search' ) :
            session['flow'] = SEARCH
        elif text.count( 'show' ) :
            session['flow'] = SHOW
        # run function
        flow_swicher(event, session)

# image handler
@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    session = getattr(g, 'session', None)

    if 'flow' not in session:
        # when flow is not set
        print( 'WARNING : no flow selected' )
        show_command(event)

    else:
        # when flow is set already
        flow_swicher(event, session)

# location handler
@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    session = getattr(g, 'session', None)

    if 'flow' not in session:
        # when flow is not set
        print( 'WARNING : no flow selected' )
        show_command(event)

    else:
        # when flow is set already
        flow_swicher(event, session)

# postback handler
@handler.add(PostbackEvent)
def handle_postback(event):
    session = getattr(g, 'session', None)
    postback_data = ast.literal_eval(event.postback.data)
    flow = postback_data['message_type']
    if flow == 'edit':
        session['flow'] = EDIT
        edit_flow.handle_postback( event, session )

def flow_swicher(event, session):
        status_code = 1
        msg_type    = event.message.type

        if 'flow' not in session:
            status_code = -1
            return( status_code )
        else:
            flow = session.get('flow')

        if msg_type == 'text':
            if flow == REGISTER:
                register_flow.handle_text_message( event, session )
            elif flow == EDIT:
                edit_flow.handle_text_message( event, session )
            elif flow == SEARCH:
                search_flow.handle_text_message( event, session )
            elif flow == SHOW:
                show_flow.show_items(event, session)
            elif flow == VERIFY:
                # TODO : implement verify mode function
                pass
            else:
                print( 'ERROR : no flow matched' )
                status_code = -1

        if msg_type == 'image':
            if flow == REGISTER:
                register_flow.handle_image_message( event, session )
            elif flow == EDIT:
                edit_flow.handle_image_message( event, session )
            elif flow == SEARCH:
                search_flow.handle_image_message( event, session )
            elif flow == SHOW:
                show_flow.show_items(event, session)
            elif flow == VERIFY:
                # TODO : implement verify mode function
                pass
            else:
                print( 'ERROR : no flow matched' )
                status_code = -1

        if msg_type == 'location':
            if flow == REGISTER:
                register_flow.handle_location_message( event, session )
            elif flow == EDIT:
                edit_flow.handle_location_message( event, session )
            elif flow == SEARCH:
                search_flow.handle_location_message( event, session )
            elif flow == SHOW:
                show_flow.show_items(event, session)
            elif flow == VERIFY:
                # TODO : implement verify mode function
                pass
            else:
                print( 'ERROR : no flow matched' )
                status_code = -1

        return( status_code )

def show_command(event):
    reply_text = static_message.REQUEST_COMMAND_INPUT
    reply_msg  = TextSendMessage(text=reply_text)
    line_bot_api.reply_message(
        event.reply_token,
        reply_msg
    )

if __name__ == "__main__":
    app.run(port=8000)
