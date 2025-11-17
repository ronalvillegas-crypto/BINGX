# app.py - CON TODOS LOS ACTIVOS
import os
import time
import threading
from flask import Flask, jsonify

print("🚀 INICIANDO BOT TRADING 24/7 - FOREX + MATERIAS PRIMAS")
print("🎯 ESTRATEGIA: S/R ETAPA 1 - 8 ACTIVOS")

# Inicializar e iniciar MONITOR inmediatamente
try:
    from monitor_mercado import MonitorMercado
    monitor = MonitorMercado()
    print("✅ Monitor inicializado correctamente")
    
    # Iniciar monitoreo en segundo plano
    def iniciar_bot():
        monitor.iniciar_monitoreo()
    
    hilo_bot = threading.Thread(target=iniciar_bot, daemon=True)
    hilo_bot.start()
    print("✅ Bot de trading iniciado en segundo plano")
    
except Exception as e:
    print(f"❌ Error iniciando bot: {e}")
    monitor = None

app = Flask(__name__)

@app.route('/')
def home():
    if monitor and monitor.monitoreando:
        estado = "TRADING_ACTIVO_24_7"
    else:
        estado = "INICIALIZANDO"
    
    return jsonify({
        "status": estado,
        "message": "🤖 BOT DE TRADING MULTI-ACTIVOS 24/7",
        "service": "Bot Trading - Forex + Materias Primas", 
        "estrategia": "S/R Etapa 1 - Backtesting Optimizado",
        "activos_monitoreados": {
            "forex": ["EURUSD", "USDCAD", "EURCHF", "EURAUD"],
            "materias_primas": ["XAUUSD (Oro)", "XAGUSD (Plata)", "OILUSD (Petróleo)", "XPTUSD (Platino)"]
        },
        "total_activos": 8,
        "monitoreo_activo": monitor.monitoreando if monitor else False,
        "operaciones_activas": len(monitor.gestor.operaciones_activas) if monitor else 0,
        "nota": "BUCLE INFINITO INTENCIONAL - DISEÑADO PARA 24/7"
    })

@app.route('/status')
def status():
    return jsonify({
        "status": "OPERACIONAL_MULTI_ACTIVOS",
        "bot_activo": monitor.monitoreando if monitor else False,
        "estrategia": "S/R Etapa 1 - Forex & Commodities",
        "total_pares": 8,
        "categorias": ["Forex (4)", "Materias Primas (4)"]
    })

@app.route('/activos')
def activos():
    return jsonify({
        "forex": {
            "EURUSD": "Euro/Dólar",
            "USDCAD": "Dólar/Dólar Canadiense", 
            "EURCHF": "Euro/Franco Suizo",
            "EURAUD": "Euro/Dólar Australiano"
        },
        "materias_primas": {
            "XAUUSD": "Oro",
            "XAGUSD": "Plata",
            "OILUSD": "Petróleo Crudo",
            "XPTUSD": "Platino"
        }
    })

@app.route('/forzar-señal/<par>')
def forzar_señal(par):
    """Forzar una señal manualmente (para testing)"""
    if monitor is None:
        return jsonify({"status": "error", "message": "Monitor no disponible"})
    
    # PERMITIR TODOS LOS PARES (Forex + Commodities)
    pares_permitidos = ['EURUSD', 'USDCAD', 'EURCHF', 'EURAUD', 'XAUUSD', 'XAGUSD', 'OILUSD', 'XPTUSD']
    
    if par not in pares_permitidos:
        return jsonify({"status": "error", "mensaje": f"Par no válido. Pares permitidos: {pares_permitidos}"})
    
    from estrategia_dca import EstrategiaDCA
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Servidor web iniciado en puerto {port}")
    print(f"📊 Monitoreando 8 activos: 4 Forex + 4 Materias Primas")
    print(f"💡 Estrategia única: S/R Etapa 1 para todos los activos")
    app.run(host="0.0.0.0", port=port, debug=False)
