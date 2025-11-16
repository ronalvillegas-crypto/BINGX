#!/usr/bin/env python3
# app.py - Servidor principal que une todos los módulos
import os
import time
import random
import threading
from flask import Flask, jsonify
from config import TOP_5_PARES
from estrategia_dca import EstrategiaDCA
from gestor_operaciones import GestorOperaciones
from telegram_bot import TelegramBotReal

app = Flask(__name__)

# Inicializar módulos
estrategia = EstrategiaDCA()
gestor = GestorOperaciones()
telegram = TelegramBotReal()

print("🚀 BOT TRADING REAL INICIADO - ARQUITECTURA MODULAR")

def seguir_operacion(operacion_id):
    """Seguir operación en tiempo real"""
    for _ in range(10):  # 10 actualizaciones
        time.sleep(5)  # Cada 5 segundos
        
        resultado = gestor.simular_seguimiento(operacion_id)
        
        if resultado and resultado['resultado']:
            # Operación cerrada - enviar notificación
            telegram.enviar_cierre_operacion(resultado['operacion'])
            break

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Bot Trading Real - Arquitectura Modular",
        "modulos_activos": [
            "Estrategia DCA", "Gestor Operaciones", "Telegram Bot"
        ],
        "estadisticas": gestor.estadisticas,
        "operaciones_activas": len(gestor.operaciones_activas)
    })

@app.route('/generar-operacion-real')
def generar_operacion_real():
    """Generar operación REAL con estrategia completa"""
    try:
        # 1. Seleccionar par
        par = random.choice(TOP_5_PARES)
        
        # 2. Generar señal REAL
        señal = estrategia.generar_señal_real(par)
        
        # 3. Abrir operación
        operacion_id = gestor.abrir_operacion(señal)
        
        # 4. Enviar a Telegram
        telegram.enviar_señal_completa(señal)
        
        # 5. Iniciar seguimiento en hilo separado
        threading.Thread(
            target=seguir_operacion,
            args=(operacion_id,),
            daemon=True
        ).start()
        
        return jsonify({
            "status": "operacion_creada",
            "operacion_id": operacion_id,
            "señal": señal,
            "seguimiento": "ACTIVO"
        })
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route('/estadisticas-reales')
def estadisticas_reales():
    return jsonify({
        "estadisticas": gestor.estadisticas,
        "operaciones_activas": gestor.operaciones_activas,
        "historial_reciente": gestor.historial[-5:] if gestor.historial else []
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Servidor modular iniciado en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
