import logging
import random
import re
import request_helper as request

def get_return_text(raw_text):
    """
    Returns the response we are giving to slack
    :raw_text the raw message text we received
    :return: text we want to return to slack
    """

    user_id, message = parse_mention(raw_text)

    if message is None or message == "": return "What do you need? I know `image me`, and `reverse me`"
    command, query = parse_command(message)
    if command is None: return "Sorry I don't know that command. I know `image me`, and `reverse me`"
    if query is None: return "Sorry I don't usderstand your request."
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
    return split if len(split) == 2 else [None, None]
    
    
def run_command(command, query):
    """
    runs the passed in command and query
    :command what to run (image me, gif me etc)
    :query what to search for
    :Returns the result of the bot command
    """

    split = query.rsplit(' ', 2)

    if command.strip() == "image":
        # If the user added 'from google' or 'from bing' to end of command
        # use that engine.
        if split[1].lower() == 'from':
            if split[2].lower() == 'google':
                return request.google_image_search(query.strip())
            elif split[2].lower() == 'bing':
                return request.google_image_search(query.strip())

        # If the user didn't specify a search engine we just pick one
        search_engine = random.choice(['google', 'bing'])
        if search_engine == 'google':
            return "From Google: " + request.google_image_search(query.strip())
        else:
            return "From Bing: " + request.bing_image_search(query.strip())
        
    if command.strip() == 'reverse':
        logging.warn(query)
        reverse = query[::-1]
        return reverse
        
    return "Sorry I don't know that command: I know `image me`, or `reverse me`"
