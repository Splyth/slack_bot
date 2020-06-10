# slack_bot
A repo containing the code for a slack bot using an AWS lambda instance.

# Requirements
  [AWS Account](https://aws.amazon.com/console/)
  
  Python 3.6 Runtime (Select once you have your lamabda function environment and API Gateway created)
  
  [DynamoDB](https://aws.amazon.com/dynamodb/) Tables: [bot_id: [id = 1, BOT_ID], karma_scores: [user, karma]]
  
  [Google Account](https://console.developers.google.com)
  Google Custom Search API Enabled: Once your Google API Account is made enable "Custom Search API" for your project
  
  [Azure Account](https://azure.microsoft.com/en-us/account/)
  Azure Custom Search API Enabled: Once your Microsoft Azure account is made enable "Custom Search API" for your project
  
  [Giphy Access](https://developers.giphy.com/)

  [Spotify Access](https://developer.spotify.com/documentation/web-api/quick-start/)

  [Slack App API Access](https://api.slack.com/)
  
# Invoke
  Once running the bot knows the following commands
  
  @BOT_NAME help - sends user a private message with all known commands

  @BOT_NAME reverse me - reverse text entered after command
  
  @BOT_NAME image me - use text after command to query Google for an image
  
  @BOT_NAME youtube me - use text after command to query youtube for a video
  
  @BOT_NAME anime me - use text after command to query anime news network for anime info
  
  @BOT_NAME manga me - use text after command to query anime news network for manga info

  @BOT_NAME wiki me - use text after command to query wikipedia for an article

  @BOT_NAME gif me - use text after command to query giphey for gif

  @BOT_NAME spotify me [track|album|artist|playlist] - use text after command, including one of the media types in brackets, to query spotify for a song, album, artist, or playlist

  @BOT_NAME sticker me - use text after command to query giphey for sticker

  @BOT_NAME table flip - responds with a tableflip emoji

  @BOT_NAME put it back - responds with a reversetableflip emoji

  @BOT_NAME flip coin - responds with either head or tails

  @BOT_NAME decide - responds randomly with one of the words after this command

  @BOT_NAME call the cops - responds with an image of anime cops with the caption "You Called"

  @BOT_NAME kill me - reacts to user message, kicks user from channel, and sends user a DM with a quote about death

  @BOT_USER shame <User ID> - You must @USER_NAME (might figure out how to display with a user name search)

  @BOT_USER praise <User ID> - You must @USER_NAME (might figure out how to display with a user name search)

# Other Bot Interactions:
  ## Delete Bot Message:
    If a bot has posted something you didn't want it to. You can respond with an emoji to have the
    bot delete that message. Currently the emoji is :delet: Yes it's misspelled. If you ever make your
    own feel free to change it in the code or make it configurable
  
# Environment Variables

  BING_SUBSCRIPTION_KEY: The Subscription Key from the Azure Account to use

  BING_CUSTOM_SEARCH_KEY: The Custom Search Key to use (Create in Azure under Bing Custom image search)

  BOT_TOKEN is the slack apps token more info is [here:](https://api.slack.com/bot-users)

  GOOGLE_CUSTOM_SEARCH_KEY: Once you've enabled you Custom Search API check there it's the: Search Engine ID

  GIPHY_API_KEY: A Giphey API KEY [here](https://developers.giphy.com/docs/api#quick-start-guide)

  GOOGLE API KEY: You can generate one in the Google API Under Credentials

  GOOGLE_CUSTOM_SEARCH_KEY: Genereate a custom search engine in API key should be generated with search engine

  SLACK_SECRET: Under General Information in slack API. Used to ensure bot only responds to requests from slack

  SLACK_USER_TOKEN: User token of the person who made the bot (must have kick user priveldges for certain commands)

  SPOTIFY_CLIENT_ID: Client ID for Spotify (check the spotify docs in the requirements section)

  SPOTIFY_CLIENT_SECRET: Client Secret for Spotify (check the spotify docs in the requirements section)

# Notes on Google API
  https://cse.google.com/cse/all (In the web form where you create/edit your custom search engine enable "Image search" option and and for "Sites to search" option select "Search the entire web but emphasize included sites")

  After setting up you Google developers account and project you should have your developers API key and project CX (aka search engine id)

# Notes on Setting Up A Slack Bot on AWS
  ## A Good Starting Tutorial:
    https://chatbotslife.com/write-a-serverless-slack-chat-bot-using-aws-e2d2432c380e
    he also provides a direct link to a more full version than in his tutorial:
    https://gist.github.com/zedr/226fab1c28f3bec8d656f6b54cea742f

  ## Some Gotchas from his tutorial:
    don't listen to him about the API stuff that might have been true at one point but now
    you must set the `Use Lambda Proxy integration` But really what you SHOULD do is go to the
    lambda service and when you start creating a new lambda function it will ask if you want to
    create an new API Gateway. Say yes and it will handle all that BS for you. (You will still have to
    grab the INVOKE URL (remember to actually drill down to the method (e.g. ANY, POST, etc) to get the full
    path)

  ## Testing this function.
    AWS has a way to test this via the Test button next to save. You can click on the drop down next
    to it and use the following JSONS
  ## Reverse me test
  ```
  {
    {
      "body": "{\"token\":\"TEST_TOKEN\",\"team_id\":\"TEAM_ID\",\"api_app_id\":\"APP_ID\",\"event\":{\"client_msg_id\":\"MSG_ID\",\"type\":\"app_mention\",\"text\":\"<@APP_ID> reverse me I am a palindrome tacocat\",\"user\":\"USER_WHO_SENT_MESSAGE\",\"team\":\"TEAM_ID\",\"channel\":\"CHANNEL_ID\"},\"type\":\"event_callback\",\"event_id\":\"EVENT_ID\"}"
    }
  }
  ```
  ## Image me test
  ```
  {
    {
      "body": "{\"token\":\"TEST_TOKEN\",\"team_id\":\"TEAM_ID\",\"api_app_id\":\"APP_ID\",\"event\":{\"client_msg_id\":\"MSG_ID\",\"type\":\"app_mention\",\"text\":\"<@APP_ID> image me Tacos\",\"user\":\"USER_WHO_SENT_MESSAGE\",\"team\":\"TEAM_ID\",\"channel\":\"CHANNEL_ID\"},\"type\":\"event_callback\",\"event_id\":\"EVENT_ID\"}"
    }
  }
  ```

# Misc Notes
  ## Easiest way to find a channel: 
  Open up your slack workspace in your favorite browser. Now navigate to the
  channel you want to post in. Check your URL. Notice that last string of letters and numbers in the URL changes as you click
  around. Those numbers the channel ID

  Remember for your bot to post you must give it events to listen to that's handled in the Slack.api website.

  AWS does provide the ability to check the status of calls against your function via the CloudLogs. I won't go into detail here but the AWS docs are pretty good.

  ## Testing your function is being called correctly from the Gateway API
  Drill down to the `ANY` method in your API (it can be POST GET etc. But if you did what I said above it will be any) Now click
  on it. You see that cool diagram that just showed up? See the `Test` button click it. Select `Post` from the drop down box and copy that JSON I gave up above and click `Test` It will output the log of the Cloud API Gateway trying to hit your currently saved lambda function (NOTE Not the the DEPLOYED one the one you have saved) Saved is either the same or newer that deployed

  ## Deploying your function:
  Until it's deployed no one is gonna be able to use it. Slack can't call it. So just click on the `Actions` button and `Deploy API`
  and that should deploy your app and now people can hit it.
