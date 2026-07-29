import json
from channels.generic.websocket import AsyncWebsocketConsumer

class MapupdatesConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    self.group_name="map_updates"

    await self.channel_layer.group_add(
      self.group_name,
      self.channel_name
    )
    await self.accept()
  async def disconnect(self, class_code):
    await self.channel_layer.group_discard(
      self.group_name,
      self.channel_name
    )
  async def incident_update(self,event):
    await self.send(text_data=json.dumps(event["data"]))