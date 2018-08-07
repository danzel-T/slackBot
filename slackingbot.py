import time
import re
import keys
import tweepy
import json
import schedule
from operator import itemgetter
from slackclient import SlackClient


slackClient = SlackClient(keys.slackBotKey)
slackbotId = None

rtmReadDelay = 1
requestCommand = "tweet"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parseSlackingBotCommands(slackEvents):
    for event in slackEvents:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parseDM(event["text"])
            if user_id == slackbotId:
                return message, event["channel"]
    return None, None

def parseDM(message):
    matches = re.search(MENTION_REGEX, message)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    notFoundResponse = "Command Not Found. Try tweet"
    response = None
    if command.startswith(requestCommand):
        response = showTweets()

    slackClient.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or notFoundResponse
    )

def showTweets():
    topTen = []
    auth = tweepy.OAuthHandler(keys.consumerKey,keys.consumerSecret)
    auth.set_access_token(keys.accessToken,keys.accessTokenSecret)
    api = tweepy.API(auth)

    trending = json.loads(json.dumps(api.trends_place(1),indent=2))
    counter = 0
    newTrending = trending[0]['trends']
    sorted_trending = sorted(newTrending, key=itemgetter("tweet_volume"), reverse=True)

    for trend in sorted_trending:
        if counter < 10:
            topTen.append(str(counter+1) +". " +trend['name'])
            counter+=1

    response = '\n'.join(topTen)
    if channel == None:
        slackClient.api_call(
            "chat.postMessage",
            channel='assignment1',
            text=response
       )
    else:
        return "\n".join(topTen)





if __name__ == "__main__":
    if slackClient.rtm_connect(with_team_state=False):
        print("Slack Bot connected and running!")
        slackbotId = slackClient.api_call("auth.test")["user_id"]
        schedule.every().day.at('00:00').do(showTweets)
        while True:
            schedule.run_pending()
            time.sleep(1)
            command, channel = parseSlackingBotCommands(slackClient.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(rtmReadDelay)
    else:
        print("Connection failed")