"""
To keep the commands file clean any shared or supplemental logic should be
place here.
"""

import request_helper as request

def karma_requested_for(query, slack_event):
    """
    Used to determine any special karma cases (e.g. someone wants to give themselves karma)

    query - query str (unused for this function)
    slack_event - A dict of slack event information

    returns one of the following: self, bot, or other
    """

    if query in ['ME', query == '<@'+slack_event['user']+'>']:
        return 'self'
    if query == '<@'+request.dynamodb_query('bot_id', {'id':{'S': '1'}})['Item']['bot_id']['S']+'>':
        return 'bot'

    return 'other'
