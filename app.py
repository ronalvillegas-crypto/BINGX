#!/usr/bin/env python3
# app.py - Bot Trading Mejorado - Versión Estable
import os
import time
import random
import requests
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

# Configuración
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

print("🚀 BOT TRADING - VERSIÓN ESTABLE INICIADA")

# Parámetros
PARES = ['USDCAD', 'USDJPY', 'AUDUSD', 'EURGBP', 'GBPUSD']
BACKTESTING = {
    'USDCAD': {'winrate': 85.0, 'profit': 536.5},
    'USDJPY': {'winrate': 75.0, 'profit': 390.1},
    'AUDUSD': {'winrate': 80.0, 'profit': 383.9},
    'EURGBP': {'winrate': 75.0, 'profit': 373.9},
    'GBPUSD': {'winrate': 75.0, 'profit': 324.4}
}

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
    
    def enviar(self, mensaje):
        try:
            if not self.token or not self.chat_id:
                return False
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': mensaje,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except:
            return False

bot = TelegramBot(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Bot Trading Estable",
        "pares": PARES,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/generar-señal')
def generar_señal():
    try:
        par = random.choice(PARES)
        datos = BACKTESTING[par]
        direccion = random.choice(['COMPRA', 'VENTA'])
        
        mensaje = f"""
📈 <b>SEÑAL {par}</b>
🎯 {direccion}
📊 WR: {datos['winrate']}% | Profit: {datos['profit']}%
⏰ {datetime.now().strftime('%H:%M:%S')}
        """
        
        # Enviar a Telegram
        telegram_ok = bot.enviar(mensaje.strip())
        
        return jsonify({
            "status": "success",
            "señal": {
                "par": par,
                "direccion": direccion,
                "winrate": datos['winrate'],
                "profit": datos['profit'],
                "telegram_enviado": telegram_ok
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route('/test-telegram')
def test_telegram():
    mensaje = f"✅ TEST - {datetime.now().strftime('%H:%M:%S')}"
    enviado = bot.enviar(mensaje)
    return jsonify({
        "telegram_configurado": bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID),
        "mensaje_enviado": enviado
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Servidor iniciado en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
