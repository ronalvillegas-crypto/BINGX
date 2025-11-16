# app.py - Servidor con monitoreo en tiempo real
import os
import threading
from flask import Flask, jsonify
from monitor_mercado import monitor

app = Flask(__name__)

print("🚀 BOT TRADING - MONITOREO EN TIEMPO REAL")

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
    if not monitor.monitoreando:
        threading.Thread(target=monitor.iniciar_monitoreo, daemon=True).start()
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
    from gestor_operaciones import GestorOperaciones
    
    estrategia = EstrategiaDCA()
    señal = estrategia.generar_señal_real(par)
    monitor.ejecutar_señal(señal)
    
    return jsonify({
        "status": "señal_forzada",
        "par": par,
        "señal": señal
    })

# Iniciar monitoreo automáticamente al deploy
@app.before_first_request
def iniciar_auto():
    print("🔄 Iniciando monitoreo automático...")
    threading.Thread(target=monitor.iniciar_monitoreo, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Servidor iniciado en puerto {port}")
    print(f"🔍 Monitoreo en tiempo real: ACTIVADO")
    app.run(host="0.0.0.0", port=port, debug=False)
