"""
handles parsing text and running the command specified from it
then gets the string to pass back to slack
"""

import logging
import random
import re
import json
import request_helper as request

def get_return_text(slack_event):
    """
    Returns the response we are giving to slack
    :raw_text the raw message text we received
    :message_user the user who sent the message
    :return: text we want to return to slack
    """
    _bot_user_id, message = parse_mention(slack_event['text'])
    return run_command(message, '', slack_event)

def parse_mention(message_text):
    """
    Finds direct mentions (mentions at the front of a message)
    :param message_text: The message text
    :return: User ID mentioned, or if no direct mention, None
    """
    matches = re.search("^<@(|[WU].+?)>(.*)", message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip().lower()) if matches else (None, None)

def commands():
    """
    returns the list of the commands, their description and the function they
    map to
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
            "description": 'use text after command to search for an image (use suffix "from [google|bing]" if you want to specify a search engine)'
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
    runs the passed in command and query
    :message_text contains text (sans bot mention)
    :slack_event the event from slack
    :Returns the result of the bot command
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
    query: query str
    slack_event: A dict of slack event information(unused for this function)
    returns the text to send back to slack
    """
    return request.anime_news_network_search('anime', query)

def call_the_cops(_query, slack_event):
    """
    query: query str (unused for this function)
    slack_event: A dict of slack event information
    returns the text to send back to slack

    """
    return 'You called? ' + image_me('anime cops from bing', slack_event)

def decide(query, _slack_event):
    """
    query: query str
    slack_event: A dict of slack event information(unused for this function)
    returns the text to send back to slack

    """
    return f"I'm gonna go with: {random.choice(query.split(' '))}"

def flip_coin(_query, _slack_event):
    """
    query: query str (unused for this function)
    slack_event: A dict of slack event information(unused for this function)
    returns the text to send back to slack

    """
    return f":coin: :coin: {random.choice(['HEADS', 'TAILS'])} :coin: :coin:"

def gif_me(query, _slack_event):
    """
    query: query str
    slack_event: A dict of slack event information(unused for this function)
    returns the text to send back to slack
    """
    return request.gify_search('gifs', query)

def help_command(_query, slack_event):
    """
    query: query str(unused for this function)
    slack_event: A dict of slack event information
    returns the text to send back to slack
    """

    # get users direct message channel id
    dm_id = json.loads(request.submit_slack_request({'user': slack_event['user']}, 'im.open'))['channel']['id']
    text = 'Known Commands\\\n'
    command_list = commands()

    for command in command_list.keys():
        line_text = '`' + command + '` - ' + command_list[command]['description'] + '\\\n'
        text = text + line_text
    data = {
        'channel': dm_id,
        'text': text
    }

    # Post list of commands to user in direct message
    request.submit_slack_request(data, 'chat.postMessage')
    # react to current message with an emoji (CURRENTLY NOT WORKING)
    # request.submit_slack_request({'name': 'diddy_boom_box'}, 'reactions.add')
    return ''

def image_me(query, slack_event):
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
        logging.warning('IN FROM')
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

def kill_me(query, _slack_event):
    """
    query: query str
    slack_event: A dict of slack event information(unused for this function)
    returns the text to send back to slack
    """
    return request.gify_search('gifs', 'kill me')

def manga_me(query, _slack_event):
    """
    query: query str
    slack_event: A dict of slack event information(unused for this function)
    returns the text to send back to slack
    """
    return request.anime_news_network_search('manga', query)

def put_it_back(_query, _slack_event):
    """
    query: query str(unused for this function)
    slack_event: A dict of slack event information(unused for this function)
    returns the text to send back to slack
    """
    return random.choice(["┬─┬ノ( º _ ºノ)", r"┬──┬ ¯\_(ツ)"])

def reverse_me(query, _slack_event):
    """
    query: query str
    slack_event: A dict of slack event information(unused for this function)
    returns the text to send back to slack
    """
    return query[::-1]

def shame(query, _slack_event):
    """
    query: query str
    slack_event: A dict of slack event information(unused for this function)
    returns the text to send back to slack
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
    query: query str
    slack_event: A dict of slack event information(unused for this function)
    returns the text to send back to slack
    """

def table_flip(_query, _slack_event):
    """
    query: query str (unused for this function)
    slack_event: A dict of slack event information(unused for this function)
    returns the text to send back to slack
    """
    return random.choice(["(ﾉಥ益ಥ）ﾉ ┻━┻ ", "┻━┻ ︵ヽ(`Д´)ﾉ︵ ┻━┻    ", "(ノಠ益ಠ)ノ彡┻━┻ ", "ヽ(｀Д´)ﾉ┻━┻", " (ノ≥∇))ノ┻━┻ ", "(╯°□°）╯︵ ┻━┻ "])

def wiki_me(query, _slack_event):
    """
    query: query str
    slack_event: A dict of slack event information(unused for this function)
    returns the text to send back to slack
    """
    return request.wikipedia_search(query)

def youtube_me(query, _slack_event):
    """
    query: query str
    slack_event: A dict of slack event information(unused for this function)
    returns the text to send back to slack
    """
    return request.youtube_search(query)
