import unittest
from unittest.mock import patch, MagicMock
from farmCoupons.db import DataBase

class TestDataBase(unittest.TestCase):
    def setUp(self):
        # Mock the database connection
        self.mock_db = MagicMock()
        self.db_manager = DataBase(self.mock_db)

    def test_add_proxy(self):
        # Test adding a proxy
        proxy = {'ip': '127.0.0.1', 'port': '8080'}
        self.db_manager.add_proxy(proxy)
        self.mock_db.proxies.insert_one.assert_called_once_with(proxy)

    def test_get_proxy(self):
        # Test retrieving a proxy
        self.mock_db.proxies.find_one.return_value = {'ip': '127.0.0.1', 'port': '8080'}
        proxy = self.db_manager.get_proxy()
        self.assertEqual(proxy['ip'], '127.0.0.1')

    def test_add_coupon(self):
        # Test adding a coupon
        coupon = {'code': 'SAVE10', 'discount': 10}
        self.db_manager.add_coupon(coupon)
        self.mock_db.coupons.insert_one.assert_called_once_with(coupon)

    def test_get_coupon(self):
        # Test retrieving a coupon
        self.mock_db.coupons.find_one.return_value = {'code': 'SAVE10', 'discount': 10}
        coupon = self.db_manager.get_coupon('SAVE10')
        self.assertEqual(coupon['discount'], 10)

    def test_update_coupon(self):
        # Test updating a coupon
        self.db_manager.update_coupon('SAVE10', {'discount': 15})
        self.mock_db.coupons.update_one.assert_called_once_with({'code': 'SAVE10'}, {'$set': {'discount': 15}})

    def test_delete_coupon(self):
        # Test deleting a coupon
        self.db_manager.delete_coupon('SAVE10')
        self.mock_db.coupons.delete_one.assert_called_once_with({'code': 'SAVE10'})

if __name__ == '__main__':
    unittest.main()
