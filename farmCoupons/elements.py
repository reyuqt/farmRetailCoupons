# Standard library imports
import random
from typing import Optional, Dict

# Third-party imports
import pyautogui

# Local application imports
from farmCoupons.definitions import ASSET_DIRECTORY

# Constants
MOUSE_MOVEMENTS = [
    pyautogui.easeInQuad,
    pyautogui.easeOutQuad,
    pyautogui.easeInOutQuad,
    pyautogui.easeInOutSine,
    pyautogui.easeInQuint
]
pyautogui.PAUSE = 2

class Element:
    def __init__(self, file_location: str, adjustments: Optional[Dict], confidence=0.9):
        """
        Initialize an Element with a file location, optional adjustments, and confidence level.
        """
        self.file_location = file_location
        self.adjustments = adjustments
        self.confidence = confidence

    def coordinates(self, sample=False) -> tuple:
        """
        Calculate random coordinates within the element's bounding box.
        """
        if sample:
            locations = list(
                pyautogui.locateAllOnScreen(self.file_location, grayscale=True, confidence=self.confidence))
            location = random.choice(locations)
        else:
            location = pyautogui.locateOnScreen(self.file_location, grayscale=True, confidence=self.confidence)
        x1 = location.left + 5
        y1 = location.top + 5
        width = location.width - 10
        height = location.height - 10
        x = random.randint(x1, x1 + width)
        y = random.randint(y1, y1 + height)
        return x, y

    def click(self, clicks=1, sample=False) -> bool:
        """
        Simulate a mouse click on the element.
        """
        tween = random.choice(MOUSE_MOVEMENTS)
        duration = round(random.uniform(1, 3), 2)
        x, y = self.coordinates(sample)
        pyautogui.click(x=x, y=y, duration=duration, tween=tween, clicks=clicks)
        return True

    def hover(self) -> None:
        """
        Simulate a mouse hover over the element.
        """
        tween = random.choice(MOUSE_MOVEMENTS)
        duration = round(random.uniform(1, 3), 2)
        x, y = self.coordinates()
        pyautogui.moveTo(x, y, duration=duration, tween=tween)

    def type(self, string):
        """
        Simulate typing a string into the element.
        """
        interval = round(random.uniform(0.2, 0.5), 2)
        self.click()
        pyautogui.typewrite(string, interval=interval)
        pyautogui.press("Enter")


# Pre-defined elements
START_SHOPPING = Element(f'{ASSET_DIRECTORY}/start_shopping.png', adjustments=None, confidence=0.7)
ADD_TO_CART = Element(f'{ASSET_DIRECTORY}/add_to_cart.png', adjustments=None, confidence=0.7)
ADD_TO_CARTV1 = Element(f'{ASSET_DIRECTORY}/v1/add_to_cart.png', adjustments=None, confidence=0.7)
ADD_TO_CARTV2 = Element(f'{ASSET_DIRECTORY}/v2/add_to_cart.png', adjustments=None, confidence=0.7)
OPEN_PROMO_CODE = Element(f'{ASSET_DIRECTORY}/open_promo_code.png', adjustments=None, confidence=0.7)
INPUT_PROMO_CODE = Element(f'{ASSET_DIRECTORY}/input_promo_code.png', adjustments=None, confidence=0.7)
APPLY_PROMO_CODE = Element(f'{ASSET_DIRECTORY}/apply_promo_code.png', adjustments=None, confidence=0.7)
REMOVE_PROMO_CODE = Element(f'{ASSET_DIRECTORY}/remove_promo_code.png', adjustments=None, confidence=0.7)
CLOSE_POPUP = Element(f'{ASSET_DIRECTORY}/close_popup.png', adjustments=None, confidence=0.7)
SHOP = Element(f'{ASSET_DIRECTORY}/shop.png', adjustments=None, confidence=0.7)
SHOPV1 = Element(f'{ASSET_DIRECTORY}/v1/shop.png', adjustments=None, confidence=0.7)
TARGET = Element(f'{ASSET_DIRECTORY}/tmpy.png', adjustments=None, confidence=0.7)
VIEW_CART = Element(f'{ASSET_DIRECTORY}/view_cart.png', adjustments=None, confidence=0.7)
CHANGE_SHIPPING = Element(f'{ASSET_DIRECTORY}/change_shipping.png', adjustments=None, confidence=0.7)
