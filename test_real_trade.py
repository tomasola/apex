import requests
import time
import sys

BASE_URL = "http://127.0.0.1:5001/api/trading"

def test_trade():
    print("--- INICIANDO PRUEBA DE TRADING REAL ---")
    
    # 1. Asegurar que estamos en modo REAL
    print("Configurando modo REAL...")
    r = requests.post(f"{BASE_URL}/mode", json={"mode": "REAL"})
    if r.status_code != 200:
        print(f"Error al cambiar modo: {r.text}")
        return
    print("Modo REAL confirmado.")

    # 2. Ejecutar COMPRA manual
    print("Ejecutando COMPRA manual de BTC/USDC (50 USDC)...")
    r = requests.post(f"{BASE_URL}/manual", json={"action": "BUY", "symbol": "BTC/USDC"})
    if r.status_code != 200:
        print(f"Error en COMPRA: {r.text}")
        return
    print(f"COMPRA EXITOSA: {r.json().get('message')}")

    # 3. Esperar 1 minuto
    print("Esperando 60 segundos para vender...")
    time.sleep(60)

    # 4. Ejecutar VENTA manual
    print("Ejecutando VENTA manual de BTC/USDC...")
    r = requests.post(f"{BASE_URL}/manual", json={"action": "SELL", "symbol": "BTC/USDC"})
    if r.status_code != 200:
        print(f"Error en VENTA: {r.text}")
        return
    print(f"VENTA EXITOSA: {r.json().get('message')}")
    
    print("--- PRUEBA FINALIZADA CON ÉXITO ---")

if __name__ == "__main__":
    test_trade()
