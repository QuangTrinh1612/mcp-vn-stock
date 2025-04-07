from src.vnstock_agent.server import YahooFinanceServer

# Example usage
# if __name__ == "__main__":
#     # Configure logging
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
#     # Create Yahoo Finance agent
#     agent = YahooFinanceAgent()
    
#     # Example: Get ticker info
#     ticker_info = agent.get_ticker_info("AAPL")
#     print(f"Ticker info: {ticker_info}")
    
#     # Example: Get price history
#     price_history = agent.get_price_history("AAPL", period="1mo")
#     print(f"Price history: {price_history}")

# Example for running the server
if __name__ == "__main__":
    # Create and run the server
    server = YahooFinanceServer()
    server.run()