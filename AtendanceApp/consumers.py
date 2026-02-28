from channels.generic.websocket import AsyncJsonWebsocketConsumer

class AttendanceConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Only allow staff users to connect
        if not (self.scope["user"].is_staff or self.scope["user"].is_superuser or self.scope["user"].is_admin):
            await self.close()
            return

        # Add the channel to the group
        await self.channel_layer.group_add(
            "attendance_live",
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the channel from the group when disconnected
        await self.channel_layer.group_discard(
            "attendance_live",
            self.channel_name
        )

    async def attendance_event(self, event):
        # Send the event data to the WebSocket client
        await self.send_json(event["data"])
