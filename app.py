# app.py - Servidor con monitoreo en tiempo real (CORREGIDO)
import os
import threading
from flask import Flask, jsonify
from monitor_mercado import monitor

app = Flask(__name__)

print("🚀 BOT TRADING - MONITOREO EN TIEMPO REAL")

# Variable para controlar si ya iniciamos el monitoreo
monitoreo_iniciado = False

@app.route('/')
def home():
    return jsonify({
        "status": "online", 
        "service": "Bot Trading - Detección en Tiempo Real",
        "modulos_activos": [
            "Monitor Mercado", "Estrategia DCA", "Gestor Operaciones", "Telegram Bot"
        ],
        "estadisticas": monitor.gestor.estadisticas,
        "operaciones_activas": len(monitor.gestor.operaciones_activas),
        "monitoreo_activo": monitor.monitoreando
    })

@app.route('/iniciar-monitoreo')
def iniciar_monitoreo():
    """Iniciar monitoreo en tiempo real"""
    global monitoreo_iniciado
    
    if not monitor.monitoreando:
        threading.Thread(target=monitor.iniciar_monitoreo, daemon=True).start()
        monitoreo_iniciado = True
        return jsonify({
            "status": "monitoreo_iniciado",
            "mensaje": "Monitoreo en tiempo real ACTIVADO"
        })
    return jsonify({"status": "ya_activo", "mensaje": "Monitoreo ya está activo"})

@app.route('/detener-monitoreo')
def detener_monitoreo():
    """Detener monitoreo"""
    monitor.detener_monitoreo()
    return jsonify({
        "status": "monitoreo_detenido", 
        "mensaje": "Monitoreo DETENIDO"
    })

@app.route('/estadisticas')
def estadisticas():
    return jsonify({
        "estadisticas": monitor.gestor.estadisticas,
        "operaciones_activas": monitor.gestor.operaciones_activas,
        "historial_reciente": monitor.gestor.historial[-5:] if monitor.gestor.historial else []
    })

@app.route('/forzar-señal/<par>')
def forzar_señal(par):
    """Forzar una señal manualmente (para testing)"""
    from estrategia_dca import EstrategiaDCA
    
    if par not in ['USDCAD', 'USDJPY', 'AUDUSD', 'EURGBP', 'GBPUSD']:
        return jsonify({"status": "error", "mensaje": "Par no válido"})
    
    estrategia = EstrategiaDCA()
    señal = estrategia.generar_señal_real(par)
    monitor.ejecutar_señal(señal)
    
    return jsonify({
        "status": "señal_forzada",
        "par": par,
        "señal": señal
    })

@app.route('/status')
def status():
    """Estado del sistema"""
    return jsonify({
        "monitoreo_activo": monitor.monitoreando,
        "operaciones_activas": len(monitor.gestor.operaciones_activas),
        "total_operaciones": monitor.gestor.estadisticas['total_operaciones'],
        "operaciones_ganadoras": monitor.gestor.estadisticas['operaciones_ganadoras'],
        "profit_total": monitor.gestor.estadisticas['profit_total']
    })

# Iniciar monitoreo automáticamente al primer request
@app.before_request
def iniciar_monitoreo_auto():
    global monitoreo_iniciado
    if not monitoreo_iniciado:
        print("🔄 Iniciando monitoreo automático...")
        threading.Thread(target=monitor.iniciar_monitoreo, daemon=True).start()
        monitoreo_iniciado = True

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Servidor iniciado en puerto {port}")
    print(f"🔍 Monitoreo en tiempo real: ACTIVADO AL PRIMER REQUEST")
    app.run(host="0.0.0.0", port=port, debug=False)
