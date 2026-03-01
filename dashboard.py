from flask import Flask, render_template, jsonify, request
import threading
import time
import logging
from engine import TradeEngine
import os

# Configuración básica
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

app = Flask(__name__)

# Credenciales (Usar variables de entorno para Render/Cloud)
API_KEY = os.environ.get("BINANCE_API_KEY", "4ylvMPr3SNWHSdpNUT1NVCjJJuZ33CKcpCZjaYjOkhStsxYC73IAoXyQRZQf7OW2")
API_SECRET = os.environ.get("BINANCE_API_SECRET", "DtAfLiz730s5tPmVUKEJA2SpxGRUFJhAeiYZq8eDeRH0DaJFxZiVOLxWoDTZkQ6v")

engine = TradeEngine(API_KEY, API_SECRET, testnet=False)

def bot_loop():
    while True:
        try:
            engine.run_cycle()
            time.sleep(30)
        except Exception as e:
            logging.error(f"Loop error: {e}")
            time.sleep(5)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    tf = request.args.get('tf', '1h')
    # Devolver las stats filtradas por el timeframe solicitado
    filtered_stats = {}
    for symbol in engine.current_stats:
        if tf in engine.current_stats[symbol]:
            filtered_stats[symbol] = engine.current_stats[symbol][tf]
            
    return jsonify({
        'stats': filtered_stats,
        'symbols': engine.symbols
    })

@app.route('/api/trading/params', methods=['POST']) # Corrected endpoint name to match index.html
def update_params():
    try:
        data = request.json
        # Map frontend names to engine names
        engine.params['rsi_fast'] = int(data.get('rsi_fast', engine.params['rsi_fast']))
        engine.params['rsi_slow'] = int(data.get('rsi_slow', engine.params['rsi_slow']))
        engine.params['stoch_rsi_len'] = int(data.get('stoch_rsi_len', engine.params['stoch_rsi_len']))
        engine.params['stoch_k_period'] = int(data.get('stoch_k_period', engine.params['stoch_k_period']))
        engine.params['stoch_smooth_k'] = int(data.get('stoch_smooth_k', engine.params['stoch_smooth_k']))
        engine.params['st_factor'] = float(data.get('st_factor', 3.0))
        engine.params['investment_amount'] = float(data.get('investment_amount', 100.0))
        engine.params['trading_timeframe'] = data.get('trading_timeframe', '1h')
        engine.params['stop_loss_pct'] = float(data.get('stop_loss_pct', 5.0))
        engine.params['trailing_stop'] = bool(data.get('trailing_stop', False))
        engine.params['active_strategy'] = int(data.get('active_strategy', 1))
        engine.params['ema_fast'] = int(data.get('ema_fast', 9))
        engine.params['ema_slow'] = int(data.get('ema_slow', 21))
        engine.params['macd_fast'] = int(data.get('macd_fast', 12))
        engine.params['macd_slow'] = int(data.get('macd_slow', 26))
        engine.params['macd_signal'] = int(data.get('macd_signal', 9))
        engine.params['adx_period'] = int(data.get('adx_period', 14))
        engine.params['adx_threshold'] = int(data.get('adx_threshold', 25))
        
        # Strategy 4 Specific
        engine.params['rsi_fast_4'] = int(data.get('rsi_fast_4', 5))
        engine.params['rsi_slow_4'] = int(data.get('rsi_slow_4', 14))
        engine.params['rsi_offset'] = float(data.get('rsi_offset', 0))
        engine.params['st_len_4'] = int(data.get('st_len_4', 14))
        engine.params['st_factor_4'] = float(data.get('st_factor_4', 3.0))
        engine.params['stoch_offset'] = float(data.get('stoch_offset', 30))
        
        # WhatsApp Specific
        engine.params['whatsapp_phone'] = data.get('whatsapp_phone', engine.params['whatsapp_phone'])
        engine.params['whatsapp_apikey'] = data.get('whatsapp_apikey', engine.params['whatsapp_apikey'])
        
        logging.info(f"PARAMS UPDATED: {engine.params}")
        # Force a cycle to apply changes immediately
        engine.run_cycle()
        return jsonify({"status": "success", "params": engine.params})
    except Exception as e:
        logging.error(f"Params update error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/trading/mode', methods=['POST'])
def set_trading_mode():
    data = request.json
    mode = data.get('mode')
    if mode in ['OFF', 'SIM', 'REAL']:
        engine.trading_mode = mode
        logging.info(f"Trading mode set to: {mode}")
        return jsonify({"status": "success", "mode": mode})
    return jsonify({"status": "error", "message": "Invalid mode"}), 400

@app.route('/api/trading/manual', methods=['POST'])
def manual_trade():
    try:
        data = request.json
        action = data.get('action') # BUY or SELL
        symbol = data.get('symbol', 'BTC/USDC')
        
        if engine.trading_mode == "OFF":
            return jsonify({"status": "error", "message": "Trading is OFF. Switch to SIM or REAL."}), 400

        ticker = engine.exchange.fetch_ticker(symbol)
        price = ticker['last']

        if action == "BUY":
            if symbol in engine.active_positions:
                return jsonify({"status": "error", "message": "Position already open"}), 400
            engine.open_position(symbol, price)
            return jsonify({"status": "success", "message": f"Manual BUY {symbol} @ {price}"})
        
        elif action == "SELL":
            if symbol not in engine.active_positions:
                return jsonify({"status": "error", "message": "No active position to close"}), 400
            engine.close_position(symbol, price)
            return jsonify({"status": "success", "message": f"Manual SELL {symbol} @ {price}"})

        return jsonify({"status": "error", "message": "Invalid action"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/trading/history')
def get_trading_history():
    return jsonify(engine.get_trade_history())

@app.route('/api/trading/balance')
def get_trading_balance():
    return jsonify({"balance": engine.get_balance()})

@app.route('/api/trading/panic', methods=['POST'])
def panic_button():
    engine.close_all_positions()
    return jsonify({"message": "PANIC ACTIVATED: All positions closed"})

@app.route('/api/watchlist')
def get_watchlist():
    return jsonify({"watchlist": engine.get_watchlist()})

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    engine.clear_trade_history()
    return jsonify({"status": "success", "message": "History cleared"})

@app.route('/api/history/delete/<int:index>', methods=['POST'])
def delete_trade_record(index):
    if engine.delete_trade(index):
        return jsonify({"status": "success", "message": f"Trade {index} deleted"})
    return jsonify({"status": "error", "message": "Invalid index"}), 400

@app.route('/api/backtest')
def run_backtest():
    symbol = request.args.get('symbol', 'BTC/USDC')
    tf = request.args.get('tf', '1h')
    return jsonify(engine.run_backtest(symbol, tf))

@app.route('/api/history/<path:symbol>')
def history(symbol):
    tf = request.args.get('tf', '1h')
    if symbol in engine.history and tf in engine.history[symbol]:
        h = engine.history[symbol][tf]
        logging.info(f"Serving history for {symbol} ({tf}): {len(h.get('candles', []))} candles, {len(h.get('signals', []))} signals")
        return jsonify(h)
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    # Ejecutar análisis inicial
    engine.run_cycle()
    
    # Hilo del bot
    t = threading.Thread(target=bot_loop, daemon=True)
    t.start()
    
    # Render binding: host 0.0.0.0 and dynamic port
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
