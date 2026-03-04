import ccxt
import os
import json
from dotenv import load_dotenv

def audit():
    load_dotenv()
    exchange = ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_API_SECRET'),
        'enableRateLimit': True
    })
    
    # Check if we should use sandbox
    # (The dashboard uses testnet=False in the current code, but let's check both or just follow dashboard)
    # The dashboard says engine = TradeEngine(API_KEY, API_SECRET, testnet=False)
    # So it's REAL account.
    
    try:
        balance = exchange.fetch_balance()
        total_usdc = 0
        details = []
        
        for coin, qty in balance['total'].items():
            if qty <= 0:
                continue
            
            val = 0
            price = 0
            try:
                if coin == 'USDC':
                    val = qty
                    price = 1.0
                elif coin == 'BNB':
                    # Special case for BNB often used for fees
                    ticker = exchange.fetch_ticker('BNB/USDC')
                    price = ticker['last']
                    val = qty * price
                else:
                    # Generic fetch for LD tokens or other holdings
                    base = coin[2:] if coin.startswith('LD') else coin
                    if base == 'USDC':
                        val = qty
                        price = 1.0
                    else:
                        ticker = exchange.fetch_ticker(f"{base}/USDC")
                        price = ticker['last']
                        val = qty * price
                
                total_usdc += val
                details.append({
                    'asset': coin,
                    'qty': qty,
                    'price': price,
                    'value_usdc': round(val, 2)
                })
            except Exception as e:
                details.append({
                    'asset': coin,
                    'qty': qty,
                    'error': str(e)
                })
        
        print(f"\n--- AUDIT DE BALANCE TOTAL ---")
        print(f"Total en USDC: {round(total_usdc, 2)}")
        print("\nDesglose:")
        for d in details:
            if 'error' in d:
                print(f"- {d['asset']}: {d['qty']} (Precio no encontrado)")
            else:
                print(f"- {d['asset']}: {d['qty']} | Valor: {d['value_usdc']} USDC (@{d['price']})")
                
    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    audit()
