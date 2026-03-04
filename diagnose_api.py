import ccxt
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def diagnose():
    api_key = os.environ.get("BINANCE_API_KEY")
    api_secret = os.environ.get("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        logging.error("❌ API Keys NOT FOUND in environment variables.")
        logging.info("Please set them using:")
        logging.info('setx BINANCE_API_KEY "tu_key"')
        logging.info('setx BINANCE_API_SECRET "tu_secret"')
        return

    logging.info(f"✅ API Keys found (ending in ...{api_key[-4:]})")

    try:
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
        
        logging.info("Connecting to Binance...")
        balance = exchange.fetch_balance()
        
        usdc_free = balance.get('USDC', {}).get('free', 0.0)
        usdc_total = balance.get('USDC', {}).get('total', 0.0)
        
        logging.info(f"💰 USDC Balance: Free={usdc_free}, Total={usdc_total}")
        
        if usdc_free < 10:
            logging.warning("⚠️ Low USDC balance. Real trades might fail due to minimum order size.")
        
        # Check permissions
        logging.info("Checking API permissions...")
        # Most CCXT methods don't explicitly return "permissions", so we test a small private fetch
        try:
            exchange.fetch_open_orders('BTC/USDC')
            logging.info("✅ API Permission: Trading/Private data access confirmed.")
        except Exception as e:
            logging.error(f"❌ API Permission Error: {e}")

        logging.info("\n--- DIAGNOSIS COMPLETE ---")
        if usdc_free > 10:
            logging.info("🚀 System seems ready for REAL trading. Ensure you click 'REAL' in the dashboard.")
        else:
            logging.error("❌ System NOT ready: Insufficient USDC balance.")

    except Exception as e:
        logging.error(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    diagnose()
