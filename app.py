# app.py - BOT CON REACTIVACIÓN AUTOMÁTICA
import os
import time
import threading
import logging
from flask import Flask, jsonify
from datetime import datetime, timedelta

# Configuración robusta de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

print("=" * 70)
print("🚀 BOT TRADING - REACTIVACIÓN AUTOMÁTICA ACTIVADA")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# Estado global mejorado
monitor = None
bot_activo = False
ultima_actividad = datetime.now()
reinicios_automaticos = 0

def log_activo(mensaje):
    """Logging que actualiza timestamp de actividad"""
    global ultima_actividad
    print(f"[ACTIVO] {datetime.now().strftime('%H:%M:%S')} - {mensaje}")
    logger.info(mensaje)
    ultima_actividad = datetime.now()

def inicializar_monitor():
    """Inicializar monitor de mercado"""
    global monitor
    try:
        from monitor_mercado import MonitorMercado
        monitor = MonitorMercado()
        log_activo("✅ Monitor inicializado")
        return True
    except Exception as e:
        log_activo(f"❌ Error inicializando monitor: {e}")
        return False

def verificar_bot_activo():
    """Verificar si el bot está realmente activo"""
    global monitor, bot_activo, ultima_actividad
    
    if not monitor or not hasattr(monitor, 'monitoreando'):
        return False
    
    # Verificar si el bot está monitoreando
    if not monitor.monitoreando:
        log_activo("⚠️ Bot detectado INACTIVO")
        return False
    
    # Verificar tiempo desde última actividad
    tiempo_inactivo = (datetime.now() - ultima_actividad).total_seconds()
    if tiempo_inactivo > 600:  # 10 minutos sin actividad
        log_activo(f"🚨 Bot inactivo por {tiempo_inactivo:.0f} segundos")
        return False
    
    return True

def reactivar_bot():
    """Reactivar el bot si se detuvo"""
    global monitor, bot_activo, reinicios_automaticos
    
    log_activo("🔄 Intentando reactivar bot...")
    
    try:
        # Si el monitor existe pero no está activo, reactivarlo
        if monitor and hasattr(monitor, 'monitoreando') and not monitor.monitoreando:
            log_activo("🔁 Reiniciando monitor existente...")
            monitor.iniciar_monitoreo()
        
        # Si no hay monitor, inicializar uno nuevo
        elif not monitor:
            if inicializar_monitor():
                monitor.iniciar_monitoreo()
        
        # Verificar que se reactivó
        time.sleep(5)
        if monitor and monitor.monitoreando:
            bot_activo = True
            reinicios_automaticos += 1
            log_activo(f"✅ Bot reactivado exitosamente (#{reinicios_automaticos})")
            
            # Notificar por Telegram
            try:
                if hasattr(monitor, 'telegram'):
                    monitor.telegram.enviar_mensaje(
                        f"🔄 BOT REACTIVADO AUTOMÁTICAMENTE\n"
                        f"⏰ {datetime.now().strftime('%H:%M:%S')}\n"
                        f"📊 Reinicio #{reinicios_automaticos}\n"
                        f"✅ Sistema operativo"
                    )
            except Exception as e:
                log_activo(f"⚠️ No se pudo notificar Telegram: {e}")
            
            return True
        else:
            log_activo("❌ No se pudo reactivar el bot")
            return False
            
    except Exception as e:
        log_activo(f"💥 Error reactivando bot: {e}")
        return False

def monitor_continuo_bot():
    """Monitor continuo que mantiene el bot activo"""
    log_activo("🛡️ Iniciando monitor de reactivación automática")
    
    while True:
        try:
            # Verificar cada 2 minutos
            time.sleep(120)
            
            # Verificar estado del bot
            if not verificar_bot_activo():
                log_activo("🚨 Bot inactivo detectado, reactivando...")
                reactivar_bot()
            else:
                # Log de actividad normal cada 10 minutos
                if datetime.now().minute % 10 == 0:
                    log_activo("📊 Bot activo y monitoreando mercados")
                    
        except Exception as e:
            log_activo(f"❌ Error en monitor continuo: {e}")
            time.sleep(60)

# RUTAS FLASK MEJORADAS

@app.route('/')
def home():
    global bot_activo, ultima_actividad, reinicios_automaticos
    
    estado_bot = "ACTIVO" if verificar_bot_activo() else "INACTIVO"
    segundos_inactivo = (datetime.now() - ultima_actividad).total_seconds()
    
    return jsonify({
        "status": "SERVICIO ACTIVO",
        "bot_trading": estado_bot,
        "segundos_desde_ultima_actividad": int(segundos_inactivo),
        "reinicios_automaticos": reinicios_automaticos,
        "ultima_actividad": ultima_actividad.strftime("%H:%M:%S"),
        "timestamp": datetime.now().isoformat(),
        "endpoints_control": [
            "/", "/status", "/reactivar", "/force-cycle",
            "/debug", "/test-telegram"
        ]
    })

@app.route('/status')
def status():
    """Estado detallado del bot"""
    global monitor, bot_activo
    
    estado = verificar_bot_activo()
    tiempo_activo = datetime.now() - ultima_actividad
    
    info = {
        "bot_activo": estado,
        "monitoreando": monitor.monitoreando if monitor and hasattr(monitor, 'monitoreando') else False,
        "tiempo_desde_ultima_actividad_segundos": int(tiempo_activo.total_seconds()),
        "reinicios_automaticos": reinicios_automaticos,
        "operaciones_activas": len(monitor.gestor.operaciones_activas) if monitor else 0,
        "capital_actual": f"${monitor.capital_actual:.2f}" if monitor else "N/A",
        "timestamp": datetime.now().isoformat()
    }
    
    log_activo("📊 Status consultado")
    return jsonify(info)

@app.route('/reactivar')
def reactivar_manual():
    """Reactivación manual inmediata"""
    log_activo("🔄 Reactivación manual solicitada")
    exito = reactivar_bot()
    
    return jsonify({
        "status": "success" if exito else "error",
        "message": "Bot reactivado manualmente" if exito else "Error en reactivación",
        "reinicios_totales": reinicios_automaticos,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/force-cycle')
def force_cycle():
    """Forzar un ciclo de análisis inmediato"""
    global monitor
    
    if not monitor:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    try:
        log_activo("🔁 Ciclo forzado de análisis")
        
        # Analizar un par específico para generar actividad
        from config import TOP_5_PARES
        
        señales_generadas = 0
        for par in TOP_5_PARES[:2]:  # Solo primeros 2 pares
            señal = monitor.analizar_par(par)
            if señal:
                monitor.ejecutar_señal(señal)
                señales_generadas += 1
                break  # Solo una señal por ciclo forzado
        
        return jsonify({
            "status": "success",
            "señales_generadas": señales_generadas,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        log_activo(f"❌ Error en ciclo forzado: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/debug')
def debug():
    """Debug completo"""
    global monitor, bot_activo, ultima_actividad
    
    estado = verificar_bot_activo()
    
    return jsonify({
        "sistema": {
            "bot_activo": estado,
            "flask_activo": True,
            "python_version": "3.13.4",
            "timestamp": datetime.now().isoformat()
        },
        "monitor": {
            "inicializado": monitor is not None,
            "monitoreando": monitor.monitoreando if monitor and hasattr(monitor, 'monitoreando') else False,
            "operaciones_activas": len(monitor.gestor.operaciones_activas) if monitor else 0
        },
        "actividad": {
            "ultima_actividad": ultima_actividad.strftime("%H:%M:%S"),
            "segundos_inactivo": int((datetime.now() - ultima_actividad).total_seconds()),
            "reinicios_automaticos": reinicios_automaticos
        }
    })

# INICIALIZACIÓN AL ARRANCAR

log_activo("🚀 Iniciando sistema de reactivación automática...")

# Inicializar monitor
if inicializar_monitor():
    # Iniciar bot automáticamente
    if reactivar_bot():
        log_activo("✅ Bot iniciado automáticamente al arrancar")
    else:
        log_activo("❌ No se pudo iniciar bot automáticamente")
    
    # Iniciar monitor de reactivación en segundo plano
    hilo_reactivacion = threading.Thread(target=monitor_continuo_bot, daemon=True)
    hilo_reactivacion.start()
    log_activo("🛡️ Monitor de reactivación iniciado")
else:
    log_activo("💥 No se pudo inicializar el sistema")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    log_activo(f"🌐 Servidor iniciando en puerto {port}")
    
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
