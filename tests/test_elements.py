from PIL import Image
import unittest
from unittest.mock import patch, MagicMock
from farmCoupons.elements import Element

class TestElement(unittest.TestCase):
    def setUp(self):
        # Initialize an Element instance for testing
        self.element = Element(file_location='farmCoupons/assets/add_to_cart.png', adjustments=None, confidence=0.9)
                # Open the image
        self.image = Image.open('farmCoupons/assets/add_to_cart.png')
        self.image.show()

    def tearDown(self):
        # Close the image after tests
        self.image.close()

    @patch('pyautogui.click')
    def test_click(self, mock_click):
        # Test the click method
        self.element.click()
        mock_click.assert_called_once()

    @patch('pyautogui.moveTo')
    def test_hover(self, mock_moveTo):
        # Test the hover method
        self.element.hover()
        mock_moveTo.assert_called_once()

    @patch('pyautogui.typewrite')
    @patch('pyautogui.press')
    def test_type(self, mock_press, mock_typewrite):
        # Test the type method
        self.element.type('test')
        mock_typewrite.assert_called_once_with('test', interval=unittest.mock.ANY)
        mock_press.assert_called_once_with('Enter')

    def test_coordinates(self):
        # Test the coordinates method
        x, y = self.element.coordinates()
        self.assertIsInstance(x, int)
        self.assertIsInstance(y, int)

if __name__ == '__main__':
    unittest.main()
