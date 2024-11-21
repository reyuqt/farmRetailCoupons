import logging
from urllib.request import Request
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pyautogui
from farmCoupons.elements import (
    START_SHOPPING, OPEN_PROMO_CODE, INPUT_PROMO_CODE, APPLY_PROMO_CODE,
    REMOVE_PROMO_CODE, CLOSE_POPUP, ADD_TO_CART, VIEW_CART, SHOP, TARGET,
    CHANGE_SHIPPING, SHOPV1, ADD_TO_CARTV1, ADD_TO_CARTV2
)
from pydantic import BaseModel
from farmCoupons.db import DataBase

# Initialize database
db = DataBase(database_name="RETAIL_STORE")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server.log", mode="a"),
    ]
)

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Cookie(BaseModel):
    value: list


@app.get('/start_shopping')
async def start_shopping():
    """Start the shopping process."""
    logging.info("Attempting to start shopping.")
    START_SHOPPING.click()
    return {"message": "success"}


@app.get('/change_shipping')
async def change_shipping():
    """Change the shipping address."""
    logging.info("Changing shipping address.")
    CHANGE_SHIPPING.click()
    return {"message": "success"}


@app.get('/open_promo_code')
async def open_promo_code():
    """Open the promo code input section."""
    logging.info("Opening promo code input.")
    OPEN_PROMO_CODE.click()
    return {"message": "success"}


@app.get('/input_promo_code/{coupon_type}')
async def input_promo_code(coupon_type: str):
    """
    Input a promo code for a given coupon type.
    
    Args:
        coupon_type: The type of coupon to apply.

    Returns:
        The applied promo code.
    """
    logging.info(f"Fetching promo code for coupon type: {coupon_type}")
    coupon_code = db.get_coupon_code(coupon_type)
    logging.info(f"Fetched coupon code: {coupon_code}")
    
    INPUT_PROMO_CODE.type(coupon_code)
    logging.info("Typed promo code successfully.")
    APPLY_PROMO_CODE.click()
    logging.info("Applied promo code successfully.")
    
    return {"message": coupon_code}


@app.get('/valid_coupon/{coupon_type}/{coupon_code}')
async def valid_coupon_code(coupon_type: str, coupon_code: str):
    """
    Mark a coupon as valid in the database.

    Args:
        coupon_type: The type of coupon.
        coupon_code: The validated coupon code.

    Returns:
        Confirmation message.
    """
    logging.info(f"Marking coupon {coupon_code} as valid for type {coupon_type}.")
    db.update_valid_coupon(coupon_type, coupon_code)
    return {"message": coupon_code}


@app.get('/invalid_coupon/{coupon_type}/{coupon_code}')
async def invalid_coupon_code(coupon_type: str, coupon_code: str):
    """
    Mark a coupon as invalid in the database.

    Args:
        coupon_type: The type of coupon.
        coupon_code: The invalidated coupon code.

    Returns:
        Confirmation message.
    """
    logging.info(f"Marking coupon {coupon_code} as invalid for type {coupon_type}.")
    db.update_invalid_coupon(coupon_type, coupon_code)
    return {"message": coupon_code}


@app.get('/remove_promo_code')
async def remove_promo_code():
    """Remove the applied promo code."""
    logging.info("Removing promo code.")
    REMOVE_PROMO_CODE.click()
    return {"message": "success"}


@app.get('/close_popup')
async def close_popup():
    """Close any pop-up dialogs."""
    logging.info("Closing popup.")
    CLOSE_POPUP.click()
    return {"message": "success"}


@app.get('/add_to_cart')
async def add_to_cart():
    """Add an item to the shopping cart."""
    logging.info("Attempting to add item to cart.")
    try:
        ADD_TO_CART.click(sample=False)
        logging.info("Added to cart using default method.")
    except Exception as e:
        logging.warning(f"Failed to add to cart using default method: {e}")
        try:
            ADD_TO_CARTV1.click(sample=False)
            logging.info("Added to cart using method V1.")
        except Exception as e:
            logging.warning(f"Failed to add to cart using method V1: {e}")
            ADD_TO_CARTV2.click(sample=False)
            logging.info("Added to cart using method V2.")
    return {"message": "success"}


@app.post('/save_cookies')
async def save_cookie(cookie: Cookie):
    """
    Save cookies to the database.

    Args:
        cookie: The cookie data to save.

    Returns:
        Confirmation message.
    """
    logging.info("Saving cookies to the database.")
    db.insert_cookie(cookie.value)
    return {"message": "success"}


@app.get('/view_cart')
async def view_cart():
    """View the contents of the shopping cart."""
    logging.info("Viewing cart.")
    VIEW_CART.click()
    return {"message": "success"}


@app.get('/shop')
async def shop():
    """Start the shopping experience."""
    logging.info("Starting shop action.")
    try:
        SHOP.click()
        logging.info("Shop action completed.")
    except Exception as e:
        logging.warning(f"Default shop action failed: {e}. Using fallback.")
        SHOPV1.click()
        logging.info("Fallback shop action completed.")
    return {"message": "success"}


@app.get('/click_mouse')
async def click_mouse():
    """Simulate a mouse click."""
    logging.info("Simulating mouse click.")
    pyautogui.click()
    return {"message": "success"}


@app.get('/click')
async def click():
    """Perform a click on the target element."""
    logging.info("Clicking on the target element.")
    TARGET.click()
    return {"message": "success"}
