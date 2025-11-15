#!/usr/bin/env python3
# app.py - Trading Bot compatible con Render
import os
import requests
from datetime import datetime
from flask import Flask, jsonify
import logging

# ===================== CONFIGURACIÓN =====================
app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 INICIANDO BOT EN RENDER...")

class TelegramBot:
    def __init__(self):
        self.token = os.environ.get('TELEGRAM_TOKEN')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
    def enviar_mensaje(self, mensaje):
        try:
            if not self.token or not self.chat_id:
                print("⚠️ Variables de Telegram no configuradas")
                return False
                
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': mensaje,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error Telegram: {e}")
            return False

# Inicializar bot
telegram_bot = TelegramBot()

# ===================== RUTAS =====================
@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Trading Monitor Bot", 
        "timestamp": datetime.now().isoformat(),
        "message": "Bot funcionando correctamente en Render"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/test-telegram')
def test_telegram():
    """Ruta para probar Telegram"""
    if telegram_bot.enviar_mensaje("🤖 <b>BOT ACTIVO EN RENDER</b>\nPrueba exitosa - Sistema online"):
        return jsonify({"status": "mensaje_enviado"})
    return jsonify({"status": "error_telegram"})

@app.route('/info')
def info():
    return jsonify({
        "python_version": os.environ.get('PYTHON_VERSION', 'No detectado'),
        "telegram_configured": bool(telegram_bot.token and telegram_bot.chat_id)
    })

# ===================== INICIO =====================
if __name__ == "__main__":
    # Enviar mensaje de inicio si Telegram está configurado
    if telegram_bot.token and telegram_bot.chat_id:
        telegram_bot.enviar_mensaje(
            "🚀 <b>BOT INICIADO EN RENDER</b>\n"
            "Sistema de trading monitor activado\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
    
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Iniciando servidor en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
