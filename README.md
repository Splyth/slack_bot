# slack_bot
A repo where I stash info about how to make a slack bot using aws

## Requirements
  (AWS Account)[https://aws.amazon.com/console/]
  
  Python 3.6 Runtime (Select once you have your lamabda function environment and API Gateway created)
  
  (Google API Account)[https://console.developers.google.com]
  
  Google Custom Search API Enabled: Once your Google API Account is made enable "Custom Search API" for your project
  
  SLACK App API Access
  
## Invoke
  Once running the bot knows the following commands
  
  @BOT_NAME reverse me - reverse text enetered after command
  
  @BOT_NAME image me - use text after command to query Google for an image
  
## Environment Variables
  BOT_TOKEN is the slack apps token (more info is (here:)[https://api.slack.com/bot-users]
  
  GOOGLE API KEY: You can generate one in the Google API Under Credentials
  
  GOOGLE_CUSTOM_SEARCH_KEY: Once you've enabled you Custom Search API check there it's the: Search Engine ID

  BING_SUBSCRIPTION_KEY: The Subscription Key from the Azure Account to use

  BING_CUSTOM_SEARCH_KEY: The Custom Search Key to use (Create in Azure under Bing Custom image search)

## Notes on Google API
  https://cse.google.com/cse/all (In the web form where you create/edit your custom search engine enable "Image search" option and and for "Sites to search" option select "Search the entire web but emphasize included sites")

  After setting up you Google developers account and project you should have your developers API key and project CX (aka search engine id)

## Notes on Setting Up A Slack Bot on AWS
  ### A Good Starting Tutorial:
    https://chatbotslife.com/write-a-serverless-slack-chat-bot-using-aws-e2d2432c380e
    he also provides a direct link to a more full version than in his tutorial:
    https://gist.github.com/zedr/226fab1c28f3bec8d656f6b54cea742f

  ### Some Gotchas from his tutorial:
    don't listen to him about the API stuff that might have been true at one point but now
    you must set the `Use Lambda Proxy integration` But really what you SHOULD do is go to the
    lambda service and when you start creating a new lambda function it will ask if you want to
    create an new API Gateway. Say yes and it will handle all that BS for you. (You will still have to
    grab the INVOKE URL (remember to actually drill down to the method (e.g. ANY, POST, etc) to get the full
    path)

  ### Testing this function.
    AWS has a way to test this via the Test button next to save. You can click on the drop down next
    to it and use the following JSONS
  #### Reverse me test
  ```
  {
    {
      "body": "{\"token\":\"TEST_TOKEN\",\"team_id\":\"TEAM_ID\",\"api_app_id\":\"APP_ID\",\"event\":{\"client_msg_id\":\"MSG_ID\",\"type\":\"app_mention\",\"text\":\"<@APP_ID> reverse me I am a palindrome tacocat\",\"user\":\"USER_WHO_SENT_MESSAGE\",\"team\":\"TEAM_ID\",\"channel\":\"CHANNEL_ID\"},\"type\":\"event_callback\",\"event_id\":\"EVENT_ID\"}"
    }
  }
  ```
  ### Image me test
  ```
  {
    {
      "body": "{\"token\":\"TEST_TOKEN\",\"team_id\":\"TEAM_ID\",\"api_app_id\":\"APP_ID\",\"event\":{\"client_msg_id\":\"MSG_ID\",\"type\":\"app_mention\",\"text\":\"<@APP_ID> image me Tacos\",\"user\":\"USER_WHO_SENT_MESSAGE\",\"team\":\"TEAM_ID\",\"channel\":\"CHANNEL_ID\"},\"type\":\"event_callback\",\"event_id\":\"EVENT_ID\"}"
    }
  }
  ```

## Misc Notes
  ### Easiest way to find a channel: 
  Open up your slack workspace in your favorite browser. Now navigate to the
  channel you want to post in. Check your URL. Notice that last string of letters and numbers in the URL changes as you click
  around. Those numbers the channel ID

  Remember for your bot to post you must give it events to listen to that's handled in the Slack.api website.

  AWS does provide the ability to check the status of calls against your function via the CloudLogs. I won't go into detail here but the AWS docs are pretty good.

  ### Testing your function is being called correctly from the Gateway API
  Drill down to the `ANY` method in your API (it can be POST GET etc. But if you did what I said above it will be any) Now click
  on it. You see that cool diagram that just showed up? See the `Test` button click it. Select `Post` from the drop down box and copy that JSON I gave up above and click `Test` It will output the log of the Cloud API Gateway trying to hit your currently saved lambda function (NOTE Not the the DEPLOYED one the one you have saved) Saved is either the same or newer that deployed

  ### Deploying your function:
  So until it's deployed no one is gonna be able to use it. Slack can't call it. So just click on the `Actions` button and `Deploy API`
  and that should deploy your app and now people can hit it.
