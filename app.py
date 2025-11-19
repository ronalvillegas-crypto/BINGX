# app.py - BOT OPTIMIZADO PARA PYTHON 3.13.4
import os
import time
import threading
import logging
from flask import Flask, jsonify
from datetime import datetime, timedelta

# Configurar logging robusto para Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 60)
print("🚀 INICIANDO BOT TRADING - PYTHON 3.13.4")
print("🔧 Optimizado para Render con Reinicio Automático")
print("=" * 60)

app = Flask(__name__)

# Variables globales para gestión de estado
monitor = None
bot_iniciado = False
ultimo_reinicio = datetime.now()
ciclos_completados = 0
errores_consecutivos = 0

def verificar_configuracion():
    """Verificar configuración de manera robusta"""
    try:
        token = os.environ.get('TELEGRAM_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        logger.info("🔍 Verificando configuración...")
        logger.info(f"   TELEGRAM_TOKEN: {'✅' if token else '❌ NO CONFIGURADO'}")
        logger.info(f"   TELEGRAM_CHAT_ID: {'✅' if chat_id else '❌ NO CONFIGURADO'}")
        
        if not token or not chat_id:
            logger.error("❌ ERROR: Variables de entorno faltantes")
            return False
        
        logger.info("✅ Configuración Telegram: OK")
        return True
    except Exception as e:
        logger.error(f"❌ Error verificando configuración: {e}")
        return False

def inicializar_monitor():
    """Inicializar monitor con manejo de errores mejorado"""
    global monitor
    try:
        # Importación diferida para evitar problemas de circularidad
        from monitor_mercado import MonitorMercado
        monitor = MonitorMercado()
        logger.info("✅ Monitor de mercado inicializado CORRECTAMENTE")
        return True
    except Exception as e:
        logger.error(f"❌ Error inicializando monitor: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_salud_bot():
    """Verificar salud del bot periódicamente"""
    global monitor, errores_consecutivos
    
    if not monitor:
        logger.warning("⚠️ Monitor no está disponible")
        errores_consecutivos += 1
        return False
    
    try:
        # Verificar si el monitor está respondiendo
        if hasattr(monitor, 'monitoreando'):
            stats = monitor.obtener_estadisticas_riesgo()
            logger.info(f"❤️  Salud OK - Capital: ${stats.get('capital_actual', 0):.2f}")
            errores_consecutivos = 0
            return True
        else:
            logger.warning("⚠️ Monitor no tiene atributo 'monitoreando'")
            errores_consecutivos += 1
            return False
    except Exception as e:
        logger.error(f"💔 Error en verificación de salud: {e}")
        errores_consecutivos += 1
        return False

def reiniciar_bot_suave():
    """Reinicio suave del bot sin interrumpir operaciones activas"""
    global monitor, bot_iniciado, ultimo_reinicio
    
    logger.info("🔄 INICIANDO REINICIO SUAVE DEL BOT...")
    
    try:
        # No detener el monitor completamente, solo reinicializar componentes
        if monitor and hasattr(monitor, 'gestor'):
            # Limpiar operaciones antiguas pero mantener estado
            ops_activas = len(monitor.gestor.operaciones_activas)
            logger.info(f"📊 Operaciones activas antes del reinicio: {ops_activas}")
        
        # Reimportar módulos para limpiar memoria
        import importlib
        import sys
        
        modulos_a_recargar = ['monitor_mercado', 'estrategia_dca', 'gestor_operaciones']
        for modulo in modulos_a_recargar:
            if modulo in sys.modules:
                importlib.reload(sys.modules[modulo])
                logger.info(f"🔄 Módulo {modulo} recargado")
        
        # Reinicializar monitor
        if inicializar_monitor():
            bot_iniciado = iniciar_bot_automatico()
            ultimo_reinicio = datetime.now()
            
            if bot_iniciado:
                logger.info("✅ Reinicio suave EXITOSO")
                # Notificar por Telegram
                try:
                    if monitor and hasattr(monitor, 'telegram'):
                        monitor.telegram.enviar_mensaje(
                            f"🔄 BOT REINICIADO SUAVEMENTE\n"
                            f"⏰ Hora: {datetime.now().strftime('%H:%M:%S')}\n"
                            f"📊 Estado: OPERATIVO - Python 3.13.4"
                        )
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo enviar notificación Telegram: {e}")
                
                return True
        
        logger.error("❌ Reinicio suave FALLIDO")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error en reinicio suave: {e}")
        return False

def monitor_salud_continuo():
    """Monitorear salud continuamente y reiniciar si es necesario"""
    global ciclos_completados, errores_consecutivos
    
    while True:
        try:
            time.sleep(300)  # Verificar cada 5 minutos
            ciclos_completados += 1
            
            logger.info(f"🔍 Ciclo de salud #{ciclos_completados} - Errores consecutivos: {errores_consecutivos}")
            
            # Verificar salud actual
            salud_ok = verificar_salud_bot()
            
            if not salud_ok:
                logger.warning("⚠️ Salud del bot comprometida")
                
                # Reiniciar si hay muchos errores consecutivos
                if errores_consecutivos >= 3:
                    logger.warning("🔄 Demasiados errores consecutivos, reiniciando...")
                    reiniciar_bot_suave()
            
            # Reinicio preventivo cada 4 horas
            tiempo_desde_reinicio = (datetime.now() - ultimo_reinicio).total_seconds()
            if tiempo_desde_reinicio > 14400:  # 4 horas
                logger.info("🔄 Reinicio preventivo programado (4 horas)")
                reiniciar_bot_suave()
                
            # Limpiar memoria cada 10 ciclos
            if ciclos_completados % 10 == 0:
                import gc
                gc.collect()
                logger.info("🧹 Limpieza de memoria ejecutada")
                
        except Exception as e:
            logger.error(f"❌ Error en monitor de salud: {e}")
            time.sleep(60)  # Esperar 1 minuto antes de reintentar

def iniciar_bot_automatico():
    """Iniciar bot automático con manejo de errores"""
    global monitor, bot_iniciado
    
    if not monitor:
        logger.error("❌ Monitor no disponible para iniciar bot")
        return False
        
    try:
        def ejecutar_bot():
            global bot_iniciado
            try:
                logger.info("🤖 INICIANDO BUCLE PRINCIPAL DE TRADING...")
                logger.info("🔄 Monitoreo automático activado")
                monitor.iniciar_monitoreo()
            except Exception as e:
                logger.error(f"❌ Error en bucle principal: {e}")
                bot_iniciado = False
        
        # Iniciar en un hilo separado
        hilo_bot = threading.Thread(target=ejecutar_bot, daemon=True, name="BotTrading")
        hilo_bot.start()
        
        # Esperar a que se inicie
        time.sleep(5)
        
        # Verificar que se inició correctamente
        if hasattr(monitor, 'monitoreando') and monitor.monitoreando:
            logger.info("✅ Bot de trading AUTOMÁTICO iniciado correctamente")
            return True
        else:
            logger.warning("⚠️ Bot iniciado pero estado incierto")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error iniciando bot automático: {e}")
        return False

# ================= INICIALIZACIÓN =================

logger.info("🚀 INICIANDO SISTEMA CON REINICIO AUTOMÁTICO...")

# Verificar configuración primero
config_ok = verificar_configuracion()

if config_ok:
    # Inicializar monitor
    monitor_ok = inicializar_monitor()
    
    if monitor_ok:
        # Iniciar bot automático
        bot_iniciado = iniciar_bot_automatico()
        
        # Iniciar monitor de salud en segundo plano
        hilo_salud = threading.Thread(target=monitor_salud_continuo, daemon=True, name="MonitorSalud")
        hilo_salud.start()
        logger.info("✅ Monitor de salud iniciado en segundo plano")
        
        logger.info("🎯 SISTEMA INICIADO CORRECTAMENTE")
        logger.info(f"📊 Bot automático: {'✅ ACTIVO' if bot_iniciado else '⚠️ INCIERTO'}")
    else:
        logger.error("❌ No se pudo inicializar el monitor")
else:
    logger.error("❌ Configuración incorrecta, bot no iniciado")

# ================= RUTAS FLASK MEJORADAS =================

@app.route('/')
def home():
    global monitor, bot_iniciado, ultimo_reinicio, ciclos_completados, errores_consecutivos
    
    salud_ok = verificar_salud_bot()
    estado = "ACTIVO" if salud_ok else "PROBLEMAS"
    
    return jsonify({
        "status": estado,
        "service": "Bot Trading Multi-Activos",
        "python_version": "3.13.4",
        "modo": "AUTOMÁTICO" if bot_iniciado else "MANUAL",
        "ultimo_reinicio": ultimo_reinicio.isoformat(),
        "ciclos_salud": ciclos_completados,
        "errores_consecutivos": errores_consecutivos,
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/", "/status", "/salud", "/debug", 
            "/reiniciar", "/estadisticas", "/test-telegram"
        ]
    })

@app.route('/status')
def status():
    """Estado detallado del sistema"""
    global monitor, bot_iniciado
    
    salud_ok = verificar_salud_bot()
    
    info = {
        "sistema": {
            "status": "OPERATIVO" if salud_ok else "PROBLEMAS",
            "python_version": "3.13.4",
            "servidor": "Render",
            "timestamp": datetime.now().isoformat()
        },
        "bot": {
            "iniciado": bot_iniciado,
            "monitoreando": monitor.monitoreando if monitor and hasattr(monitor, 'monitoreando') else False,
            "operaciones_activas": len(monitor.gestor.operaciones_activas) if monitor else 0,
            "capital_actual": f"${monitor.capital_actual:.2f}" if monitor else "$0.00"
        },
        "rendimiento": {
            "ciclos_salud": ciclos_completados,
            "errores_consecutivos": errores_consecutivos,
            "ultimo_reinicio": ultimo_reinicio.strftime("%H:%M:%S")
        }
    }
    
    return jsonify(info)

@app.route('/salud')
def salud():
    """Endpoint de verificación de salud rápido"""
    salud_ok = verificar_salud_bot()
    
    return jsonify({
        "status": "OK" if salud_ok else "PROBLEMAS",
        "timestamp": datetime.now().isoformat(),
        "response_time": "instant"
    })

@app.route('/reiniciar')
def reiniciar_manual():
    """Reiniciar manualmente el bot"""
    exito = reiniciar_bot_suave()
    
    return jsonify({
        "status": "success" if exito else "error",
        "message": "Reinicio manual ejecutado" if exito else "Error en reinicio",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/debug')
def debug():
    """Debug completo del sistema"""
    global monitor, bot_iniciado, ultimo_reinicio, ciclos_completados
    
    salud_ok = verificar_salud_bot()
    
    # Información de memoria
    import psutil
    import os
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    debug_info = {
        "status": "online",
        "salud": "OK" if salud_ok else "PROBLEMAS",
        "python_version": "3.13.4",
        "memoria_uso_mb": round(memory_info.rss / 1024 / 1024, 2),
        "bot": {
            "automatico": bot_iniciado,
            "activo": monitor.monitoreando if monitor and hasattr(monitor, 'monitoreando') else False,
            "operaciones_activas": len(monitor.gestor.operaciones_activas) if monitor else 0,
            "capital_actual": monitor.capital_actual if monitor else 0
        },
        "sistema": {
            "ciclos_salud": ciclos_completados,
            "ultimo_reinicio": ultimo_reinicio.isoformat(),
            "tiempo_activo_horas": round((datetime.now() - ultimo_reinicio).total_seconds() / 3600, 2)
        },
        "environment": {
            "TELEGRAM_TOKEN": "CONFIGURADO" if os.environ.get('TELEGRAM_TOKEN') else "FALTANTE",
            "TELEGRAM_CHAT_ID": "CONFIGURADO" if os.environ.get('TELEGRAM_CHAT_ID') else "FALTANTE",
            "RENDER": "SI" if os.environ.get('RENDER') else "NO"
        }
    }
    return jsonify(debug_info)

# Mantén tus otras rutas existentes...

@app.route('/test-telegram')
def test_telegram():
    """Probar Telegram"""
    if not monitor:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    try:
        mensaje = f"🤖 TEST BOT PYTHON 3.13.4\nHora: {datetime.now().strftime('%H:%M:%S')}\nStatus: {'ACTIVO' if bot_iniciado else 'INACTIVO'}\nSalud: {'OK' if verificar_salud_bot() else 'PROBLEMAS'}"
        exito = monitor.telegram.enviar_mensaje(mensaje)
        
        return jsonify({
            "status": "success" if exito else "error",
            "message": "✅ Test Telegram enviado" if exito else "❌ Error enviando test",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Manejo de errores global
@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": "error", "message": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"status": "error", "message": "Error interno del servidor"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🌐 Servidor web iniciando en puerto {port}")
    logger.info("📡 Endpoints disponibles:")
    logger.info("   • / - Estado general")
    logger.info("   • /status - Estado detallado")
    logger.info("   • /salud - Verificación rápida")
    logger.info("   • /debug - Información completa")
    logger.info("   • /reiniciar - Reinicio manual")
    logger.info("   • /test-telegram - Probar Telegram")
    
    app.run(
        host="0.0.0.0", 
        port=port, 
        debug=False,
        threaded=True
    )
