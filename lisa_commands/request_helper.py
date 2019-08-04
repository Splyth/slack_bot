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

# The Microsoft Azure subscription key
BING_SUBSCRIPTION_KEY = os.environ['BING_SUBSCRIPTION_KEY']
# The Custom Search API (uses bing) in Mircorsoft Azure to use
BING_CUSTOM_SEARCH_KEY = os.environ['BING_CUSTOM_SEARCH_KEY']

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

def google_image_search(query):
    """
    Submit a search to google for images
    :query what to query for
    """
    params = urllib.parse.urlencode({
        'q': query, 
        'key': GOOGLE_API_KEY, 
        'cx': GOOGLE_CUSTOM_SEARCH_KEY,
        'num': 10
    })
    data = json.loads(urllib.request.urlopen("https://www.googleapis.com/customsearch/v1?" + params).read())
    if 'items' in data:
        return random.choice(data["items"])["pagemap"]["cse_image"][0]['src']
    else:
        return "Sorry! I didn't find any results."

def bing_image_search(query):
    params = urllib.parse.urlencode({
        'q': query, 
        'count': 10,
        'mkt': 'en-US',
        'customconfig': BING_CUSTOM_SEARCH_KEY
    })
    
    request = urllib.request.Request('https://api.cognitive.microsoft.com/bingcustomsearch/v7.0/images/search?' + params)
    request.add_header("Ocp-Apim-Subscription-Key", BING_SUBSCRIPTION_KEY)

    data = json.loads(urllib.request.urlopen(request).read())

    logging.warn(data)
    if 'value' in data and data['value']:
        return random.choice(data["value"])["contentUrl"]
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
