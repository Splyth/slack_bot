"""
A wrapper around external requests to APIs
"""
import json
import os
import urllib
import random
import re
import base64
import logging
import boto3
# from googlesearch import search_images Need to figure out how to install this

# Bot OAuth token from the environment.
BOT_TOKEN = os.environ["BOT_TOKEN"] # stats with xoxb
# User who made the bot Oauth Token (found in API above bot token starts with xoxp)
SLACK_USER_TOKEN = os.environ["SLACK_USER_TOKEN"]

# GOOGLE API KEY info can be found here: https://developers.google.com/custom-search/
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
GOOGLE_CUSTOM_SEARCH_KEY = os.environ['GOOGLE_CUSTOM_SEARCH_KEY']

# Spotify API Client ID and Secret
SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']

# Giphy API Key
GIPHY_API_KEY = os.environ['GIPHY_API_KEY']

# Define the URL of the targeted Slack API resource.
# We'll send our replies there.
SLACK_URL = "https://slack.com/api/"

def submit_slack_request(data, chat_action, auth_type='BOT'):
    """
    Submit request obj to slack
    data - a dict to be placed in the JSON body
    chat_action - the slack action to perform
    auth_type - ['BOT'| 'USER'] Which token to use (default is bot)
    """
    # Construct the HTTP request that will be sent to the Slack API.
    request = urllib.request.Request(SLACK_URL + chat_action)
    # Add a header mentioning that the text is JSON.
    request.add_header(
        "Content-Type",
        "application/json"
    )

    token = BOT_TOKEN
    if auth_type == 'USER':
        token = SLACK_USER_TOKEN

    request.add_header(
        "Authorization", f'Bearer {token}',
    )

    # Fire off the request!
    return urllib.request.urlopen(request, json.dumps(data).encode('utf-8')).read()

def direct_message_channel_search(slack_event):
    """
    slack_event - a dict containing the slack event

    Returns the channel_id for the dm between the bot and the user who sent the message
    """
    return json.loads(
        submit_slack_request({'user': slack_event['user']}, 'im.open')
    )['channel']['id']

def anime_news_network_search(media_type, query):
    """
    search anilist for series info
    :type [anime|manga] string
    :query what to search for
    """
    params = urllib.parse.urlencode({
        'id':155,
        'search': query.strip(),
        'type': media_type
    })

    data = urllib.request.urlopen(
        r'https://www.animenewsnetwork.com/encyclopedia/reports.xml?' + params
    ).read().decode('utf-8')

    show_ids = re.search(r"<id>(\d+)</id>", data)
    if show_ids is not None:
        show_id = ''.join(i for i in show_ids.groups(1) if i.isdigit())
        return f"https://www.animenewsnetwork.com/encyclopedia/{media_type}.php?id={show_id}"

    return None

def gif_search(query):
    """
    submit a search to giphy
    :query what to query for
    """
    link = google_image_search(query,{'imgType':'animated'})

    if link != None:
        return link
    return None

def google_image_search(query, param_overrides={}):
    """
    Submit a search to google for images
    :query what to query for
    :param_overrides a dict of search parameter overrides
    """

    params = {
        'q': query,
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CUSTOM_SEARCH_KEY,
        'num': 5,
        'searchType': 'image'
    }

    params.update(param_overrides)

    data = json.loads(
        urllib.request.urlopen("https://www.googleapis.com/customsearch/v1?" + urllib.parse.urlencode(params)).read()
    )
    if 'items' in data:
        return random.choice(data['items'])['link']

    return None

def youtube_search(query):
    """
    Submit a search to youtube
    :query what to query for
    """
    params = urllib.parse.urlencode({
        'part': 'snippet',
        'q': query,
        'key': GOOGLE_API_KEY,
        'maxResults': 1,
        'type': 'video'
    })
    request = urllib.request.Request("https://www.googleapis.com/youtube/v3/search?" + params)
    request.add_header("Content-Type", "application/json")
    data = json.loads(urllib.request.urlopen(request).read())

    if data.get('items'):
        video_id = data["items"][0]["id"]["videoId"]
        return f"https://www.youtube.com/watch?v={video_id}"

    return None

def wikipedia_search(query):
    """
    Submit a search to wikipedia
    :query what to query for
    """

    request_params = urllib.parse.urlencode({
        'action':'query',
        'list':'search',
        'srsearch': query,
        'format':'json'
    })

    request = urllib.request.Request('https://en.wikipedia.org/w/api.php?' + request_params)

    data = json.loads(urllib.request.urlopen(request).read())

    if data['query']:
        if data['query']['search']:
            wikipedia_title = data['query']['search'][0]['title']
            link_title = '_'.join(wikipedia_title.split())
            return f"https://en.wikipedia.org/wiki/{link_title}"

    return None

def spotify_search(query_type, search_query):
    """
    submit a search query to spotify
    :param query_type: the type of query, of track, album, artist, or playlist.
    :param search_query:
    """
    search_params = urllib.parse.urlencode({
        'q': search_query,
        'type': query_type,
        'limit': 1
    })

    search_request = urllib.request.Request(
        'https://api.spotify.com/v1/search' + '?' + search_params
    )
    search_request.add_header(
        'Authorization',
        f'Bearer {spotify_token()}'
    )

    # Submit search request
    search_response = json.load(urllib.request.urlopen(search_request))

    # First property of the JSON response is the query type pluralized, which is why I did this
    # monstrosizty of a format string to not have an if statement for each type
    if search_response[f'{query_type}s']['items']:
        return search_response[f'{query_type}s']['items'][0]['external_urls']['spotify']

    return None

def return_status():
    """
    We always want to return status OK to the gateway API
    This has no bearing on the slack request. It's just
    stating that function completed OK
    """
    return {
        'statusCode': 200,
        'body':'no worries',
    }

def dynamodb_update(table, keys, update_expression, expression_values):
    """
    Updates a Dynamodb Item

    table - The table name (string)
    keys - The keys of the item we are to update (dict)
    update_expression - The sql statement we want to preform (string)
    expression_values - The subbed in values to the update expression (dict)

    Example:
        dynamodb_update(
            'my_table',
            {'user': {'S': 'Rick Hunter'}},
            'SET karma = karma + :val',
            {':val': {'N': '1'} }
        )

    Returns Nothing
    """
    dynamodb = boto3.client('dynamodb')
    dynamodb.update_item(
        TableName=table,
        Key=keys,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values)

def dynamodb_query(table, keys):
    """
    Queries a Dynamodb Item

    table - The table name (string)
    keys - The keys of the item we are to update (dict)

    Example:
        dynamodb_update(
            'my_table',
            {'user': {'S': 'Rick Hunter'}}
        )
        #=> {'Item': {...}}

    Returns a dict
    """

    dynamodb = boto3.client('dynamodb')
    return dynamodb.get_item(TableName=table, Key=keys)

## HELPER FUNCTIONS
def spotify_token():
    """
    Handles getting the access token to authenticate to spotify
    """

    # First we need to get an access token to do the search request
    token_request = urllib.request.Request('https://accounts.spotify.com/api/token')

    token_request.add_header(
        'Content-Type',
        'application/x-www-form-urlencoded'
    )

    # Spotify expects an authorization header in the format Base64(client_id:client_secret)
    authorization = base64.b64encode(
        bytes(SPOTIFY_CLIENT_ID+':'+SPOTIFY_CLIENT_SECRET, encoding='utf8')
    ).decode('utf-8')

    token_request.add_header(
        'Authorization',
        f'Basic {authorization}'
    )
    token_params = urllib.parse.urlencode({
        'grant_type': 'client_credentials'
    }).encode('utf-8')

    # TODO: Should cache this token (use Redis or equivalent AWS product)
    return json.load(
        urllib.request.urlopen(token_request, data=token_params)
    )['access_token']
