"""
A wrapper to apply additional fun options to the response we send to slack 
(e.g. post with different name or icon image.)
"""

from datetime import datetime

def apply_additional_message_options(body):
    """
    Lisa likes to get gussied up for special occasions. So we replace her
    name and icon in the response that appears in slack.

    body - response body (dict)
    """

    # During October for Halloween
    if datetime.now().month == 10:
        body['username'] ='Witchy Lisa'
        body["icon_url"] = 'https://raw.githubusercontent.com/Splyth/slack_bot/master/icons/Lisa_Halloween.png'
    # During December for Christmas
    elif datetime.now().month == 12:
        body['username'] ='Santa Lisa'
        body["icon_url"] = 'https://raw.githubusercontent.com/Splyth/slack_bot/master/icons/Lisa_Christmas.png'
        
    return body
