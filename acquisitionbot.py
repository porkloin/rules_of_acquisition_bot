import os
import time
import json
import re
import random
from slackclient import SlackClient


#bot's ID from environment var
BOT_ID = os.environ.get("BOT_ID")
jsonfile = 'ferengiRulesOfAcquisition.json'
#constants
AT_BOT = "<@" + str(BOT_ID) + ">"
EXAMPLE_COMMAND = "random"
REGEX = re.compile('\d+')
#start client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def handle_command(command, channel):
    """
        takes a command and figures out if it's gonna work for us or not
        depending on our functions and maybe even asks for more if
        necessary
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + "* command or enter a specific number."
    if command.startswith(EXAMPLE_COMMAND):
        with open (jsonfile) as f:
            data = json.load(f)
            choice = random.choice(data)
            response = "Rule of Acquisition number " + str(choice['Number']) + ": " + choice['Rule']
            f.close()
    if REGEX.match(command):
        with open (jsonfile) as f:
            data = json.load(f)
            choice = None;
            for i in data:
                if i.get('Number') == int(command):
                    choice = i
            if choice:
                response = "Rule of Acquisition number " + str(choice['Number']) + ": " + choice['Rule']
            else:
                response = "There is no rule number " + str(command) + ", try again with a number between 1 and " + str(len(data))
            f.close()
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    """
        Find out if someone is talking at us
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                #return text if @ mentioned
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                                               output['channel']
    return None, None

if __name__ == "__main__":
    #wait a sec
    READ_WEBSOCKET_DELAY = 1 
    if slack_client.rtm_connect():
        print("Connected, ready")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Check your junk, token and ID, etc.")

