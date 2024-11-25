# MetaTrader5 Trading API Server

This script provides an HTTP API server using Flask to interact with the MetaTrader5 trading platform. It allows users to perform trading operations such as creating, updating, and deleting orders via API endpoints. The script is designed to handle trading logic and provides detailed logging for tracking activity.

## Features
- **Order Creation**: Create market or pending orders with customizable parameters such as symbol, order type, volume, stop loss, and take profit.
- **Order Update**: Modify existing orders by updating their stop loss or take profit levels.
- **Order Deletion**: Remove pending orders from MetaTrader5.
- **API Server**: Accessible endpoints for remote management of trading operations.
- **Error Logging**: Comprehensive logging for debugging and operational tracking.

## Use Venv

- `py -m venv .venv`
- `.venv\Scripts\activate`

## Requirements

`pip install -r requirements.txt`

## Run

`py .\server.py`