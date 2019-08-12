"""
handles parsing text and running the command specified from it
then gets the string to pass back to slack
"""

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
    _user_id, message = parse_mention(raw_text)
    command, query = parse_command(message)

    return run_command(command.strip(), query)

def parse_mention(message_text):
    """
    Finds direct mentions (mentions at the front of a message)
    :param message_text: The message text
    :return: User ID mentioned, or if no direct mention, None
    """
    matches = re.search("^<@(|[WU].+?)>(.*)", message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip().lower()) if matches else (None, None)

def parse_command(message_text):
    """
    Finds the command and the query from the string
    :message_text the text we're searching
    :returns: command mentioned and query string
    """

    # for commands using the '* me' syntax (e.g. image me, youtube me, gif me etc.)
    split = message_text.split(" me ", 1)
    if len(split) == 2: return split

    # If command isn't a '* me' command assume a single word command (e.g. decide, flipcoin, etc)
    split = message_text.split(' ', 1)
    if len(split) == 1: return [split[0].strip(), '']

    logging.warning(split)
    # if command is a single word command with text (e.g. decide, shame, etc)
    if len(split) == 2: return split

    # else no command
    return ['', '']


def run_command(command, query):
    """
    runs the passed in command and query
    :command what to run (image me, gif me etc)
    :query what to search for
    :Returns the result of the bot command
    """

    text = ''
    if not command: text = 'Did you need something?'
    if command in ["anime", 'manga']: text = request.anime_news_network_search(command, query)
    elif command in ["image", "img"]: text = fetch_image(query)
    elif command == 'reverse': text = query[::-1]
    elif command == 'youtube': text = request.youtube_search(query)
    elif command in ['wiki', 'wikipedia']: text = request.wikipedia_search(query)
    elif command in ['gif', 'sticker']: text = request.gify_search(command, query)
    elif command == 'tableflip': text = random.choice(["(ﾉಥ益ಥ）ﾉ ┻━┻ ", "┻━┻ ︵ヽ(`Д´)ﾉ︵ ┻━┻    ", "(ノಠ益ಠ)ノ彡┻━┻ ", "ヽ(｀Д´)ﾉ┻━┻", " (ノ≥∇))ノ┻━┻ ", "(╯°□°）╯︵ ┻━┻ "])
    elif command == 'putitback': text = random.choice(["┬─┬ノ( º _ ºノ)", r"┬──┬ ¯\_(ツ)"])
    elif command == 'flipcoin': text = f":coin: :coin: {random.choice(['HEADS', 'TAILS'])} :coin: :coin:"
    elif command == 'decide': text = f"I'm gonna go with: {random.choice(query.split(' '))}"
    elif command == 'callthecops': text = 'You called? ' + fetch_image('anime cops from bing')
    elif command == 'kill': text = request.gify_search('gif', 'kill me')
    elif command == 'shame':
        user = query.strip().upper()
        text = random.choice([
            'Shame on you! ' + user + 'You should know better!',
            user + ' ಠ_ಠ',
            user + ' You have made a mockery of yourself. Turn in your weeabo credentials!',
            user + ' :blobdisapproval:',
            user + ' :disappoint:',
            user + ' you did bad and you should feel bad',
            user + ' :smh:',
        ])
    else: text = "Sorry I don't know that command. Try `image me` `youtube me` or `reverse me`"

    if not text: text = "Sorry no results found"

    return text

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
    if len(split) > 1 and split[1].lower() == 'from':
        text = None
        if split[2].lower() == 'google':
            text = request.google_image_search(query)
        elif split[2].lower() == 'bing':
            text = request.bing_image_search(query)

        if text is None: text = 'Sorry no results found.'
        return text
    # If the user didn't specify a search engine we just pick one
    search_engine = random.choice(['google', 'bing'])
    if search_engine == 'google':
        return "From Google: " + request.google_image_search(query)

    return "From Bing: " + request.bing_image_search(query)
