import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CallConsumer(AsyncWebsocketConsumer):


    async def connect(self):
        
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {"type": "connection", "data": {"message": "Connected"}}
            )
        )

    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.my_name, self.channel_name)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        eventType = text_data_json["type"]

        if eventType == "login":
            name = text_data_json["data"]["name"]
            self.my_name = name
            await self.channel_layer.group_add(self.my_name, self.channel_name)


        if eventType == "call":
            name = text_data_json["data"]["name"]
            print(self.my_name, "is calling", "name")
            await self.channel_layer.group_send(
                name,
                {
                    "type":"call_received",
                    "data": {
                        "caller": self.my_name,
                        "rtcMessage": text_data_json["data"]["rtcMessage"],
                    },
                },
            )

        if eventType == "ICEcandidate":
            user = text_data_json["data"]["user"]
            await self.channel_layer.group_send(
                user,
                {
                    "type":"ICEcandidate",
                    "data":{"rtcMessage": text_data_json["data"]["rtcMessage"]},
                },
            )


    async def call_received(self, event):
        print("Call Received by", self.my_name)
        await self.send(
            text_data=json.dumps({"type":"call_received", "data":event["data"]})
        )



    async def call_answered(self, event):

        print(self.my_name, "'s call answered")
        await self.send(
            text_data=json.dumps({"type":"call_answered", "data":event["data"]})
        )


    async def ICEcandidate(self, event):
        await self.send(
            text_data=json.dumps({"type": "ICEcandidate", "data": event["data"]})
        )



