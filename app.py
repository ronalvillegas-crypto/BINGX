# app.py - CON INICIALIZACIÓN CORREGIDA
import os
import time
import threading
from flask import Flask, jsonify
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 INICIANDO BOT TRADING - SIN IMPORTACIONES CIRCULARES")
print("=" * 60)

app = Flask(__name__)

# Verificar configuración primero
def verificar_configuracion():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    print(f"🔍 Verificando configuración...")
    print(f"   TELEGRAM_TOKEN: {'✅' if token else '❌ NO CONFIGURADO'}")
    print(f"   TELEGRAM_CHAT_ID: {'✅' if chat_id else '❌ NO CONFIGURADO'}")
    
    if not token or not chat_id:
        print("❌ ERROR CRÍTICO: Variables de entorno faltantes")
        print("💡 Solución: Ve a Render.com → Tu servicio → Environment → Add Environment Variables")
        return False
    
    print("✅ Configuración Telegram: OK")
    return True

# Inicializar monitor CON MANEJO DE ERRORES MEJORADO
monitor = None
def inicializar_monitor():
    global monitor
    try:
        from monitor_mercado import MonitorMercado
        monitor = MonitorMercado()
        print("✅ Monitor de mercado inicializado CORRECTAMENTE")
        return True
    except Exception as e:
        print(f"❌ Error inicializando monitor: {e}")
        import traceback
        traceback.print_exc()
        return False

# Inicializar y verificar
config_ok = verificar_configuracion()
monitor_ok = inicializar_monitor()

# Iniciar bot en segundo plano si todo está correcto
if config_ok and monitor_ok:
    try:
        def iniciar_bot():
            print("🤖 INICIANDO BUCLE PRINCIPAL DE TRADING...")
            monitor.iniciar_monitoreo()
        
        hilo_bot = threading.Thread(target=iniciar_bot, daemon=True)
        hilo_bot.start()
        print("✅ Bot de trading iniciado en segundo plano")
        
    except Exception as e:
        print(f"❌ Error iniciando bot: {e}")
else:
    print(f"🛑 Bot NO iniciado - Config: {config_ok}, Monitor: {monitor_ok}")

# ================= RUTAS FLASK =================
# ... (el resto del código de las rutas se mantiene igual que antes)
# [MANTENER TODO EL CÓDIGO DE RUTAS QUE TE ENVIÉ ANTES]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Servidor web iniciando en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
