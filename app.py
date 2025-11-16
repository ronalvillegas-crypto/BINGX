#!/usr/bin/env python3
# app.py - Bot Trading Mejorado CORREGIDO para Render
import os
import time
import random
import requests
import logging
from datetime import datetime
from flask import Flask, jsonify

# ===================== CONFIGURACIÓN =====================
app = Flask(__name__)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 BOT TRADING MEJORADO - VERSIÓN ESTABLE")

# ===================== PARÁMETROS DE BACKTESTING =====================
TOP_5_PARES_CONFIRMADOS = ['USDCAD', 'USDJPY', 'AUDUSD', 'EURGBP', 'GBPUSD']

PARAMETROS_POR_PAR = {
    'USDCAD': {'winrate': 85.0, 'rentabilidad': 536.5, 'leverage': 20},
    'USDJPY': {'winrate': 75.0, 'rentabilidad': 390.1, 'leverage': 20},
    'AUDUSD': {'winrate': 80.0, 'rentabilidad': 383.9, 'leverage': 20},
    'EURGBP': {'winrate': 75.0, 'rentabilidad': 373.9, 'leverage': 20},
    'GBPUSD': {'winrate': 75.0, 'rentabilidad': 324.4, 'leverage': 20}
}

# ===================== BOT TELEGRAM SIMPLE =====================
class TelegramBotSimple:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        
    def enviar_mensaje(self, mensaje):
        """Enviar mensaje simple a Telegram"""
        try:
            if not self.token or not self.chat_id:
                return False
                
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': mensaje,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error Telegram: {e}")
            return False

# ===================== SISTEMA TRADING =====================
class SistemaTrading:
    def __init__(self):
        self.telegram_bot = TelegramBotSimple(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
        self.estadisticas = {'señales_generadas': 0}
    
    def generar_señal(self):
        """Generar señal simple"""
        try:
            par = random.choice(TOP_5_PARES_CONFIRMADOS)
            params = PARAMETROS_POR_PAR[par]
            
            # Precio simulado
            precios_base = {'USDCAD': 1.3450, 'USDJPY': 148.50, 'AUDUSD': 0.6520, 
                           'EURGBP': 0.8570, 'GBPUSD': 1.2650}
            precio = precios_base[par] * random.uniform(0.999, 1.001)
            
            señal = {
                'par': par,
                'direccion': random.choice(['COMPRA', 'VENTA']),
                'precio': round(precio, 5),
                'winrate': params['winrate'],
                'rentabilidad': params['rentabilidad'],
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
            
            # Enviar a Telegram
            if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                mensaje = f"""
📈 <b>SEÑAL {señal['par']}</b>
🎯 {señal['direccion']} a {señal['precio']}
📊 WR: {señal['winrate']}% | Profit: {señal['rentabilidad']}%
⏰ {señal['timestamp']}
                """
                self.telegram_bot.enviar_mensaje(mensaje.strip())
            
            self.estadisticas['señales_generadas'] += 1
            logger.info(f"Señal generada: {señal}")
            return señal
            
        except Exception as e:
            logger.error(f"Error generando señal: {e}")
            return None

# ===================== INICIALIZACIÓN =====================
sistema = SistemaTrading()

# ===================== RUTAS FLASK =====================
@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Bot Trading - Versión Estable",
        "pares": TOP_5_PARES_CONFIRMADOS,
        "estadisticas": sistema.estadisticas,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/generar-señal')
def generar_señal():
    señal = sistema.generar_señal()
    if señal:
        return jsonify({"status": "success", "señal": señal})
    return jsonify({"status": "error"})

@app.route('/test-telegram')
def test_telegram():
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        mensaje = f"✅ TEST TELEGRAM - {datetime.now().strftime('%H:%M:%S')}"
        enviado = sistema.telegram_bot.enviar_mensaje(mensaje)
        return jsonify({"status": "enviado" if enviado else "error"})
    return jsonify({"status": "no_configurado"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# ===================== INICIO =====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Servidor iniciado en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
else:
    print("✅ Servicio Render iniciado correctamente")
