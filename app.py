# app.py - BOT AUTOMÁTICO CORREGIDO
import os
import time
import threading
from flask import Flask, jsonify
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 INICIANDO BOT TRADING - MODO AUTOMÁTICO")
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

# FUNCIÓN PARA INICIAR BOT AUTOMÁTICO
def iniciar_bot_automatico():
    if config_ok and monitor_ok:
        try:
            def ejecutar_bot():
                print("🤖 INICIANDO BUCLE PRINCIPAL DE TRADING AUTOMÁTICO...")
                print("🔄 El bot monitoreará automáticamente cada 2 minutos")
                print("📊 Pares: EURUSD, USDCAD, EURCHF, EURAUD, XAUUSD, XAGUSD, OILUSD, XPTUSD")
                monitor.iniciar_monitoreo()
            
            # Iniciar en un hilo separado
            hilo_bot = threading.Thread(target=ejecutar_bot, daemon=True)
            hilo_bot.start()
            print("✅ Bot de trading AUTOMÁTICO iniciado en segundo plano")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando bot automático: {e}")
            return False
    else:
        print(f"🛑 Bot NO iniciado - Config: {config_ok}, Monitor: {monitor_ok}")
        return False

# INICIAR BOT AUTOMÁTICAMENTE AL ARRANCAR
print("🚀 INICIANDO SISTEMA AUTOMÁTICO...")
bot_iniciado = iniciar_bot_automatico()

if bot_iniciado:
    print("🎯 El bot está ahora monitoreando mercados AUTOMÁTICAMENTE")
    print("⏰ Enviará señales cada 2 minutos cuando detecte oportunidades")
else:
    print("💤 Bot en modo manual - usa endpoints para activar")

# ================= RUTAS FLASK =================

@app.route('/')
def home():
    """Página principal"""
    estado = "ACTIVO" if monitor and hasattr(monitor, 'monitoreando') and monitor.monitoreando else "INICIALIZANDO"
    
    return jsonify({
        "status": estado,
        "service": "Bot Trading Multi-Activos",
        "message": "Bot funcionando correctamente" if estado == "ACTIVO" else "Bot iniciándose",
        "modo": "AUTOMÁTICO" if bot_iniciado else "MANUAL",
        "timestamp": datetime.now().isoformat(),
        "endpoints_available": [
            "/", "/debug", "/test-telegram", "/status", 
            "/estadisticas", "/forzar-analisis/EURUSD", "/iniciar-manual"
        ]
    })

@app.route('/debug')
def debug():
    """Endpoint de diagnóstico completo"""
    bot_activo = monitor and hasattr(monitor, 'monitoreando') and monitor.monitoreando
    
    info = {
        "status": "online",
        "bot_automatico": bot_iniciado,
        "bot_activo": bot_activo,
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "TELEGRAM_TOKEN": "CONFIGURADO" if os.environ.get('TELEGRAM_TOKEN') else "FALTANTE",
            "TELEGRAM_CHAT_ID": "CONFIGURADO" if os.environ.get('TELEGRAM_CHAT_ID') else "FALTANTE",
            "PYTHON_VERSION": os.environ.get('PYTHON_VERSION', '3.13.4'),
            "RENDER": "SI" if os.environ.get('RENDER') else "NO"
        },
        "monitor": {
            "inicializado": monitor is not None,
            "monitoreando": bot_activo,
            "operaciones_activas": len(monitor.gestor.operaciones_activas) if monitor else 0,
            "capital_actual": monitor.capital_actual if monitor else 0,
            "total_operaciones": monitor.total_operaciones if monitor else 0
        },
        "system": {
            "python_version": "3.13.4",
            "flask_status": "running",
            "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "uptime": "ACTIVO"
        }
    }
    return jsonify(info)

@app.route('/test-telegram')
def test_telegram():
    """Probar conexión con Telegram"""
    if not monitor:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    try:
        mensaje = f"🤖 TEST DE CONEXIÓN EXITOSO\nHora: {datetime.now().strftime('%H:%M:%S')}\nBot: Trading Multi-Activos\nModo: {'AUTOMÁTICO' if bot_iniciado else 'MANUAL'}\nServidor: Render"
        exito = monitor.telegram.enviar_mensaje(mensaje)
        
        return jsonify({
            "status": "success" if exito else "error",
            "message": "✅ Mensaje de test enviado a Telegram" if exito else "❌ Error enviando mensaje",
            "modo": "AUTOMÁTICO" if bot_iniciado else "MANUAL",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/status')
def status():
    """Estado del bot"""
    if not monitor:
        return jsonify({"status": "error", "message": "Monitor no inicializado"})
    
    bot_activo = hasattr(monitor, 'monitoreando') and monitor.monitoreando
    
    return jsonify({
        "status": "OPERACIONAL" if bot_activo else "INICIALIZANDO",
        "bot_activo": bot_activo,
        "modo": "AUTOMÁTICO" if bot_iniciado else "MANUAL",
        "operaciones_activas": len(monitor.gestor.operaciones_activas),
        "capital_actual": f"${monitor.capital_actual:.2f}",
        "total_operaciones": monitor.total_operaciones,
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
                "señal_generada": True,
                "señal": {
                    "direccion": señal['direccion'],
                    "precio": señal['precio_actual'],
                    "confianza": señal.get('confianza', 'MEDIA')
                },
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "par": par,
                "señal_generada": False,
                "message": "No se generó señal - condiciones no óptimas",
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

@app.route('/iniciar-manual')
def iniciar_manual():
    """Iniciar bot manualmente si no arrancó automático"""
    global monitor, bot_iniciado
    
    if not monitor:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    if hasattr(monitor, 'monitoreando') and monitor.monitoreando:
        return jsonify({"status": "info", "message": "El bot ya está ejecutándose"})
    
    try:
        def iniciar_bot():
            print("🤖 INICIANDO BOT EN MODO MANUAL...")
            monitor.iniciar_monitoreo()
        
        hilo = threading.Thread(target=iniciar_bot, daemon=True)
        hilo.start()
        bot_iniciado = True
        
        return jsonify({
            "status": "success", 
            "message": "Bot iniciado manualmente",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/reiniciar-riesgo')
def reiniciar_riesgo():
    """Reiniciar contadores de riesgo"""
    if not monitor:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    try:
        monitor.reiniciar_riesgo()
        return jsonify({
            "status": "success",
            "message": "Contadores de riesgo reiniciados",
            "capital_actual": f"${monitor.capital_actual:.2f}",
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
            "/estadisticas", "/forzar-analisis/EURUSD", "/iniciar-manual", "/reiniciar-riesgo"
        ],
        "timestamp": datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error", 
        "message": "Error interno del servidor",
        "timestamp": datetime.now().isoformat()
    }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Servidor web iniciando en puerto {port}")
    print(f"📡 Endpoints disponibles:")
    print(f"   • https://bingx-f9ol.onrender.com/")
    print(f"   • https://bingx-f9ol.onrender.com/debug")
    print(f"   • https://bingx-f9ol.onrender.com/test-telegram")
    print(f"   • https://bingx-f9ol.onrender.com/status")
    print(f"   • https://bingx-f9ol.onrender.com/estadisticas")
    print(f"   • https://bingx-f9ol.onrender.com/forzar-analisis/EURUSD")
    print(f"   • https://bingx-f9ol.onrender.com/iniciar-manual")
    print(f"   • https://bingx-f9ol.onrender.com/reiniciar-riesgo")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False)
