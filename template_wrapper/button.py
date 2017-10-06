from linebot.models import TemplateSendMessage
from linebot.models.template import ButtonsTemplate
from linebot.models.template import MessageTemplateAction

sample_actions = [ MessageTemplateAction( label = 'test', text = 'sample' ) ]

def generate_button_message(text, thumbnail_image_url, actions = sample_actions):

    """
    :param actions: Action when tapped.
    Max: 4
    :type actions: list[T <= :py:class:`linebot.models.template.TemplateAction`]
    """

    button_template = ButtonsTemplate(
                text = text,
                thumbnail_image_url = thumbnail_image_url,
                actions = actions
            )
    button_message = TemplateSendMessage(
                alt_text = 'Buttons alt text',
                template = button_template
            )
    return( button_message )

