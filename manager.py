# Standard library imports
import argparse
import datetime
import json
import os
import platform
import random
import subprocess
import sys
import time
from shutil import which
from subprocess import Popen
from typing import List, Dict, Union, Final
import logging

# Third-party imports
import schedule

# Local application imports
from farmCoupons.definitions import PUPPETEER_PROFILE_DIR
from farmCoupons.db import DataBase

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("manager.log", mode="a"),
    ]
)
database = DataBase(database_name="RETAIL_STORE")
# Constants
RUN_TIME = 10
USERNAME = os.getlogin()
ROOT_PATH = os.getcwd()
NODE_PATH = which('node')
LOG_PATH = os.path.join(ROOT_PATH, 'LOGS')
PYTHON_PATH = sys.executable

# Argument Parser
parser = argparse.ArgumentParser(description="Manage coupon processes.")
parser.add_argument("-c", "--chrome", help="Path to Chrome executable to use with Puppeteer")
parser.add_argument("-C", "--coupons", help="Coupon arguments separated by commas", default="TWENTY_OFF_HUNDRED")
parser.add_argument("-b", "--boss", help="Set this to True for the main coupon manager", default=False, action="store_true")
parser.add_argument("-d", "--delay", type=int, help="Delay for testing ban rate effect", default=10)
parser.add_argument("-v", "--vpn", help="Use VPN", default=False, action="store_true")

args = parser.parse_args()
ACTIVE_COUPONS = [x.strip() for x in args.coupons.split(",") if x]

COUPONS = [
    {"coupon_type": 'TEN_OFF', "min_required": 0},
    {"coupon_type": 'TEN_OFF_ADVANTAGE', "min_required": 0},
    {"coupon_type": 'TWENTY_OFF_HUNDRED', "min_required": 0},
    {"coupon_type": 'TEN_OFF_FIFTY', "min_required": 0},
    {"coupon_type": 'TWENTY_OFF_HUNDRED_PRO', "min_required": 0},
    {"coupon_type": 'TWENTY_OFF', "min_required": 0},
]


class ProcessNotRunning(Exception):
    """Exception raised when attempting to interact with a non-running process."""
    pass


def is_running(func):
    """
    Decorator to ensure a process is running before executing a function.
    """
    def wrapper(self, *args, **kwargs):
        if self.process is None:
            raise ProcessNotRunning("Process is not running.")
        return func(self, *args, **kwargs)
    return wrapper


class Manager:
    """Manager for coordinating coupon processes."""
    def __init__(self, num_of_workers: int):
        self.num_of_workers: Final[int] = num_of_workers
        self.processes_running: List = []
        self.processes_ready: List = []
        self.processes_finished: List = []

    def run(self):
        """Run the manager workflow."""
        self.check_processes()
        self.assign_processes()
        self.start_processes()

    def check_processes(self):
        """Check and manage the state of running processes."""
        active_processes = self.processes_running[:]
        self.processes_running.clear()

        for process in active_processes:
            runtime = round(process.runtime(), 2)
            logging.info(f"[{process.coupon_type}] Runtime: {runtime} seconds")

            if process.runtime() > TIMEOUT:
                logging.warning(f"Process {process.coupon_type} timed out. Killing...")
                process.kill()

            if process.complete():
                logging.info(f"Process {process.coupon_type} completed.")
                self.processes_finished.append(process)
            else:
                self.processes_running.append(process)

    def assign_processes(self):
        """Assign new processes if necessary."""
        if not self.processes_running:
            new_process = Worker(coupon_type=self._choose_coupon(), proxy=database.get_new_proxy())
            self.processes_ready.append(new_process)

    def start_processes(self):
        """Start ready processes."""
        while self.processes_ready:
            time.sleep(random.randint(10, 30))
            process = self.processes_ready.pop()
            process.start()
            logging.info(f"Started process for {process.coupon_type}")
            self.processes_running.append(process)

    def _choose_coupon(self) -> str:
        """Choose a coupon type based on availability."""
        for coupon in ACTIVE_COUPONS:
            if database.get_count(coupon) < 30:
                return coupon
        return "TEN_OFF"

    def shutdown(self):
        """Clean up all running and pending processes."""
        for process in self.processes_running:
            process.kill()
        self.processes_ready.clear()
        self.processes_finished.clear()
        logging.info("Shutdown complete.")


def launch_script(commands: List[str]):
    """Launch a script as a detached process."""
    kwargs = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if platform.system() == 'Windows' else {"start_new_session": True}
    Popen(commands, **kwargs)


# Initialize database and manager
database = Database()
manager = Manager(num_of_workers=sum(coupon["min_required"] for coupon in COUPONS))

if __name__ == "__main__":
    manager.run()
    schedule.every(10).minutes.do(manager.run)
    while True:
        schedule.run_pending()
        time.sleep(1)
