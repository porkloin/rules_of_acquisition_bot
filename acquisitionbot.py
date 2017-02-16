import os
import time
import json
import re
import random
from slackclient import SlackClient


# bot's ID from environment var
BOT_ID = os.environ.get("BOT_ID")
jsonfile = 'ferengiRulesOfAcquisition.json'
# constants
AT_BOT = "<@" + str(BOT_ID) + ">"
EXAMPLE_COMMAND = "random"
REGEX = re.compile('\d+')
# start client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# Make a list of valid commands
validCommands = ["random", "list all"]

# Load the JSON into memory
with open(jsonfile) as f:
    rules = json.load(f)

# Sort all rules into Number: complete dict
sortedRules = {}
for i in rules:
    sortedRules[i['Number']] = i


def handle_command(command, channel):
    """
        takes a command and figures out if it's gonna work for us or not
        depending on our functions and maybe even asks for more if
        necessary
    """
    # check if command is a digit
    try:
        command = int(command)
    except ValueError:
        # command is a string
        pass

    # If we have a number, try this
    if str(command).isdigit():
        if command in sortedRules.keys():
            response = "Rule of Acquisition number " + str(sortedRules[command]['Number']) + ": " + sortedRules[command]['Rule']

        else:
            # response = "There is no rule number " + str(command) + ", try again with a number between 1 and " + str(sortedRules[-1['Number']])
            response = "There is no rule number " + str(command) + ", try again with a number between 1 and " + str(max(sortedRules.keys()))
            print response

    # If we don't have a number, check the list of valid commands
    else:
        if str(command).lower() == "random":
            choice = random.choice(rules)
            response = "Rule of Acquisition number " + str(choice['Number']) + ": " + choice['Rule']

        elif str(command).lower() == "list all":
            choice = random.choice(rules)
            response = "The available list of rules is as follows: {}".format(sortedRules.keys())

        if command not in validCommands:
            response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + "* command or enter a specific number."

    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        Find out if someone is talking at us
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text if @ mentioned
                return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
    return None, None

if __name__ == "__main__":
    # wait a sec
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
