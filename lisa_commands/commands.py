"""
handles parsing text and running the command specified from it
then gets the string to pass back to slack
"""

import random
import re
import json
import request_helper as request

def message_text(slack_event):
    """
    Gets text to send back to slack

    slack_event - a dictionary containing slack event information

    Returns the message text we will send to Slack
    """

    _bot_user_id, message = parse_mention(slack_event['text'])
    return run_command(message, '', slack_event)

def parse_mention(text):
    """
    Finds direct mentions (mentions at the front of a message)

    text - a dictionary containing slack event information

    Returns an 2 element tuple of [USER_ID, rest_of_message]
    """

    matches = re.search("^<@(|[WU].+?)>(.*)", text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip().lower()) if matches else (None, None)

def commands():
    """
    Gets the known command list

    Returns a dictionary of known commands
    """

    return {
        'anime me': {
            'function': anime_me,
            "description": "use text after command to query anime news network for anime info"
        },
        'call the cops': {
            'function': call_the_cops,
            "description": "responds with an image of anime cops with the caption You Called?"
        },
        'decide': {
            'function': decide,
            "description": "picks one of the words at radom in the text after command"
        },
        'flip coin': {
            'function': flip_coin,
            "description": "use text after command to query giphy for gifs"
        },
        'gif me': {
            'function': gif_me,
            "description": "use text after command to query giphy for gifs"
        },
        'help': {
            'function': help_command,
            "description": "send user a direct message to user with list of commands"
        },
        'image me': {
            'function': image_me,
            "description": """
                use text after command to search for an image
                You can specify a search engine to use by appending
                "from google" or "from bing" to query google or bing
                respectively. Otherwise one is chosen at random
            """
        },
        'kill me': {
            'function': kill_me,
            "description": ' responds with a gif with kill me as a search'
        },
        'manga me': {
            'function': manga_me,
            "description": "use text after command to query anime news network for manga info"
        },
        'put it back': {
            'function': put_it_back,
            "description": "when you are done flipping the table and it's time to clean up"
        },
        'reverse me': {
            'function': reverse_me,
            "description": "reverses text after command"
        },
        'shame': {
            'function': shame,
            "description": 'shame the text after command'
        },
        'sticker me': {
            'function': sticker_me,
            "description": "uses text after command to query giphey for stickers"
        },
        'table flip': {
            'function': table_flip,
            "description": "when you gotta flip a table"
        },
        'wiki me': {
            'function': wiki_me,
            "description": "use text after command to query wikipedia"
        },
        'youtube me': {
            'function': youtube_me,
            "description": "use text after command to query youtube"
        },
    }

def run_command(command, query, slack_event):
    """
    Attempts to run the passed in command. This is a recursive function.
    If it's unable to run the command it will chop off the last word add it
    to the query argument and try again until it either finds a command to run
    or the command argument is empty.

    command - a string containing the command to search for
    query - the query to send to the command
    slack_event - a dictionary containing slack event information

    Returns the message text to send back to slack
    """

    command = command.lower().strip()
    if command in commands().keys():
        text = commands()[command]['function'](query, slack_event)
        if text is None:
            text = 'Sorry! No results found!'
        return text

    if command and command.strip().count(' ') > 0:
        command, query_word = command.rsplit(' ', 1)
        return run_command(command, query_word + ' ' + query, slack_event)

    return "Sorry I don't know that command. To see all my commands use `help`"

def anime_me(query, _slack_event):
    """
    query - query str
    slack_event - A dict of slack event information(unused for this function)

    Returns a link to info on an anime series
    """

    return request.anime_news_network_search('anime', query)

def call_the_cops(_query, slack_event):
    """
    query - query str (unused for this function)
    slack_event - A dict of slack event information

    Returns an image link with the caption "You called?"
    """

    return 'You called? ' + image_me('anime cops from bing', slack_event)

def decide(query, _slack_event):
    """
    query - query str
    slack_event - A dict of slack event information(unused for this function)

    Returns the message: "I'm going to go with" followed by a random word from the query
    """

    return f"I'm gonna go with: {random.choice(query.split(' '))}"

def flip_coin(_query, _slack_event):
    """
    query - query str (unused for this function)
    slack_event - A dict of slack event information(unused for this function)

    Returns HEADS or TAILS sourrounded by coin emojis
    """

    return f":coin: :coin: {random.choice(['HEADS', 'TAILS'])} :coin: :coin:"

def gif_me(query, _slack_event):
    """
    query - query str
    slack_event - A dict of slack event information(unused for this function)

    Returns a link to a gif
    """
    return request.gify_search('gifs', query)

def help_command(_query, slack_event):
    """
    Sends a private message to user containing information on commands known

    query - query str(unused for this function)
    slack_event - A dict of slack event information

    Returns empty string
    """

    # get users direct message channel id
    dm_request = json.loads(request.submit_slack_request({'user': slack_event['user']}, 'im.open'))
    dm_id = dm_request['channel']['id']

    text = "Known Commands:\n"
    for command, info, in commands().items():
        line_text = '`' + command + '` - ' + info['description'] + "\n"
        text = text + line_text

    # Post list of commands to user in direct message
    request.submit_slack_request({'channel': dm_id, 'text': text}, 'chat.postMessage')

    # react to current message with an emoji
    data = {
        'name': 'diddy_boom_box',
        'channel': slack_event["channel"],
        'timestamp': slack_event['ts'],
    }
    request.submit_slack_request(data, 'reactions.add')

    return ''

def image_me(query, _slack_event):
    """
    Gets an image link for Google or Bing. I am on free teirs so I can only send
    ~100 requests to google and ~100 requests to Bing a day. To avoid hitting usage
    caps I randomly pick one unless the user specifies "from google" or "from bing"
    at the end of their query

    query - query str(unused for this function)
    slack_event - A dict of slack event information

    Returns an image link (with optional caption)
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

        text = 'Sorry no results found.' if text is None else text

        return text
    # If the user didn't specify a search engine we just pick one
    search_engine = random.choice(['google', 'bing'])
    if search_engine == 'google':
        return "From Google: " + request.google_image_search(query)
    return "From Bing: " + request.bing_image_search(query)

def kill_me(_query, _slack_event):
    """
    query - query str (unused for this function)
    slack_event - A dict of slack event information (unused for this function)

    Returns a link to a gif
    """
    return request.gify_search('gifs', 'kill me')

def manga_me(query, _slack_event):
    """
    query - query str
    slack_event - A dict of slack event information(unused for this function)

    Returns a link to manga series info
    """
    return request.anime_news_network_search('manga', query)

def put_it_back(_query, _slack_event):
    """
    query - query str
    slack_event - A dict of slack event information(unused for this function)

    Returns a randomly selected reverse_table_flip ascii art
    """
    return random.choice(["┬─┬ノ( º _ ºノ)", r"┬──┬ ¯\_(ツ)"])

def reverse_me(query, _slack_event):
    """
    query - query str
    slack_event - A dict of slack event information(unused for this function)

    Returns the query string in reverse order
    """
    return query[::-1]

def shame(query, _slack_event):
    """
    query - query str
    slack_event - A dict of slack event information(unused for this function)

    Returns the query with some additional text shaming it.
    """

    user = query.strip().upper()
    return random.choice([
        'Shame on you! ' + user + 'You should know better!',
        user + ' ಠ_ಠ',
        user + ' You have made a mockery of yourself. Turn in your weeabo credentials!',
        user + ' :blobdisapproval:',
        user + ' :disappoint:',
        user + ' you did bad and you should feel bad',
        user + ' :smh:',
    ])

def sticker_me(query, _slack_event):
    """
    query - query str
    slack_event - A dict of slack event information(unused for this function)

    Returns a link to a sticker
    """

    return request.gify_search('stickers', query)

def table_flip(_query, _slack_event):
    """
    query - query str(unused for this function)
    slack_event - A dict of slack event information(unused for this function)

    Returns the a random table_flip ascii art
    """

    return random.choice([
        "(ﾉಥ益ಥ）ﾉ ┻━┻ ",
        "┻━┻ ︵ヽ(`Д´)ﾉ︵ ┻━┻    ",
        "(ノಠ益ಠ)ノ彡┻━┻ ",
        "ヽ(｀Д´)ﾉ┻━┻",
        " (ノ≥∇))ノ┻━┻ ",
        "(╯°□°）╯︵ ┻━┻ "
    ])

def wiki_me(query, _slack_event):
    """
    query - query str
    slack_event - A dict of slack event information(unused for this function)

    Returns a link to wiki page found by search
    """
    return request.wikipedia_search(query)

def youtube_me(query, _slack_event):
    """
    query - query str
    slack_event - A dict of slack event information(unused for this function)

    Returns a link to youtube video found by search
    """
    return request.youtube_search(query)
