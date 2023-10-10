from decouple import config
import asyncio
import json
import redis.asyncio as redis

COUPON_CODES = {
    'entery_10': 0.1,
    'nice_15': 0.15,
    'super_20': 0.2,
    'vip_delight': 0.4
}

redis_url = config('REDIS')

class SessionManager:
    def __init__(self, redis_url):
        pool = redis.ConnectionPool.from_url(redis_url+'?decode_responses=True')
        self.redis = redis.Redis.from_pool(pool)

    async def session_exists(self, session_id: str = ''):
        return await self.redis.exists(session_id)

    async def get_session_data(self, session_id):
        session_data = await self.redis.get(session_id, encoding='utf-8')

        # Deserialize the session data if it exists
        if session_data:
            session_data = json.loads(session_data)
        
        return session_data

    async def set_session_data(self, session_id, session_data):
        # Serialize the session data if exists
        if session_data:
            session_data = json.dumps(session_data)
            await self.redis.set(session_id, session_data)

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
        await self.redis.aclose()

# Instantiate a SessionManager object
session_manager = SessionManager(redis_url)

__all__ = ['session_manager']