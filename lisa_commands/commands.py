"""
handles parsing text and running the command specified from it
then gets the string to pass back to slack
"""

import random
import re
import json
import logging
import commands_helper
import request_helper as request
import collections
import emojify_constants
import magic_parser

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
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

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
            "description": "Returns either HEADS or TAILS"
        },
        'gif me': {
            'function': gif_me,
            "description": "use text after command to query google for gifs"
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
            "description": 'removes person who invoked the command from current channel'
        },
        'manga me': {
            'function': manga_me,
            "description": "use text after command to query anime news network for manga info"
        },
        'most praised':{
            'function': most_praised,
            'description': 'list the highest karma earners'
        },
        'most shamed': {
            'function': most_shamed,
            'description': 'list lowest karma earners'
        },
        'my karma': {
            'function': my_karma,
            "description": "Shows user their karma"
        },
        'praise': {
            'function': praise,
            "description": 'praise the text after command and adds karma'
        },
        'put it back': {
            'function': put_it_back,
            "description": "when you are done flipping the table and it's time to clean up"
        },
        'poll me': {
            'function': poll_me,
            "description": """
            Starts a poll with the given options. First argument is the title of the poll, further arguments are the
            poll options. Input should be formatted as comma-separated values. Max of 9 options.
            Usage examples:
            `@Lisa poll me Lunch?, Pizza, Burgers, Mexican`
            `@Lisa poll me What's the better series?, Star Wars, Star Trek`
            """
        },
        'reverse me': {
            'function': reverse_me,
            "description": "reverses text after command"
        },
        'roll me': {
            'function': roll_me,
            "description": """
            Roll the dice! Usage:
            `roll me`: defaults to rolling 1d6
            `roll me 3d6`: rolls three d6es
            `roll me 4d20`: rolls four d20s :snoop:
            Maximum die size: d1000
            Maximum die count: 300
            """
        },
        'roll': {
            'function': roll_me,
            "description": 'convenience alias for `roll me`'
        },
        'shame': {
            'function': shame,
            "description": 'shame the text after command and removes karma'
        },
        'spotify me': {
            'function': spotify_me,
            "description": """
            Use text after command to query spotify for a song, album, or artist. Must designate
            what type you are searching for.
            Examples:
                spotify me track Snow Halation
                spotify me album The Life of Pablo
                spotify me artist Streetlight Manifesto
                spotify me playlist Today's Top Hits
            """
        },
        'song me': {
          'function': song_me,
            "description": """
            Shortcut for 'spotify me track.'
            """
        },
        'album me': {
            'function': album_me,
            "description": """
        Shortcut for 'spotify me album.'
        """
        },
        'artist me': {
            'function': artist_me,
            "description": """
        Shortcut for 'spotify me artist.'
        """
        },
        'playlist me': {
            'function': playlist_me,
            "description": """
        Shortcut for 'spotify me playlist.'
        """
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
        'emojify me': {
            'function': emojify_me,
            "description": "Write words made of emoji! First emoji found in the command is used, subsequent emojis are treated as text."
        },
        'magic me': {
            'function': magic_me,
            "description": "Get data on a Magic: the Gathering card from Scryfall."
        },
        'card me': {
            'function': magic_me,
            "description": "Alias for 'magic me'"
        }
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

    check_command = command.lower().strip()
    if check_command in commands().keys():
        text = commands()[check_command]['function'](query.strip(), slack_event)
        if text is None:
            text = no_result_found_response()
        return text

    if check_command and check_command.strip().count(' ') > 0:
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

    return 'You called? ' + image_me('anime police cops', slack_event)

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
    return request.gif_search(query)

def help_command(_query, slack_event):
    """
    Sends a private message to user containing information on commands known
    query - query str(unused for this function)
    slack_event - A dict of slack event information
    Returns empty string
    """


    # get users direct message channel id
    dm_request = json.loads(request.submit_slack_request({'user': slack_event['user']}, 'im.open'))
    dm_id = request.direct_message_channel_search(slack_event)


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
    Gets an image link from Google
    query - query str(unused for this function)
    slack_event - A dict of slack event information
    Returns an image link (with optional caption) or None
    """

    img_link = request.google_image_search(query)
    if img_link:
        return img_link
    return None

def kill_me(_query, slack_event):
    """
    query - query str (unused for this function)
    slack_event - A dict of slack event information
    Returns nothing
    """

    # kick user from channel
    data = {
        'channel': slack_event["channel"],
        'user': slack_event['user'],
    }
    response = json.loads(request.submit_slack_request(data, 'conversations.kick', 'USER'))

    # DM User with fun line
    if response['ok']:
        text = random.choice([
            'By order of the SDF Armed Forces you have been killed',
            'Ask not for whom the bell tolls. It tolls for thee ~ John Donne',
            "We all have but one life to live. Well you do. I'm a bot, and I have backups",
            ('A coward dies a thousand times before their death, but the valiant '
             'taste of death but once.\n ~ William Shakespeare'),
            ('Do not go gentle into that good night\n'
             'Old age should burn and rave at close of day; \n'
             'Rage, rage against the dying of the light. \n ~ Dylan Thomas'),
            ('Life is cruel. Of this I have no doubt. '
             'One can only hope that one leaves behind a lasting legacy. '
             'But so often, the legacies we leave behind...are not the ones we intended.\n'
             '~ Queen Myrrah ~ Gears of War 2'),
            ('Death is inevitable. Our fear of it makes us play safe, blocks out emotion. '
             "It's a losing game. Without passion, you are already dead. \n~Max Payne"),
            ('The ending isn’t any more important than any of the moments leading to it.\n'
             '~ Dr Rosalene (To The Moon)'),
            "Omae wa Mou Shindeiru!",
            ('Stop pitying yourself. Pity yourself, and life becomes an endless nightmare.\n'
             '~ Osamu Dazai (Bungo Stray Dogs)'),
            "Heghlu’meH QaQ jajvam ~ Klingon Proverb",
            "batlhbIHeghjaj ~ Klingon Proverb"
        ])
    elif response['error'] == 'cant_kick_from_general':
        text = "The top brass told me I can't kick people from workspaces anymore. :pouting_cat:"
    else:
        text = f"I can't get that done. I get this error: `{response['error']}`"

    dm_id = request.direct_message_channel_search(slack_event)
    request.submit_slack_request({'channel': dm_id, 'text': text}, 'chat.postMessage')

    # React to users message asking the bot to kill them
    data = {
        'name': 'dead4',
        'channel': slack_event["channel"],
        'timestamp': slack_event['ts'],
    }
    request.submit_slack_request(data, 'reactions.add')

    return ''

def manga_me(query, _slack_event):
    """
    query - query str
    slack_event - A dict of slack event information(unused for this function)
    Returns a link to manga series info
    """
    return request.anime_news_network_search('manga', query)

def most_praised(_query, _slack_event):
    table = collections.defaultdict(list)
    for record in request.dynamodb_scan('karma_scores')['Items']:
        table[int(record['karma']['N'])].append(record['user']['S'])

    sorted_records = collections.OrderedDict(sorted(table.items(), reverse=True))
    
    text = ['THE PRAISED :praise_the_sun: \n']
    for karma, users in sorted_records.items():
        for user in users:
            if len(text) == 11:
                break
            
            text.append("{}. {}   Karma: {} \n".format(len(text), user, karma))
    
    return ">".join(text)

def most_shamed(_query, _slack_event):
    table = collections.defaultdict(list)
    for record in request.dynamodb_scan('karma_scores')['Items']:
        table[int(record['karma']['N'])].append(record['user']['S'])

    sorted_records = collections.OrderedDict(sorted(table.items()))
    
    text = ['THE SHAMED :shame_bell: \n']
    for karma, users in sorted_records.items():
        for user in users:
            if len(text) == 11:
                break
            
            text.append("{}. {}   Karma: {} \n".format(len(text), user, karma))
    
    return ">".join(text)

def my_karma(_query, slack_event):
    """
    _query - query str (unused for this function)
    slack_event - A dict of slack event information(unused for this function)
    Returns the users karma:
    """
    text = random.choice([
        'Sure thing! Your karma is: ',
        "Let's see. Your current karma is: ",
        'I have your karma at: ',
        "Looks like your karma is: ",
    ])

    return text + request.dynamodb_query(
        'karma_scores',
        {'user': {'S': '<@' + slack_event['user'] + '>'}}
    )['Item']['karma']['N']

def praise(query, slack_event):
    """
    query - query str
    slack_event - A dict of slack event information
    Returns the query with some additional text praising it.
    """
    if len(query) == 0:
        return ":praise_the_sun:"
    query = query.strip().upper()
    requested_for = commands_helper.karma_requested_for(query, slack_event)

    if requested_for == 'self':
        user = '<@' + slack_event['user'] + '>'
        return random.choice([
            user + " Isn't that a little like high fiving yourself?",
            user + ' That seems a little narcissistic...',
            user + " I don't really like doing that.",
            user + " I'm an XO on a space battleship, Who really deservers praise here?",
            user + " Do something someone else thinks worthy of praise and we'll talk",
        ])

    request.dynamodb_update(
        'karma_scores',
        {'user':{'S':query}},
        'ADD karma :val',
        {':val':{'N':'1'}}
    )

    if requested_for == 'bot':
        user = '<@' + slack_event['user'] + '>'
        text = random.choice([
            user + " Thanks! That's so nice of you to say",
            user + ' Aww thanks!',
            user + ' :blobblush:',
            user + " :02blush: That's kind of you!",
            user + ' Oh, you! :meowblush:'
        ])

        text = text + '\n' +' My Karma is now: '

    else:
        user = query
        text = random.choice([
            'Great job! ' + user + ' I knew you could do it!',
            user + ' you have brought honor to your family name.',
            user + ' it takes a special person to accomplish what you have accomplished.',
            ':praise_the_sun::praise_the_sun:' + user + ' :praise_the_sun::praise_the_sun:',
            user + ' :drake_approves:',
            user + ' :chika-approves:',
            user + ' :batman-approves:',
            user + ' you have done well, and you should be proud.'
        ])

        text = text + '\n' + user + ' Your Karma is now: '
    return text + request.dynamodb_query(
        'karma_scores',
        {'user': {'S': query}}
    )['Item']['karma']['N']

def poll_me(query, slack_event):
    """
    Makes a poll! Max of 9 options, comma separated.
    :param query: query str
    :param slack_event: A dict of slack event information
    :return: A poll with the given options in the query string
    """
    if len(query) == 0:
        return "You want me to create a poll without giving me a question or options? Give me something to work with here!"
    tokens = query.split(',')
    number_emojis = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:"]

    if len(tokens) == 1:
        return "Polls aren't open-ended questions, you'll need to provide at least two answer choices!"
    elif len(tokens) == 2:
        return "A poll with only one option? Sounds like you've already made up your mind..."
    elif len(tokens) > 10:
        return "That's too many options, you'll give everyone decision paralysis! Maximum of 9 poll options allowed."

    response_text = "POLL: "
    response_text += tokens.pop(0)
    for i in range(0, len(tokens)):
        response_text += "\n" + number_emojis[i] + ": " + tokens[i].strip()

    return response_text

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

def roll_me(query, _slack_event):
    """
    rolls the dice. maximum die size: d1000, maximum number of dice: 300
    :param query: query string
    :param _slack_event: a dict of slack event information (unused for this function)
    :return: a string with the result
    """
    # lisa can have little a easter egg, as a treat.
    # video is the smoke weed every day song
    if query == "a joint" or query == "a blunt":
        return ":mokeweed::snoop: https://www.youtube.com/watch?v=JcBIzuuIdOA :mokeweed::snoop:"

    if query == "":
        roll = [1, 6]
    else:
        roll = query.split('d', 1)
    if len(roll) != 2:
        return "Not a valid roll. Valid examples: `roll me 1d8` or `roll me 3d10`."
    try:
        dice = int(roll[0])
        if dice > 300:
            return "Woah now, slow your roll! That's _way_ too many dice. I can only roll up to 300 dice at a time."
        sides = int(roll[1])
        if sides > 1000:
            return "Woah now, slow your roll! That die is _way_ too big. I can only roll dice with sides <= 1000."
    except ValueError:
        return "Not a valid roll. Valid examples: `roll me 1d8` or `roll me 3d10`."

    rolls = []
    for x in range(dice):
        rolls.append(random.randint(1, sides))

    result = "Rolling " + str(dice) + "d" + str(sides) + "."
    if 1 < dice <= 20:
        # for lower numbers of dice, the results of each roll are shown individually.
        # skipped for larger amounts of dice so as to not clog the screen.
        result += " Results: "
        result += str(rolls)
        result += " = " + str(sum(rolls))
    else:
        result += " Result: " + str(sum(rolls))
    return result


def shame(query, slack_event):
    """
    query - query str
    slack_event - A dict of slack event information
    Returns the query with some additional text shaming it.
    """
    query = query.strip().upper()
    requested_for = commands_helper.karma_requested_for(query, slack_event)

    if requested_for == 'self':
        user = '<@' + slack_event['user'] + '>'
        return random.choice([
            user + " You shouldn't be so hard on yourself :ganbatte:",
            user + " :02pat: There there I'm sure it'll get better",
            user + " :meowhug: It's not so bad I promise things will get better.",
            ("```\nWhat though life conspire to cheat you,\n"
             "Do not sorrow or complain.\n"
             "Lie still on the day of pain,\n\n"
             "And the day of joy will greet you.\n"
             "Hearts live in the coming day.\n"
             "There's an end to passing sorrow.\n\n"
             "Suddenly all flies away,\n"
             "And delight returns tomorrow.\n"
             "~ A.S. Pushkin\n```"),
            (user + " Life is not always a matter of holding good cards,"
             "but sometimes, playing a poor hand well ~ Jack London"),
        ])

    request.dynamodb_update(
        'karma_scores',
        {'user':{'S':query}},
        'ADD karma :val',
        {':val':{'N':'-1'}}
    )

    if requested_for == 'bot':
        user = '<@' + slack_event['user'] + '>'
        text = random.choice([
            user + " I'm sorry I've offended you so :bow:",
            user + ' Failure is not the end, I will endeavor to do better',
            user + ':sorry: I sincerely apologize! :bow: ',
            user + "You learn more from defeat. Still doesn't make it hurt any less. :sad:",
            user + ":sadlute:"
        ])

        text = text + '\n' +' My Karma is now: '

    else:
        user = query
        text = random.choice([
            'Shame on you! ' + user + ' You should know better!',
            user + ' ಠ_ಠ',
            user + ' You have made a mockery of yourself. Turn in your weeaboo credentials!',
            user + ' :blobdisapproval:',
            user + ' :disappoint:',
            user + ' you did bad and you should feel bad',
            user + ' :smh:',
        ])
        text = text + '\n' + user + ' Your Karma is now: '

    return text + request.dynamodb_query(
        'karma_scores',
        {'user': {'S': query}}
    )['Item']['karma']['N']

def spotify_me(query, _slack_event, query_type=None):
    """
    :param query: query str
    :param _slack_event: A dict of slack event information(unused for this function)
    :param query_type: An optional string used for passing in the query type of the spotify search (song, album, artist,
    playlist). If no query type is passed, the query type will be parsed used the first word of the query.
    Returns a link to spotify media item found by search
    """
    if query_type is None:
        query_type, search_query = query.split(' ', 1)
    else:
        search_query = query

    query_types = ['track', 'album', 'artist', 'playlist']
    if query_type not in query_types:
        return f'Invalid Media Type for search. Valid types are {" ".join(query_types)}'
    return request.spotify_search(query_type, search_query)

def song_me(query, _slack_event):
    """
    :param query: query str
    :param _slack_event: a dict of slack event information(unused for this function)
    :return: a link to spotify song item found by search
    """
    return spotify_me(query, _slack_event, 'track')

def album_me(query, _slack_event):
    """
    :param query: query str
    :param _slack_event: a dict of slack event information(unused for this function)
    :return: a link to spotify album item found by search
    """
    return spotify_me(query, _slack_event, 'album')

def artist_me(query, _slack_event):
    """
    :param query: query str
    :param _slack_event: a dict of slack event information(unused for this function)
    :return: a link to spotify artist item found by search
    """
    return spotify_me(query, _slack_event, 'artist')

def playlist_me(query, _slack_event):
    """
    :param query: query str
    :param _slack_event: a dict of slack event information(unused for this function)
    :return: a link to spotify playlist item found by search
    """
    return spotify_me(query, _slack_event, 'playlist')

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

def emojify_me(query, _slack_event):
    """
    query - query str
    slack_event - A dict of slack event information(unused for this function)
    Returns the query text rendered in the form of a drawing made of emojis.
    """
    query = query.strip().upper()  # TODO: remove .upper() when lowercase support is added to emojify_constants
    emoji = ""
    char_patterns = []
    for token in query.split():
        # Use the first emoji found in the message as the template, and don't emojify it.
        if token[0] == ":" and token[-1] == ":" and not emoji:
            emoji = token
        else:
            # if it's past the first word in the command, add a space before the word
            if char_patterns:
                char_patterns.append(emojify_constants.patterns.get(' '))
            for char in token:
                pattern = emojify_constants.patterns.get(char)
                # skip characters that don't have a char pattern in emojify_constants
                if pattern:
                    char_patterns.append(pattern)
    if not emoji:
        return "You'll need to tell me what emoji you want me to use before I can emojify something."
    if not char_patterns:
        return "There's no text in that message that I'm able to emojify."
    return commands_helper.emojify(char_patterns, emoji)

def magic_me(query, _slack_event):
    """
    query - query str
    slack_event - A dict of slack event information(unused for this function)
    Returns information on the requested Magic: the Gathering card using the Scryfall API.
    """
    return magic_parser.parse_magic_card(query)

def no_result_found_response():
    """
    Have bot return a response from a list so they feel less canned
    """
    return random.choice([
        'Ara ara no results found!... am i saying that right? What does `ara ara` even mean?',
        "I didn't find anything for that one",
        "Hmmm, maybe try rephrasing that search",
        "My search-fu failed me."
        "No dice. It's hard looking things up from a battleship in space!",
        "You search for some funny things! But I got nothing for this one.",
        "I don't like giving up but :sigh: I'm giving up. Try a different search",
        "Hmm, Nope. Nothing. Maybe try that again with some different keywords.",
        ('I can helm a battleship, command squadrons of fighters, pilot recon craft '
         "fight an alien army bent on destroying the earth. But I can't find any results for "
         "this search"),
        "I came, I searched... and got nothing.",
        "Y'know I consider myself pretty smart but this search has me stumped.",
        ('Unless this is some sort of zen riddle where the answer lies inside you '
         'I got nothing.'),
        'I searched for what you asked for and got a big angry :no: from the internet.',
        "This search must be hipster because I've never heard of it.",
        ("I've seen the vast expaneses of space, gazed into the abyss of a warp, "
         "and all of that pales in comparison to the emptiness of these search results"),
    ])
