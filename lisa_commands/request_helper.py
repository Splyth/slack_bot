import json
import logging
import os
import urllib

# from googlesearch import search_images Need to figure out how to install this

# Grab the Bot OAuth token from the environment.
BOT_TOKEN = os.environ["BOT_TOKEN"]

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
    logging.warn('arrived here')
    # for j in search_images(query, tld='com', lang='en', safe='on', num=10, start=0, stop=10, pause=2.0, only_standard=True): 
    #     print(j) 
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