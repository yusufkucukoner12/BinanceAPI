# Binance API Trading Bot

This project is a Python-based trading bot that integrates with the Binance Futures API to automate order management and real-time price monitoring. The bot leverages several computer science concepts to execute trades efficiently, making it ideal for algorithmic trading.

## Features

- **Order Creation**: Automatically places limit or stop-market orders based on your trading strategy.
- **Dynamic Stop-Loss Updates**: The bot continuously monitors market prices and adjusts stop orders dynamically, ensuring optimal risk management.
- **WebSocket Integration**: Utilizes WebSocket to receive real-time price updates from Binance, reducing latency and improving performance.
- **REST API Integration**: Securely communicates with Binance via HTTP requests, using HMAC SHA-256 encryption to sign requests.
- **Asynchronous Event Handling**: Handles market events in real-time, allowing the bot to respond to price changes and manage multiple conditions simultaneously.

## How It Works

- **REST API**: The bot communicates with Binance’s API to place and manage orders. It uses secure request signing via HMAC SHA-256 encryption, ensuring that API calls are authenticated and protected.
  
- **WebSocket for Real-Time Data**: By using WebSocket, the bot establishes a persistent connection to receive real-time market prices without repeatedly sending requests. This approach reduces latency and enables faster reactions to price changes.
  
- **Dynamic Order Management**: The bot implements logic to modify stop-loss orders and cancel orders as the market price changes, ensuring that trades are executed according to predefined strategies.

## Getting Started

### Prerequisites
- Python 3.x
- Binance Futures API account
- `requests`, `websocket-client`, and `hmac` libraries installed

You can install the required dependencies using:

```bash
pip install requests websocket-client
