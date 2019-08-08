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
    if user_id == None and message == None: return non_command_messages(raw_text)

    command, query = parse_command(message)

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
    if type(message_text) == str:
        split = message_text.split(" me ",1)
        if len(split) == 2: return split

    return [None, None]
    
def non_command_messages(text):
    """
    Handles custom responses that aren't direct commands
    Will update as I find things that I think are funny
    text: the string we were passed from user
    """
    
    return None

def run_command(command, query):
    """
    runs the passed in command and query
    :command what to run (image me, gif me etc)
    :query what to search for
    :Returns the result of the bot command
    """

    if type(command) == str: command = command.strip() 
    if type(query) == str: query = query.strip()

    if command == "anime":
        return request.anime_search(query)
    elif command == 'manga':
        return request.manga_search(query)
    elif command == "image" or command == "img":
        return fetch_image(query)
    elif command == 'reverse':
        return query[::-1]
    elif command == 'youtube':
        text = request.youtube_search(query)
        if text == None: text = 'Sorry no results found.'
        return text
    elif command == 'wiki' or command == 'wikipedia':
        return request.wikipedia_search(query)
    return "Sorry I don't know that command. Try `image me` `youtube me` or `reverse me`"
    
def fetch_image(query):
    """
    fetches an image link we return as the text.
    Because I'm using a free teir I am very limited
    on space so I have added google and bing as places
    to source images from
    """
    split = query.rsplit(' ', 2)
    # If the user added 'from google' or 'from bing' to end of command
    # use that engine.
    logging.warn(split)
    if len(split) > 1 and split[1].lower() == 'from':
        text = None
        if split[2].lower() == 'google':
            text = request.google_image_search(query)
        elif split[2].lower() == 'bing':
            text = request.bing_image_search(query)

        if text == None: text = 'Sorry no results found.' 
        return text
    # If the user didn't specify a search engine we just pick one
    search_engine = random.choice(['google', 'bing'])
    if search_engine == 'google':
        return "From Google: " + request.google_image_search(query)
    else:
        return "From Bing: " + request.bing_image_search(query)
    
