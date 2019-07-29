# slack_bot
A repo where I stash info about how to make a slack bot using aws

The lambda_function.py uses the Python 3.6 Runtime

BOT_USER is the slack apps token: 

The majority of this code was copied from from: 
https://chatbotslife.com/write-a-serverless-slack-chat-bot-using-aws-e2d2432c380e
he also provides a direct link to a more full version than in his tutorial:
https://gist.github.com/zedr/226fab1c28f3bec8d656f6b54cea742f

Some Gotchas from his tutorial:
don't listen to him about the API stuff that might have been true at one point but now
you must set the `Use Lambda Proxy integration` But really what you SHOULD do is go to the
lambda service and when you start creating a new lambda function it will ask if you want to
create an new API Gateway. Say yes and it will handle all that BS for you. (You will still have to
grab the INVOKE URL (remember to actually drill down to the method (e.g. ANY, POST, etc) to get the full
path)

Testing this function.
AWS has a way to test this via the Test button next to save. You can click on the drop down next
to it and use the following JSON
```
{
  "body": {
    "type": "direct_mention",
    "channel": "THE CHANNEL YOU WANT TO POST TO",
    "text": "testing talking from a serverless lambda function"
  }
}
```
Easiest way to find a channel: 
Open up your slack workspace in your favorite browser. Now navigate to the
channel you want to post in. Check your URL. Notice that last string of letters and numbers in the URL changes as you click
around. Those numbers the channel ID

Remember for your bot to post you must give it events to listen to that's handled in the Slack.api website.

AWS does provide the ability to check the status of calls against your function via the CloudLogs. I won't go into detail here but the AWS docs are pretty good.

Testing your function is being called correctly from the Gateway API
Drill down to the `ANY` method in your API (it can be POST GET etc. But if you did what I said above it will be any) Now click
on it. You see that cool diagram that just showed up? See the `Test` button click it. Select `Post` from the drop down box and copy that JSON I gave up above and click `Test` It will output the log of the Cloud API Gateway trying to hit your currently saved lambda function (NOTE Not the the DEPLOYED one the one you have saved) Saved is either the same or newer that deployed

Deploying your function:
So until it's deployed no one is gonna be able to use it. Slack can't call it. So just click on the `Actions` button and `Deploy API`
and that should deploy your app and now people can hit it.
