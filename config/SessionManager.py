from decouple import config
import json
import redis.asyncio as redis
from redis.commands.json.path import Path

COUPON_CODES = {
    'entery_10': 0.1,
    'nice_15': 0.15,
    'super_20': 0.2,
    'vip_delight': 0.4,
    'cart': {
        'asdasdsad': {'quantity': 0, 'price': 0.0},
        'qweqwe': {'quantity': 0, 'price': 0.0},
        'zxczxczxc': {'quantity': 0, 'price': 0.0},
        'ghjghjhj': {'quantity': 0, 'price': 0.0}
    }
}

redis_url = config('REDIS')

class SessionManager:
    def __init__(self, redis_url):
        pool = redis.ConnectionPool.from_url(redis_url+'?decode_responses=True')
        self.redis = redis.Redis.from_pool(pool)

    async def session_exists(self, session_id: str = ''):
        return await self.redis.exists(session_id)

    async def get_session_data(self, key, query: str = ''):
        res = {'success': False, 'message':'unknown error'}

        try:
            session_data = await self.redis.json().get(key, f".{query}")

            if session_data:
                res = {'success': True, 
                       'message':'data retrieved from cache', 
                       'data': session_data
                    }
            else:
                res['message'] = f'key {key} not found'
        except Exception as e:
            res['message'] = str(e)
        finally:
            return res

    async def set_session_data(self, key, session_data):
        res = {'success': False, 'message':'unknown error'}

        try:
            if key and session_data:
                res = await self.redis.json().set(key, Path.root_path(), session_data)
                if res:
                    res = {'success': True, 'message':'data added to cache'}
            else:
                res['message'] = 'missing parameters'
        except Exception as e:
            res['message'] = str(e)
        finally:
            return res
        
    async def remove_session_data(self, key, query: str =''):
        res = {'success': False, 'message':'unknown error'}
        try:
            _ = await self.redis.json().delete(key, f'.{query}')

            if _:
                res = {'success': True, 'message':f'{key}:{query} - removed from cache'}
            else:
                res['message'] = f'key {key} not found'

        except Exception as e:
            res['message'] = str(e)
        finally:
            return res        

    async def update_item_in_cart(self, session_id, item: dict):
        #TODO: Complete this function, not ready yet.
        res = {'success': False, 'message':'unknown error'}
        try:
            item_to_update = await self.get_session_data(session_id, f'.cart.{item["item_id"]}')
            if item_to_update:
                for key, val in item.items():
                    if key in item_to_update:
                        item_to_update[key] = val
                    else:
                        res['message'] = f'item {item["item_id"]}: key {key} not found'
                        break                        

                _ = await self.redis.json().set(session_id, f'.cart.{item["item_id"]}', item_to_update)
                if _:
                    res = {'success': True, 'message':f'item {item["item_id"]} - updated'}
                else:
                    res['message'] = f'Error updating item {item["item_id"]} in cache'
            else:
                res['message'] = f'item {item["item_id"]} not found in cache'
        except Exception as e:
            res['message'] = str(e)
        finally:
            return res


    async def add_item_to_list(self, session_id, item):
        session_data = await self.get_session_data(session_id)
        items = session_data.get('items', [])
        items.append(item)

        await self.update_item_list(session_id, items)

    async def remove_item_from_list(self, session_id, item_id):
        res = {'success': False, 'message':'unknown error'}
        try:
            _ = await self.remove_session_data(session_id, f'.cart.{item_id}')

            if _['success']:
                res = {'success': True, 'message':f'item {item_id} removed from cart cache'}
            else:
                res['message'] = f'item {item_id} not found in cart cache'
        except Exception as e:
            res['message'] = str(e)
        finally:
            return res
        
    async def cleanup(self):
        await self.redis.aclose()

# Instantiate a SessionManager object
session_manager = SessionManager(redis_url)

__all__ = ['session_manager']