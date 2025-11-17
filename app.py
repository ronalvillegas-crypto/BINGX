# app.py - Servidor optimizado para Render
import os
import threading
import time
from flask import Flask, jsonify

app = Flask(__name__)

print("🚀 BOT TRADING OPTIMIZADO - ESTRATEGIA S/R ETAPA 1")

# Importar después de definir app para evitar importaciones circulares
monitor = None
monitoreo_iniciado = False

def inicializar_monitor():
    """Inicializar el monitor de forma lazy"""
    global monitor
    if monitor is None:
        try:
            from monitor_mercado import MonitorMercado
            monitor = MonitorMercado()
            print("✅ Monitor inicializado correctamente")
        except Exception as e:
            print(f"❌ Error inicializando monitor: {e}")
            return None
    return monitor

@app.route('/')
def home():
    monitor_obj = inicializar_monitor()
    if monitor_obj is None:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    return jsonify({
        "status": "online", 
        "service": "Bot Trading Optimizado - Estrategia S/R Etapa 1",
        "pares_activos": ["EURUSD", "USDCAD", "EURCHF", "EURAUD"],
        "estrategia": "S/R Etapa 1 Optimizada",
        "modulos_activos": [
            "Monitor Mercado", "Estrategia S/R", "Gestor Operaciones", "Telegram Bot"
        ],
        "operaciones_activas": len(monitor_obj.gestor.operaciones_activas),
        "monitoreo_activo": monitor_obj.monitoreando
    })

@app.route('/iniciar-monitoreo')
def iniciar_monitoreo():
    """Iniciar monitoreo en tiempo real"""
    global monitoreo_iniciado
    monitor_obj = inicializar_monitor()
    
    if monitor_obj is None:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    if not monitor_obj.monitoreando:
        threading.Thread(target=monitor_obj.iniciar_monitoreo, daemon=True).start()
        monitoreo_iniciado = True
        return jsonify({
            "status": "monitoreo_iniciado",
            "mensaje": "Monitoreo S/R Etapa 1 ACTIVADO",
            "pares": ["EURUSD", "USDCAD", "EURCHF", "EURAUD"]
        })
    return jsonify({"status": "ya_activo", "mensaje": "Monitoreo ya está activo"})

@app.route('/detener-monitoreo')
def detener_monitoreo():
    """Detener monitoreo"""
    monitor_obj = inicializar_monitor()
    if monitor_obj is None:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    monitor_obj.detener_monitoreo()
    return jsonify({
        "status": "monitoreo_detenido", 
        "mensaje": "Monitoreo DETENIDO"
    })

@app.route('/estadisticas')
def estadisticas():
    monitor_obj = inicializar_monitor()
    if monitor_obj is None:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    return jsonify({
        "estadisticas": monitor_obj.gestor.estadisticas,
        "operaciones_activas": monitor_obj.gestor.operaciones_activas,
        "historial_reciente": monitor_obj.gestor.historial[-5:] if monitor_obj.gestor.historial else [],
        "riesgo": monitor_obj.obtener_estadisticas_riesgo()
    })

@app.route('/forzar-señal/<par>')
def forzar_señal(par):
    """Forzar una señal manualmente (para testing)"""
    monitor_obj = inicializar_monitor()
    if monitor_obj is None:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    if par not in ['EURUSD', 'USDCAD', 'EURCHF', 'EURAUD']:
        return jsonify({"status": "error", "mensaje": "Par no válido. Pares permitidos: EURUSD, USDCAD, EURCHF, EURAUD"})
    
    from estrategia_dca import EstrategiaDCA
    estrategia = EstrategiaDCA()
    señal = estrategia.generar_señal_real(par)
    
    if señal:
        monitor_obj.ejecutar_señal(señal)
        return jsonify({
            "status": "señal_forzada",
            "par": par,
            "señal": señal
        })
    else:
        return jsonify({
            "status": "no_señal",
            "mensaje": "No se pudo generar señal - condiciones no óptimas"
        })

@app.route('/status')
def status():
    """Estado del sistema"""
    monitor_obj = inicializar_monitor()
    if monitor_obj is None:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    return jsonify({
        "monitoreo_activo": monitor_obj.monitoreando,
        "operaciones_activas": len(monitor_obj.gestor.operaciones_activas),
        "total_operaciones": monitor_obj.gestor.estadisticas['total_operaciones'],
        "operaciones_ganadoras": monitor_obj.gestor.estadisticas['operaciones_ganadoras'],
        "profit_total": monitor_obj.gestor.estadisticas['profit_total'],
        "estrategia": "S/R Etapa 1 Optimizada",
        "pares_activos": ["EURUSD", "USDCAD", "EURCHF", "EURAUD"]
    })

@app.route('/health')
def health():
    """Endpoint de salud para Render"""
    return jsonify({"status": "healthy", "timestamp": time.time()})

# Iniciar monitoreo automáticamente al primer request
@app.before_request
def iniciar_monitoreo_auto():
    global monitoreo_iniciado
    if not monitoreo_iniciado:
        print("🔄 Iniciando monitoreo automático S/R Etapa 1...")
        monitor_obj = inicializar_monitor()
        if monitor_obj:
            threading.Thread(target=monitor_obj.iniciar_monitoreo, daemon=True).start()
            monitoreo_iniciado = True

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Servidor optimizado iniciado en puerto {port}")
    print(f"🔍 Monitoreo S/R Etapa 1: ACTIVADO AL PRIMER REQUEST")
    app.run(host="0.0.0.0", port=port, debug=False)
