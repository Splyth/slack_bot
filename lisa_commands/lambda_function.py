"""
Entry point. Called by the AWS lambda service.
"""
import logging
import json
from commands import get_return_text
import request_helper as request

def lambda_handler(data, _context):
    """
    Handle an incoming HTTP request from a Slack chat-bot.
    data: slack request object
    _context: context object from awk
    """

    slack_event = json.loads(data['body'])['event']

    if "challenge" in slack_event:
        return slack_event["challenge"]

    if "bot_id" in slack_event: # Prevent bot from responding to itself
        logging.warning("Ignore bot event")
        return request.return_status()

    chat_action = 'chat.postMessage'
    if 'app_mention' in slack_event['type']:
        # Get the ID of the channel where the message was posted.
        
        data = {
            'channel': slack_event["channel"],
            'text': get_return_text(slack_event['text'], slack_event['user'])
        }
    # Currently the emoji that causes the delete logic is 'delet' (Yes it's mispelled)
    elif 'reaction_added' in slack_event['type'] and 'delet' in slack_event["reaction"]:
        chat_action = 'chat.delete'
        data = {
            'channel': slack_event['item']['channel'],
            'ts': slack_event['item']['ts']
        }

    request.submit_slack_request(data, chat_action)
    return request.return_status()
