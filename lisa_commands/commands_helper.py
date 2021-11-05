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

    if query in ['ME', '<@'+slack_event['user']+'>']:
        return 'self'
    if query == '<@'+request.dynamodb_query('bot_id', {'id':{'S': '1'}})['Item']['bot_id']['S']+'>':
        return 'bot'

    return 'other'

def emojify(char_patterns, emoji):
    """
    Performs the heavy lifting of emojifying text.

    char_patterns - the array of values retrieved from emojify_constants for the requested query text
    """
    response = []
    # Each line of the response must be arranged individually and in sequence to make the vertical patterns across horizontal lines.
    for x in range(5):
        line = []
        # For each character in the query, take the string representing the current line of each character pattern in the query, and arrange them sequentially.
        for pattern in char_patterns:
            line.append(pattern[x])
        # After constructing a line, join its elements together, using 0 as a separator, then add it to array of lines in the response.
        response.append("0".join(line))
        if len(response[x]) > 64:  # Max emojis per line tested on a macbook. TODO: Investigate possibility of "multi-line" parsing
            return "Sorry, that text is a little too long to be emojified properly! Try a shorter message."
    return "\n".join(response).replace("0", ":nothing:").replace("1", emoji)
