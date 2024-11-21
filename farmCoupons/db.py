import logging
from typing import Dict, Optional
from pymongo import MongoClient
import json
import random
import datetime
import time
from farmCoupons.definitions import DATABASE_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("database.log", mode="a"),
    ]
)

class DataBase:
    """Database manager for handling proxies, coupons, and cookies."""

    def __init__(self, database_name: str = "COUPONS"):
        """
        Initialize the database connection.
        """
        self.database_name = database_name
        self.client = MongoClient(DATABASE_URL)
        self.proxy_db = self.client[self.database_name]["PROXIES"]
        logging.info(f"Connected to database: {self.database_name}")

    def update_proxies(self) -> None:
        """
        Update the proxy list in the database using data from `proxies.txt`.
        """
        if not args.boss:
            logging.info("Proxy updates are disabled for this instance.")
            return

        try:
            proxies = self._load_proxies_from_file("proxies.txt")
            self._update_database_with_proxies(proxies)
        except Exception as e:
            logging.error(f"Error updating proxies: {e}")

    def _load_proxies_from_file(self, filename: str) -> list:
        """
        Load proxy data from a text file and generate the proxy list.
        """
        proxy_data = []
        try:
            with open(filename, "r") as file:
                lines = file.read().splitlines()
                for line in lines:
                    data = line.split(":")
                    if not data:
                        continue

                    if "oxylabs" in data[0]:
                        proxy_data.extend(self._generate_oxylabs_proxies(data))
                    elif "smartproxy" in data[0]:
                        proxy_data.extend(self._generate_smartproxy_proxies(data))
                    elif len(data) == 2:  # Proxy with no authentication
                        proxy_data.append(self._create_proxy_entry(data[0], data[1]))
                    elif len(data) > 2:  # Proxy with authentication
                        proxy_data.append(self._create_proxy_entry(data[0], data[1], data[2], data[3]))
            logging.info(f"Loaded proxies from {filename}. Total proxies: {len(proxy_data)}")
        except FileNotFoundError:
            logging.error(f"Error: File {filename} not found.")
        except Exception as e:
            logging.error(f"Error reading proxies from {filename}: {e}")
        return proxy_data

    def _generate_oxylabs_proxies(self, data: list) -> list:
        """Generate a list of Oxylabs proxies with random session IDs."""
        return [
            {
                "protocol": "http",
                "host": data[0],
                "port": data[1],
                "username": f"{data[2]}-sessid-{random.randint(1000000, 10000000)}",
                "password": data[3],
            }
            for _ in range(20)
        ]

    def _generate_smartproxy_proxies(self, data: list) -> list:
        """Generate a list of Smartproxy proxies based on the port range."""
        port_range = range(10001, 10201) if int(data[1]) == 10000 else range(20001, 20201)
        return [
            {
                "protocol": "http",
                "host": data[0],
                "port": port,
                "username": data[2],
                "password": data[3],
            }
            for port in random.sample(port_range, 10 if int(data[1]) == 10000 else 20)
        ]

    def _create_proxy_entry(self, host: str, port: str, username: Optional[str] = None, password: Optional[str] = None) -> Dict:
        """Create a proxy entry dictionary."""
        return {"protocol": "http", "host": host, "port": port, "username": username, "password": password}

    def _update_database_with_proxies(self, proxies: list) -> None:
        """Update the database with the given proxies."""
        try:
            with open("proxies.json", "w") as file:
                json.dump(proxies, file)

            self.proxy_db.update_many({}, {"$set": {"active": False}})
            for proxy in proxies:
                self.proxy_db.update_one(
                    {"host": proxy["host"], "port": proxy["port"], "username": proxy["username"], "password": proxy["password"]},
                    {"$set": {"active": True}},
                    upsert=True
                )
            self.proxy_db.delete_many({"active": False})
            logging.info("Proxy database updated successfully.")
        except Exception as e:
            logging.error(f"Error updating proxy database: {e}")

    def get_coupon_code(self, coupon_type: str) -> Optional[str]:
        """Retrieve a coupon code for a given coupon type."""
        try:
            if random.random() < 0.2:  # 1 in 5 chance of validating a coupon
                db = self.client[self.database_name][coupon_type]
                master_code = self.client[self.database_name]["MASTER_CODES"].find_one(
                    {"type": coupon_type, "loaded": True}, sort=[("_id", -1)]
                )["masterCode"]
                old_coupon = db.find_one(
                    {
                        "used": False,
                        "code": {"$regex": f"\\d{{10}}{master_code}\\d"},
                        "lastValidDate": {"$lt": datetime.datetime.utcnow() - datetime.timedelta(days=5)},
                    },
                    sort=[("lastValidDate", 1)],
                )
                if old_coupon:
                    return old_coupon["code"]

            db = self.client[self.database_name][f"{coupon_type}_TEST_POOL"]
            documents = list(
                db.find({"tested": False, "$or": [{"testing": False}, {"testing": {"$exists": False}}]}).limit(10)
            )
            if not documents:
                documents = list(db.find({"tested": False, "testing": True}).limit(10))
            if not documents:
                return None

            document = random.choice(documents)
            db.update_one({"code": document["code"]}, {"$set": {"testing": True}})
            return document["code"]
        except Exception as e:
            logging.error(f"Error retrieving coupon code: {e}")
            return None

    def insert_cookie(self, cookies: dict) -> None:
        """Insert a set of cookies into the database."""
        try:
            self.client[self.database_name]["COOKIES"].insert_one({"value": cookies})
            logging.info("Cookies inserted successfully.")
        except Exception as e:
            logging.error(f"Error inserting cookies: {e}")

    def get_new_proxy(self) -> Dict:
        """Retrieve a new proxy that hasn't been used recently."""
        while True:
            try:
                proxy = self.proxy_db.find_one({}, sort=[("lastUsed", 1)])
                if proxy:
                    self.proxy_db.update_one(
                        {"host": proxy["host"], "port": proxy["port"], "username": proxy["username"], "password": proxy["password"]},
                        {"$set": {"lastUsed": datetime.datetime.utcnow()}}
                    )
                    return proxy
                logging.warning("No proxies available. Retrying in 5 seconds...")
                time.sleep(5)
            except Exception as e:
                logging.error(f"Error retrieving new proxy: {e}")
