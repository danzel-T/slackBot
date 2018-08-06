import time
import os
import re
import keys
from slackclient import SlackClient


slackClient = SlackClient(keys.slackBotKey)
slackbotId = None

rtmReadDelay = 1
requestCommand = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parseSlackingBotCommands(slackEvents):
    for event in slackEvents:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == slackbotId:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message):

    matches = re.search(MENTION_REGEX, message)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    notFoundResponse = "Command Not Found. Try *{}*.".format(requestCommand)

    response = None
    if command.startswith(requestCommand):
        response = "Test"

    slackClient.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or notFoundResponse
    )

if __name__ == "__main__":
    if slackClient.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        slackbotId = slackClient.api_call("auth.test")["user_id"]
        while True:
            command, channel = parseSlackingBotCommands(slackClient.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(rtmReadDelay)
    else:
        print("Connection failed")