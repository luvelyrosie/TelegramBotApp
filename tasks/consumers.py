from channels.generic.websocket import AsyncJsonWebsocketConsumer


class TaskConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        
        user = self.scope.get("user")
        print("WebSocket connect called:", self.scope["user"])
        print(f"Connected user: {user} (id={getattr(user, 'id', None)})")

        await self.accept()
        print("Accepted connection (debug mode)")

        if not user or user.is_anonymous:
            self.group_name = "public_tasks"
            print("Anonymous user connected — joined 'public_tasks' group")
        else:
            self.group_name = f"user_{user.id}"
            print(f"Authenticated user connected — joined {self.group_name}")

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        print(f"Added channel to group {self.group_name}")

    async def disconnect(self, close_code):
        group = getattr(self, "group_name", None)
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)
            print(f"Disconnected from {group}, code={close_code}")
        else:
            print(f"Disconnected (no group), code={close_code}")

    async def task_update(self, event):
        payload = event.get("payload")
        if payload:
            await self.send_json(payload)
            print("Sent task update:", payload)