from decouple import config
import json
import redis.asyncio as redis

redis_url = config('REDIS')

class SessionManager:
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)

    async def get_session_data(self, session_id):
        session_data = await self.redis.hgetall(session_id, encoding='utf-8')

        # Deserialize the 'items' field if it exists
        if 'items' in session_data:
            session_data['items'] = json.loads(session_data['items'])

        return session_data

    async def set_session_data(self, session_id, data):
        # Serialize the 'items' field if it exists
        if 'items' in data:
            data['items'] = json.dumps(data['items'])

        await self.redis.hmset_dict(session_id, data)

    async def update_item_list(self, session_id, item_list):
        # Serialize the item list before updating
        await self.redis.hmset_dict(session_id, {'items': json.dumps(item_list)})

    async def add_item_to_list(self, session_id, item):
        session_data = await self.get_session_data(session_id)
        items = session_data.get('items', [])
        items.append(item)

        await self.update_item_list(session_id, items)

    async def remove_item_from_list(self, session_id, item):
        session_data = await self.get_session_data(session_id)
        items = session_data.get('items', [])

        if item in items:
            items.remove(item)

        await self.update_item_list(session_id, items)

    async def cleanup(self):
        await self.redis.close()

# Instantiate a SessionManager object
session_manager = SessionManager(redis_url)

# Export the SessionManager object
__all__ = ['session_manager']