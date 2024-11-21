# Farm Coupons

Farm Coupons is a reworked version of a Big Box Retailer Coupons project. It integrates human-like clicking using PyAutoGUI with browser manipulation through Puppeteer to automate coupon validation processes. I opted for browser automation over requests as I experienced much lower ban rates on the browser.

This project is configured for a specific website, but I won't say who. If you know you know.

Working as of 2024-06-01 - May need updating for UI and network request changes

## Features
- Human-like mouse movements and interactions.
- Automated coupon code entry and validation.
- Database management for storing and retrieving coupon codes.
- Web server for handling coupon operations via a REST API.

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/farm-coupons.git
   cd farm-coupons
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

4. **Set up MongoDB**:
   Ensure MongoDB is running and accessible. Update the `DATABASE_URL` in `farmCoupons/definitions.py` as needed.

## Usage
- **Run the server**:
  ```bash
  python server.py
  ```
- **Manage coupons**:
  Use the `manager.py` script to start and manage coupon processes.
  ```bash
  python manager.py
  ```

## Configuration
- **Environment Variables**: Set up any necessary environment variables in the `.env` file.
- **Database**: Ensure the MongoDB URL is correctly configured in `farmCoupons/definitions.py`.

## Dependencies
- **Python**: FastAPI, PyAutoGUI, Pydantic, pymongo
- **Node.js**: Puppeteer

