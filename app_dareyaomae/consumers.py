import json
from channels.generic.websocket import AsyncWebsocketConsumer

#asyncをつけることでパフォーマンスが上がる
#websocketConsumerからAsyncWebsocketConsumerになる

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']#scopeは接続の情報を持つ、
        self.room_group_name = 'host_room_%s' % self.room_name#roomのstrを作ってる

        # Join room group
        await self.channel_layer.group_add(
        #グループ参加処理、まぁこういう書き方するんだよ、ぐらい
        #ChatComsumerは同期だがchannel_layerは非同期
            self.room_group_name,
            self.channel_name
        )

        await self.accept()#websocketをacceptする,acceptしない場合rejectされる

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(#退出処理
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(#グループにメッセージを送る
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))