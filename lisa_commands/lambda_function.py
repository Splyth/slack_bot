"""
Entry point. Called by the AWS lambda service.
"""
import json
import hashlib
import hmac
import os
import logging
from commands import message_text
import request_helper as request

def lambda_handler(data, _context):
    """
    Handle an incoming HTTP request from a Slack chat-bot.
    data: slack request object
    _context: context object from awk
    """
    if not valid_slack_request(data):
        return request.return_status()

    slack_event = json.loads(data['body'])['event']

    if "challenge" in slack_event:
        return slack_event["challenge"]

    if "bot_id" in slack_event: # Prevent bot from responding to itself
        return request.return_status()

    chat_action = 'chat.postMessage'
    if slack_event['type'] in ["message", "app_mention"]:
        # Get the ID of the channel where the message was posted.
        body = {
            'channel': slack_event["channel"],
            'text': message_text(slack_event),
            'unfurl_media': 'true',
            'unfurl_links': 'true'
        }
        if 'thread_ts' in slack_event:
            body['thread_ts'] = slack_event['thread_ts']

    # Currently the emoji that causes the delete logic is 'delet' (Yes it's mispelled)
    elif 'reaction_added' in slack_event['type'] and 'delet' in slack_event["reaction"]:
        chat_action = 'chat.delete'
        body = {
            'channel': slack_event['item']['channel'],
            'ts': slack_event['item']['ts']
        }

    request.submit_slack_request(body, chat_action)

    return request.return_status()

def valid_slack_request(data):
    """
    Did this request come from slack
    data - the data object (dict)
    """
    slack_signature = data['headers'].get('X-Slack-Signature', ' ')
    slack_request_timestamp = data['headers'].get('X-Slack-Request-Timestamp', ' ')
    request_body = data['body']
    message = f"v0:{slack_request_timestamp}:{request_body}".encode('utf-8')

    # Make the Signing Secret a bytestring too.
    slack_signing_secret = bytes(os.environ["SLACK_SECRET"], 'utf-8')

    # Create a new HMAC "signature", and return the string presentation.
    my_signature = 'v0=' + hmac.new(slack_signing_secret, message, hashlib.sha256).hexdigest()

    # Compare the the Slack provided signature to ours.
    # If they are equal, the request is legitment
    if hmac.compare_digest(my_signature, slack_signature):
        return True

    logging.warning(f"Verification failed. my_signature: {my_signature}")
    return False
