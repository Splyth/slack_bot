import logging
import json
from commands import get_return_text
import request_helper as request

def lambda_handler(data, context):
    """
    Handle an incoming HTTP request from a Slack chat-bot.
    """

    slack_event = json.loads(data['body'])['event']

    if "challenge" in slack_event:
        return slack_event["challenge"]

    if "bot_id" in slack_event: # Prevent bot from responding to itself
        logging.warn("Ignore bot event")
        return request.return_status()
    
    text = get_return_text(slack_event['text'])
    
    # # Get the ID of the channel where the message was posted.
    channel_id = slack_event["channel"]
    
    data = {
        'channel': channel_id,
        'text': text
    }
    
    logging.warn(data)
    request.submit_slack_request(json.dumps(data).encode('utf-8'))
    return request.return_status()
