# app.py - Servidor con monitoreo optimizado
import os
import threading
from flask import Flask, jsonify
from monitor_mercado import monitor

app = Flask(__name__)

print("🚀 BOT TRADING OPTIMIZADO - ESTRATEGIA S/R ETAPA 1")
print("🎯 Pares activos: EURUSD, USDCAD, EURCHF, EURAUD")

# Variable para controlar si ya iniciamos el monitoreo
monitoreo_iniciado = False

@app.route('/')
def home():
    return jsonify({
        "status": "online", 
        "service": "Bot Trading Optimizado - Estrategia S/R Etapa 1",
        "pares_activos": ["EURUSD", "USDCAD", "EURCHF", "EURAUD"],
        "estrategia": "S/R Etapa 1 Optimizada",
        "modulos_activos": [
            "Monitor Mercado", "Estrategia DCA", "Gestor Operaciones", "Telegram Bot"
        ],
        "estadisticas": monitor.gestor.estadisticas,
        "operaciones_activas": len(monitor.gestor.operaciones_activas),
        "monitoreo_activo": monitor.monitoreando,
        "riesgo": monitor.obtener_estadisticas_riesgo()
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
            "mensaje": "Monitoreo S/R Etapa 1 ACTIVADO",
            "pares": ["EURUSD", "USDCAD", "EURCHF", "EURAUD"]
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
        "historial_reciente": monitor.gestor.historial[-5:] if monitor.gestor.historial else [],
        "riesgo": monitor.obtener_estadisticas_riesgo()
    })

@app.route('/forzar-señal/<par>')
def forzar_señal(par):
    """Forzar una señal manualmente (para testing)"""
    from estrategia_dca import EstrategiaDCA
    
    if par not in ['EURUSD', 'USDCAD', 'EURCHF', 'EURAUD']:
        return jsonify({"status": "error", "mensaje": "Par no válido. Pares permitidos: EURUSD, USDCAD, EURCHF, EURAUD"})
    
    estrategia = EstrategiaDCA()
    señal = estrategia.generar_señal_real(par)
    
    if señal:
        monitor.ejecutar_señal(señal)
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
    return jsonify({
        "monitoreo_activo": monitor.monitoreando,
        "operaciones_activas": len(monitor.gestor.operaciones_activas),
        "total_operaciones": monitor.gestor.estadisticas['total_operaciones'],
        "operaciones_ganadoras": monitor.gestor.estadisticas['operaciones_ganadoras'],
        "profit_total": monitor.gestor.estadisticas['profit_total'],
        "estrategia": "S/R Etapa 1 Optimizada",
        "pares_activos": ["EURUSD", "USDCAD", "EURCHF", "EURAUD"]
    })

# Iniciar monitoreo automáticamente al primer request
@app.before_request
def iniciar_monitoreo_auto():
    global monitoreo_iniciado
    if not monitoreo_iniciado:
        print("🔄 Iniciando monitoreo automático S/R Etapa 1...")
        threading.Thread(target=monitor.iniciar_monitoreo, daemon=True).start()
        monitoreo_iniciado = True

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Servidor optimizado iniciado en puerto {port}")
    print(f"🔍 Monitoreo S/R Etapa 1: ACTIVADO AL PRIMER REQUEST")
    app.run(host="0.0.0.0", port=port, debug=False)
