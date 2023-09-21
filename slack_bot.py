import slack
import os,sys
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
sys.path.append(os.getcwd())
load_dotenv()
SLACK_TOKEN: str = os.getenv("SLACK_TOKEN")
SIGNING_SECRET: str = os.getenv("SIGNING_SECRET")


app=Flask(__name__)
slack_event_adapter=SlackEventAdapter(SIGNING_SECRET,'/slack/events',app)


client=slack.WebClient(token=SLACK_TOKEN)
BOT_ID=client.api_call('auth.test')["user_id"]

client.chat_postMessage(channel="#test-bot",text="hello welcome to sqlify")
message_counts={}

@slack_event_adapter.on('message')
def message(payload):
    event=payload.get('event',{})
    channel_id=event.get('channel')
    user_id=event.get('user')
    text=event.get('text')
    if BOT_ID!=user_id:
        if user_id in message_counts:
            message_counts[user_id]+=1
        else:
            message_counts[user_id]=1
        client.chat_postMessage(channel=channel_id,text=text)

@app.route('/message-count',methods=['POST'])
def message_count():
    data=request.form
    user_id=data.get('user_id')
    message_count=message_counts.get(user_id,0)
    channel_id=data.get('channel_id')
    client.chat_postMessage(channel=channel_id,text=f"Message:{message_count}")
    return Response() , 200


if __name__ == "__main__":
    app.run(debug=True)