# app.py - CON DIAGNÓSTICO Y RUTAS FIX
import os
import time
import threading
from flask import Flask, jsonify
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 INICIANDO BOT TRADING - MODO DIAGNÓSTICO COMPLETO")
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

# Inicializar monitor
monitor = None
try:
    from monitor_mercado import MonitorMercado
    monitor = MonitorMercado()
    print("✅ Monitor de mercado inicializado")
except Exception as e:
    print(f"❌ Error inicializando monitor: {e}")

# Iniciar bot en segundo plano si la configuración es correcta
if monitor and verificar_configuracion():
    try:
        def iniciar_bot():
            print("🤖 INICIANDO BUCLE PRINCIPAL DE TRADING...")
            print("📊 Monitoreando pares:", ['EURUSD', 'USDCAD', 'EURCHF', 'EURAUD', 'XAUUSD', 'XAGUSD', 'OILUSD', 'XPTUSD'])
            monitor.iniciar_monitoreo()
        
        hilo_bot = threading.Thread(target=iniciar_bot, daemon=True)
        hilo_bot.start()
        print("✅ Bot de trading iniciado en segundo plano")
        
    except Exception as e:
        print(f"❌ Error iniciando bot: {e}")
else:
    print("🛑 Bot NO iniciado - Configuración incompleta")

# ================= RUTAS FLASK =================

@app.route('/')
def home():
    """Página principal"""
    return jsonify({
        "status": "ACTIVO" if monitor and monitor.monitoreando else "CONFIGURANDO",
        "service": "Bot Trading Multi-Activos",
        "message": "Usa /debug para diagnóstico completo",
        "timestamp": datetime.now().isoformat(),
        "endpoints_available": ["/", "/debug", "/test-telegram", "/status", "/forzar-analisis/EURUSD"]
    })

@app.route('/debug')
def debug():
    """Endpoint de diagnóstico completo"""
    info = {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "TELEGRAM_TOKEN": "CONFIGURADO" if os.environ.get('TELEGRAM_TOKEN') else "FALTANTE",
            "TELEGRAM_CHAT_ID": "CONFIGURADO" if os.environ.get('TELEGRAM_CHAT_ID') else "FALTANTE",
            "PYTHON_VERSION": os.environ.get('PYTHON_VERSION', '3.13.4')
        },
        "monitor": {
            "inicializado": monitor is not None,
            "monitoreando": monitor.monitoreando if monitor else False,
            "operaciones_activas": len(monitor.gestor.operaciones_activas) if monitor else 0,
            "capital_actual": monitor.capital_actual if monitor else 0
        },
        "system": {
            "python_version": "3.13.4",
            "flask_status": "running"
        }
    }
    return jsonify(info)

@app.route('/test-telegram')
def test_telegram():
    """Probar conexión con Telegram"""
    if not monitor:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    try:
        mensaje = f"🤖 TEST DE CONEXIÓN EXITOSO\nHora: {datetime.now().strftime('%H:%M:%S')}\nBot: Trading Multi-Activos"
        exito = monitor.telegram.enviar_mensaje(mensaje)
        
        return jsonify({
            "status": "success" if exito else "error",
            "message": "✅ Mensaje de test enviado a Telegram" if exito else "❌ Error enviando mensaje",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/status')
def status():
    """Estado del bot"""
    return jsonify({
        "status": "OPERACIONAL" if monitor and monitor.monitoreando else "INICIALIZANDO",
        "bot_activo": monitor.monitoreando if monitor else False,
        "operaciones_activas": len(monitor.gestor.operaciones_activas) if monitor else 0,
        "ultima_actualizacion": datetime.now().isoformat()
    })

@app.route('/forzar-analisis/<par>')
def forzar_analisis(par):
    """Forzar análisis de un par específico"""
    if not monitor:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    pares_permitidos = ['EURUSD', 'USDCAD', 'EURCHF', 'EURAUD', 'XAUUSD', 'XAGUSD', 'OILUSD', 'XPTUSD']
    
    if par not in pares_permitidos:
        return jsonify({
            "status": "error", 
            "message": f"Par no válido. Usa: {', '.join(pares_permitidos)}"
        })
    
    try:
        print(f"🔍 Forzando análisis de {par}...")
        señal = monitor.analizar_par(par)
        
        if señal:
            print(f"🎯 Señal generada para {par}")
            monitor.ejecutar_señal(señal)
        
        return jsonify({
            "par": par,
            "señal_generada": señal is not None,
            "señal": señal,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/estadisticas')
def estadisticas():
    """Estadísticas del bot"""
    if not monitor:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    try:
        stats = monitor.obtener_estadisticas_riesgo()
        return jsonify({
            "status": "success",
            "estadisticas": stats,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint no encontrado",
        "endpoints_available": [
            "/", "/debug", "/test-telegram", "/status", 
            "/estadisticas", "/forzar-analisis/EURUSD"
        ]
    }), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Servidor web iniciando en puerto {port}")
    print(f"📡 Endpoints disponibles:")
    print(f"   • https://bingx-f9ol.onrender.com/")
    print(f"   • https://bingx-f9ol.onrender.com/debug")
    print(f"   • https://bingx-f9ol.onrender.com/test-telegram")
    print(f"   • https://bingx-f9ol.onrender.com/forzar-analisis/EURUSD")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False)
