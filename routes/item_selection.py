from decouple import config
from config.logging import logging
from config.monogodb import mongo_client
from config.SessionManager import session_manager
from routes.order import confirm_order
from kafka import KafkaProducer
from fastapi import APIRouter, HTTPException, Request, Depends, Cookie
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import json
import uuid

item_selection = APIRouter()

logger = logging.getLogger("ITEM SELECT ENDPOINT")
db = mongo_client['transactions']['items']


# Create a Jinja2Templates instance with the path to your 'templates' folder
templates = Jinja2Templates(directory="templates")

ITEM_SELECT_KAFKA_TOPIC = config('ITEM_SELECT_KAFKA_TOPIC')
KAFKA_BOOTSTRAP_SERVERS = config('KAFKA_BROKER_ENDPOINTS').split(',')

producer = KafkaProducer(
    bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS,
    value_serializer = lambda x: json.dumps(x).encode('utf-8'),
    acks='all'
)

logger.info("item_selection endpoint initiated")


@item_selection.get('/get_discount/')
async def get_discount(coupon_code: str):
    try:
        res = {'valid': False, 'discount': None}
        
        if not coupon_code:
            raise TypeError("The `coupon_code` parameter is required.")

        discount = await session_manager.get_coupon_code_value(coupon_code)

        if discount:
            res['valid'] = True
            res['discount'] = discount
        
    except Exception as e:
        logger.error(f'ITEMS SELECTION - ERROR getting coupon code: {str(e)}')
    finally:
        return res

@item_selection.get("/get_session_id/")
async def get_or_create_session(session_id: Optional[str] = Cookie(None)):
    session_id = session_id if type(session_id)==str else ''

    session_exists = await session_manager.session_exists(session_id)

    if session_exists == 0:
        new_session_id = str(uuid.uuid4())
        await session_manager.set_session_data(
            new_session_id, 
            {
                "user_id": None,
                "first_name": None,
                "last_name": None,
                "email": None,
                "cart": [],
                "total_cost": 0.0,
                "amount_paid": 0.0,
                "coupon_code": None,
                "discount": 0.0
            }
        )

        return new_session_id

    return session_id


@item_selection.get('/get_session_data/')
async def get_session_data(session_id: str = Depends(get_or_create_session)):
    session_data = await session_manager.get_session_data(session_id)

    response = JSONResponse(content=None)
    response.set_cookie(key="session_id", value=session_id)

    if session_data['success']:
        response = JSONResponse(content={"sessionData": session_data['data']})
    
    return response

@item_selection.post("/add_to_cart/")
async def add_to_cart(
    item_id: str,
    quantity: int,
    session_id: str = Depends(get_or_create_session)
):
    return session_id
    # # Add the item to the cart associated with the session
    # session = sessions[session_id]
    # session["cart"][item_id] = session["cart"].get(item_id, 0) + quantity

    # return {"message": "Item added to cart successfully", "cart": session["cart"]}

@item_selection.post("/remove_from_cart/")
async def remove_from_cart(
    item_id: str,
    session_id: str = Depends(get_or_create_session)
):
    session = sessions[session_id]
    cart = session["cart"]
    
    # Remove the item from the cart
    del cart[item_id]

    return {"message": "Item removed cart successfully", "cart": session["cart"]}

def calculate_total_cost(items, discount: str = None):
    # Calculate the total cost of items in the cart
    # STUIPED CODE: it doesn't take into account the quantity of the item.
    total_cost = 0
    item_ids = [item['item_id'] for item in items]
    
    pipeline = [
        {
            '$match': {
                'item_id': {'$in': item_ids}
            }
        },
        {
            '$group': {
                '_id': None,
                'total_price': {'$sum': '$price'}
            }
        }
    ]

    # Execute the aggregation pipeline
    result = list(db.aggregate(pipeline))

    # Extract the total price (if items were found)
    if result:
        total_cost = result[0]['total_price']
    else:
        raise Exception('error getting items prices')
    
    total_cost *= DISCOUNTS.get(discount, 1)

    return total_cost    


@item_selection.get('/about', response_class=HTMLResponse)
async def about(request: Request):
    logger.info('/about/ visited')
    try:
        # Render the 'items.html' template with the items data
        return templates.TemplateResponse("html/about.html", {"request": request})
    
    except HTTPException as e:
        logger.error(f'get items HTTPException: {str(e)}')
        return HTMLResponse(content=f"<h1>HTTP Error: {str(e)}</h1>", status_code=500)
    
    except Exception as e:
        logger.error(f'get items General Error: {str(e)}')
        return HTMLResponse(content=f"<h1>General Error: {str(e)}</h1>", status_code=500)
    
    finally:
        logger.info(f'getting /about page ended')


@item_selection.get('/', response_class=HTMLResponse)
async def get_items(request: Request):
    logger.info('/index/ started')
    try:
        all_items = list(db.find({}))

        # Render the 'items.html' template with the items data
        return templates.TemplateResponse("html/items.html", {"request": request, "items": all_items})
    
    except HTTPException as e:
        logger.error(f'get items HTTPException: {str(e)}')
        return HTMLResponse(content=f"<h1>HTTP Error: {str(e)}</h1>", status_code=500)
    
    except Exception as e:
        logger.error(f'get items General Error: {str(e)}')
        return HTMLResponse(content=f"<h1>General Error: {str(e)}</h1>", status_code=500)
    
    finally:
        logger.info(f'get items confirmation process ended')



@item_selection.post("/submit_order/")
async def submit_order(
    first_name: str   = None, 
    last_name:  str   = None, 
    email:      str   = None, 
    discount:   str   = None, 
    session_id: str   = Depends(get_or_create_session)
):
    try:
        if not session["cart"]:
            raise HTTPException(status_code=400, detail="The cart is empty")

        assert first_name is not None and type(first_name)==str
        assert last_name  is not None and type(last_name)==str
        assert email      is not None and type(email)==str

        session    = sessions[session_id]
        first_name = first_name
        last_name  = last_name
        email      = email
        items      = [{"item_id": item_id, "quantity": quantity} for item_id, quantity in session["cart"].items()]
        discount   = DISCOUNTS.get(discount, 0.0)

        # Process the order (store in the database, calculate total cost, etc.)
        order_id = str(uuid.uuid4())
        orders[order_id] = {
            "user_id": None,  # You can set this to the user's ID if they are logged in
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "items": items,
            "total_cost": calculate_total_cost(items, discount),
            "discount": discount
        }

        order_confirmation = await confirm_order(orders[order_id])

        if order_confirmation["status"]:
            # Clear the cart and session data for this order
            session["cart"] = {}

        return order_confirmation
    
    except Exception as e:
        return HTTPException(detail=f'{str(e)}', status_code=400)
    
    finally:
        #logging.INFO('')
        pass