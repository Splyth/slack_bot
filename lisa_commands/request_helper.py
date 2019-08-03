import json
import logging
import os
import urllib
import random
# from googlesearch import search_images Need to figure out how to install this

# Grab the Bot OAuth token from the environment.
BOT_TOKEN = os.environ["BOT_TOKEN"]

# GOOGLE API KEY info can be found here: https://developers.google.com/custom-search/
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
GOOGLE_CUSTOM_SEARCH_KEY = os.environ['GOOGLE_CUSTOM_SEARCH_KEY']

# Define the URL of the targeted Slack API resource.
# We'll send our replies there.
SLACK_URL = "https://slack.com/api/chat.postMessage"

def submit_slack_request(data):
    logging.warn
    # Construct the HTTP request that will be sent to the Slack API.
    request = urllib.request.Request(SLACK_URL)
    # Add a header mentioning that the text is URL-encoded.
    request.add_header(
        "Content-Type", 
        "application/json"
    )
    request.add_header(
        "Authorization", 'Bearer {}'.format(BOT_TOKEN),
    )

    # Fire off the request!
    urllib.request.urlopen(request, data).read()

def submit_google_image_search_request(query):
    """
    Submit a search to google for images
    :query what to query for
    """
    params = urllib.parse.urlencode({
        #  'q': query, 
        'q': ';lkj;lkjp[ui0-98poui0-9809u[09u[09u[pouj[09u0poj',
        'key': GOOGLE_API_KEY, 
        'cx': GOOGLE_CUSTOM_SEARCH_KEY,
        'num': 10
    })
    data = json.loads(urllib.request.urlopen("https://www.googleapis.com/customsearch/v1?" + params).read())
    if 'items' in data:
        return random.choice(data["items"])["pagemap"]["cse_image"][0]['src']
    else:
        return "Sorry! I didn't find any results."

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
