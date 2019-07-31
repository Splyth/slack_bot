import logging
import re
import request_helper as request

def get_return_text(raw_text):
    """
    Returns the response we are giving to slack
    :raw_text the raw message text we received
    :return: text we want to return to slack
    """

    user_id, message = parse_mention(raw_text)

    if message is None or message == "": return "Sorry I can't take any commands at the moment"
    command, query = parse_command(message)
    if query is None: return "Sorry I can't take any commands at the moment"
    return run_command(command, query)

def parse_mention(message_text):
    """
    Finds direct mentions (mentions at the front of a message)
    :param message_text: The message text
    :return: User ID mentioned, or if no direct mention, None
    """
    matches = re.search("^<@(|[WU].+?)>(.*)", message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)
    
def parse_command(message_text):
    """
    Finds the command and the query from the string
    :message_text the text we're searching
    :returns: command mentioned and query string
    """
    # we assume all commands are at the start of the line and end with the "me"
    # This will be revisited if commands are added that don't conform to that syntax
    # (e.g. image me, youtube me, gif me etc.)
    split = message_text.split("me",1)
    return split if len(split) == 2 else None
    
    
def run_command(command, query):
    """
    runs the passed in command and query
    :command what to run (image me, gif me etc)
    :query what to search for
    :Returns the result of the bot command
    """

    if command.strip() == "image":
        return request.submit_google_image_search_request(query.strip())
        
    if command.strip() == 'reverse':
        logging.warn(query)
        reverse = query[::-1]
        return reverse