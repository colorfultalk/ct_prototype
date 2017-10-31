from linebot.models import TemplateSendMessage
from linebot.models.template import (
    CarouselTemplate, CarouselColumn, MessageTemplateAction, PostbackTemplateAction, URITemplateAction
)

def generate_carousel_message_for_item(items):
    """
    param items: Item Object
    """

    columns = []
    for i in range(len(items)):
        item = items[i]
        data = {
            'message_type': 'edit',
            'edit_item_index': i
        }
        column = CarouselColumn(text=item.description, thumbnail_image_url=item.image_url, actions=[
            PostbackTemplateAction(
                label='edit', data=str(data)),
        ])
        columns.append(column)

    carousel_template = CarouselTemplate(columns=columns)
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
    return(template_message)

