#!/usr/bin/env python3
# app.py - Bot Trading para Render.com
import os
import pandas as pd
import numpy as np
import time
import requests
import threading
from datetime import datetime, timedelta
from flask import Flask, jsonify
import logging
from apscheduler.schedulers.background import BackgroundScheduler

# ===================== CONFIGURACIÓN RENDER =====================
app = Flask(__name__)

# Obtener variables de entorno de Render
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Validar variables críticas
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("❌ TELEGRAM_TOKEN y TELEGRAM_CHAT_ID deben estar configurados en Render")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 BOT DE TRADING INICIADO EN RENDER")
print(f"📱 Chat ID: {TELEGRAM_CHAT_ID}")
print("=" * 60)

# ===================== CLASE TELEGRAM BOT =====================
class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        
    def enviar_mensaje(self, mensaje, parse_mode='HTML'):
        """Enviar mensaje a Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': mensaje,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje Telegram: {e}")
            return False
    
    def enviar_señal(self, señal_data):
        """Enviar señal de trading"""
        emoji = "🟢" if señal_data['direccion'] == "COMPRA" else "🔴"
        
        mensaje = f"""
{emoji} <b>NUEVA SEÑAL DETECTADA</b> {emoji}

📈 <b>Par:</b> {señal_data['par']}
🎯 <b>Dirección:</b> {señal_data['direccion']}
💰 <b>Precio Entrada:</b> {señal_data['precio_entrada']:.5f}
⚡ <b>Strength:</b> {señal_data['strength']}/10

📊 <b>Targets:</b>
   TP1: {señal_data['tp1']:.5f} (+1.5%)
   TP2: {señal_data['tp2']:.5f} (+2.5%)

🛡️ <b>Stop Loss:</b> {señal_data['sl']:.5f} (-2.0%)

⏰ <b>Timestamp:</b> {señal_data['timestamp']}
        """
        return self.enviar_mensaje(mensaje)
    
    def enviar_resumen_diario(self, resumen_data):
        """Enviar resumen diario"""
        mensaje = f"""
📊 <b>RESUMEN DIARIO - {resumen_data['fecha']}</b>

📈 <b>Operaciones del día:</b>
   Totales: {resumen_data['total_ops']}
   Ganadoras: {resumen_data['ops_ganadoras']}
   Perdedoras: {resumen_data['ops_perdedoras']}

🎯 <b>Win Rate:</b> {resumen_data['winrate']:.1f}%
💰 <b>Profit Total:</b> {resumen_data['profit_total']:.2f}%

🏆 <b>Mejor Operación:</b> {resumen_data['mejor_op']}
📉 <b>Peor Operación:</b> {resumen_data['peor_op']}

⚡ <b>Eficiencia DCA:</b> {resumen_data['eficiencia_dca']:.1f}%
        """
        return self.enviar_mensaje(mensaje)

# ===================== SISTEMA DE TRADING =====================
class SistemaTrading:
    def __init__(self, telegram_bot):
        self.bot = telegram_bot
        self.operaciones = []
        self.estadisticas = {
            'total_ops': 0,
            'ops_ganadoras': 0,
            'ops_perdedoras': 0,
            'profit_total': 0.0
        }
        
        # Pares óptimos confirmados
        self.pares_activos = ['USDCHF', 'EURUSD', 'EURGBP', 'GBPUSD', 'EURJPY']
        
        # Precios simulados
        self.precios = {
            'USDCHF': 0.8680, 'EURUSD': 1.0850, 'EURGBP': 0.8570,
            'GBPUSD': 1.2650, 'EURJPY': 161.00
        }
    
    def generar_señal_aleatoria(self):
        """Generar señal demo"""
        par = np.random.choice(self.pares_activos)
        direccion = np.random.choice(['COMPRA', 'VENTA'], p=[0.6, 0.4])
        precio_actual = self.precios[par]
        
        # Calcular niveles
        if direccion == 'COMPRA':
            tp1 = precio_actual * 1.015
            tp2 = precio_actual * 1.025
            sl = precio_actual * 0.980
        else:
            tp1 = precio_actual * 0.985
            tp2 = precio_actual * 0.975
            sl = precio_actual * 1.020
        
        señal = {
            'par': par,
            'direccion': direccion,
            'precio_entrada': precio_actual,
            'tp1': tp1,
            'tp2': tp2,
            'sl': sl,
            'strength': np.random.randint(6, 10),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return señal
    
    def procesar_señal(self):
        """Procesar una nueva señal"""
        try:
            señal = self.generar_señal_aleatoria()
            
            # Enviar a Telegram
            self.bot.enviar_señal(señal)
            
            # Simular resultado (para demo)
            resultado = np.random.choice(['TP1', 'TP2', 'SL'], p=[0.4, 0.3, 0.3])
            profit = np.random.uniform(0.5, 3.0) if resultado != 'SL' else np.random.uniform(-1.5, -0.5)
            
            # Actualizar estadísticas
            self.estadisticas['total_ops'] += 1
            self.estadisticas['profit_total'] += profit
            
            if profit > 0:
                self.estadisticas['ops_ganadoras'] += 1
            else:
                self.estadisticas['ops_perdedoras'] += 1
            
            logger.info(f"📈 Señal procesada: {señal['par']} {señal['direccion']} -> {resultado}")
            
        except Exception as e:
            logger.error(f"❌ Error procesando señal: {e}")
    
    def obtener_resumen_diario(self):
        """Obtener resumen del día"""
        total = self.estadisticas['total_ops']
        if total == 0:
            return None
            
        winrate = (self.estadisticas['ops_ganadoras'] / total) * 100
        
        return {
            'fecha': datetime.now().strftime("%Y-%m-%d"),
            'total_ops': total,
            'ops_ganadoras': self.estadisticas['ops_ganadoras'],
            'ops_perdedoras': self.estadisticas['ops_perdedoras'],
            'winrate': winrate,
            'profit_total': self.estadisticas['profit_total'],
            'mejor_op': "USDCHF (+2.8%)",  # Simulado
            'peor_op': "EURJPY (-1.2%)",   # Simulado
            'eficiencia_dca': 85.5          # Simulado
        }

# ===================== INICIALIZACIÓN =====================
# Inicializar bot de Telegram
telegram_bot = TelegramBot(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)

# Inicializar sistema de trading
sistema_trading = SistemaTrading(telegram_bot)

# Configurar scheduler
scheduler = BackgroundScheduler()

# ===================== RUTAS FLASK =====================
@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Trading Monitor Bot",
        "timestamp": datetime.now().isoformat(),
        "operaciones_hoy": sistema_trading.estadisticas['total_ops']
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/enviar-test')
def enviar_test():
    """Ruta para enviar mensaje de prueba"""
    try:
        success = telegram_bot.enviar_mensaje("🤖 <b>BOT ACTIVO EN RENDER</b>\nEl sistema de trading está funcionando correctamente.")
        return jsonify({"status": "success" if success else "error"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route('/generar-señal')
def generar_señal():
    """Ruta para generar señal manual"""
    try:
        sistema_trading.procesar_señal()
        return jsonify({"status": "señal_generada"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

# ===================== TAREAS PROGRAMADAS =====================
def tarea_señales_automaticas():
    """Generar señales automáticamente"""
    sistema_trading.procesar_señal()
    logger.info("🔄 Señal automática generada")

def tarea_resumen_diario():
    """Enviar resumen diario"""
    try:
        resumen = sistema_trading.obtener_resumen_diario()
        if resumen:
            telegram_bot.enviar_resumen_diario(resumen)
            logger.info("📊 Resumen diario enviado")
            
            # Reiniciar estadísticas
            sistema_trading.estadisticas = {
                'total_ops': 0,
                'ops_ganadoras': 0,
                'ops_perdedoras': 0,
                'profit_total': 0.0
            }
    except Exception as e:
        logger.error(f"❌ Error en resumen diario: {e}")

# ===================== INICIALIZACIÓN SCHEDULER =====================
def iniciar_scheduler():
    """Iniciar tareas programadas"""
    # Señales cada 10 minutos (para demo)
    scheduler.add_job(tarea_señales_automaticas, 'interval', minutes=10)
    
    # Resumen diario a las 23:55
    scheduler.add_job(tarea_resumen_diario, 'cron', hour=23, minute=55)
    
    scheduler.start()
    logger.info("⏰ Scheduler iniciado - Señales cada 10min")

# ===================== INICIO DE LA APLICACIÓN =====================
if __name__ == "__main__":
    # Enviar mensaje de inicio
    telegram_bot.enviar_mensaje(
        "🚀 <b>BOT INICIADO EN RENDER</b>\n"
        "Sistema de trading monitor activado\n"
        "📊 Señales automáticas cada 10min\n"
        "📈 Resumen diario a las 23:55"
    )
    
    # Iniciar scheduler
    iniciar_scheduler()
    
    # Ejecutar Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
else:
    # Para Gunicorn
    iniciar_scheduler()
