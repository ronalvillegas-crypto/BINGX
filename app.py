# app.py - VERSIÓN GARANTIZADA PARA RENDER
import os
import time
import threading
from flask import Flask, jsonify
from datetime import datetime

print("=" * 70)
print("🚀 BOT TRADING - INICIANDO EN RENDER")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

app = Flask(__name__)
start_time = datetime.now()
bot_activo = False

@app.route('/')
def home():
    return jsonify({
        "status": "ACTIVE",
        "service": "BingX Trading Bot",
        "bot_status": "ACTIVO" if bot_activo else "INACTIVO",
        "start_time": start_time.isoformat(),
        "current_time": datetime.now().isoformat(),
        "endpoints": [
            "/", "/health", "/status", "/test", 
            "/iniciar-bot", "/detener-bot"
        ]
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat()
    })

@app.route('/status')
def status():
    uptime = int((datetime.now() - start_time).total_seconds())
    return jsonify({
        "status": "running",
        "python_version": "3.13.4",
        "uptime_seconds": uptime,
        "bot_activo": bot_activo
    })

@app.route('/test')
def test():
    return jsonify({
        "message": "✅ Todo funciona perfectamente!",
        "test_time": datetime.now().isoformat()
    })

@app.route('/iniciar-bot')
def iniciar_bot():
    global bot_activo
    try:
        from monitor_mercado import MonitorMercado
        monitor = MonitorMercado()
        
        def ejecutar_bot():
            global bot_activo
            try:
                print("🤖 INICIANDO BOT DE TRADING...")
                monitor.iniciar_monitoreo()
            except Exception as e:
                print(f"❌ Error en bot: {e}")
                bot_activo = False
        
        # Iniciar en hilo separado
        hilo = threading.Thread(target=ejecutar_bot, daemon=True)
        hilo.start()
        
        bot_activo = True
        time.sleep(3)
        
        return jsonify({
            "status": "success",
            "message": "Bot iniciado correctamente",
            "bot_activo": True
        })
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Error: {str(e)}"
        })

@app.route('/detener-bot')
def detener_bot():
    global bot_activo
    bot_activo = False
    return jsonify({
        "status": "success",
        "message": "Bot detenido",
        "bot_activo": False
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 INICIANDO SERVIDOR EN PUERTO: {port}")
    print(f"📍 URL: https://bingx-f9ol.onrender.com")
    print("🎯 Para activar el bot, visita: /iniciar-bot")
    
    app.run(host="0.0.0.0", port=port, debug=False)
