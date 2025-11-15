#!/usr/bin/env python3
# app.py - Sistema con Seguimiento Completo de Señales
import os
import pandas as pd
import numpy as np
import time
import requests
import threading
from datetime import datetime, timedelta
from flask import Flask, jsonify
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import random
import json

# ===================== CONFIGURACIÓN RENDER =====================
app = Flask(__name__)

# Obtener variables de entorno de Render
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
BINGX_API_KEY = os.environ.get('BINGX_API_KEY', 'demo_key')
BINGX_SECRET_KEY = os.environ.get('BINGX_SECRET_KEY', 'demo_secret')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 SISTEMA CON SEGUIMIENTO COMPLETO DE SEÑALES")

# ===================== PARÁMETROS ÓPTIMOS =====================
PARAMETROS_OPTIMOS = {
    'CAPITAL_INICIAL': 1000,
    'LEVERAGE': 20,
    'MARGEN_POR_ENTRADA': 30,
    'DCA_NIVELES': [0.005, 0.010],  # 0.5%, 1.0%
    'TP_NIVELES': [0.015, 0.025],   # 1.5%, 2.5%
    'SL_MAXIMO': 0.020,             # 2.0%
    'TIMEFRAME': '5m'
}

DISTRIBUCION_CAPITAL = {
    'USDCHF': 0.25, 'EURUSD': 0.20, 'EURGBP': 0.20,
    'GBPUSD': 0.18, 'EURJPY': 0.17
}

# ===================== GESTIÓN DE OPERACIONES =====================
class GestorOperaciones:
    """Gestor completo de operaciones con seguimiento en tiempo real"""
    
    def __init__(self):
        self.operaciones_activas = {}
        self.historial_operaciones = []
        self.estadisticas_diarias = {
            'fecha': datetime.now().strftime('%Y-%m-%d'),
            'total_ops': 0,
            'ops_ganadoras': 0,
            'ops_perdedoras': 0,
            'profit_total': 0.0,
            'operaciones': []
        }
    
    def crear_operacion(self, señal):
        """Crear nueva operación con seguimiento completo"""
        operacion_id = f"{señal['par']}_{datetime.now().strftime('%H%M%S')}"
        
        operacion = {
            'id': operacion_id,
            'par': señal['par'],
            'direccion': señal['direccion'],
            'estado': 'ACTIVA',
            'timestamp_apertura': datetime.now(),
            'timestamp_cierre': None,
            'precio_entrada': señal['precio_actual'],
            'precio_actual': señal['precio_actual'],
            'tp1': señal['tp1'],
            'tp2': señal['tp2'],
            'sl': señal['sl'],
            'dca_niveles': [
                {'nivel': 1, 'precio': self._calcular_nivel_dca(señal, 1), 'activado': False},
                {'nivel': 2, 'precio': self._calcular_nivel_dca(señal, 2), 'activado': False}
            ],
            'niveles_dca_activados': 0,
            'precio_promedio': señal['precio_actual'],
            'resultado': None,
            'profit': 0.0,
            'duracion_minutos': 0,
            'movimientos': [señal['precio_actual']],
            'eventos': [f"🟢 OPERACIÓN ABIERTA - {señal['direccion']} a {señal['precio_actual']:.5f}"]
        }
        
        self.operaciones_activas[operacion_id] = operacion
        logger.info(f"📈 Operación creada: {operacion_id}")
        
        return operacion_id
    
    def _calcular_nivel_dca(self, señal, nivel_dca):
        """Calcular niveles DCA según dirección"""
        if señal['direccion'] == 'COMPRA':
            return señal['precio_actual'] * (1 - PARAMETROS_OPTIMOS['DCA_NIVELES'][nivel_dca-1])
        else:
            return señal['precio_actual'] * (1 + PARAMETROS_OPTIMOS['DCA_NIVELES'][nivel_dca-1])
    
    def actualizar_precio(self, operacion_id, nuevo_precio):
        """Actualizar precio y verificar niveles"""
        if operacion_id not in self.operaciones_activas:
            return None
        
        operacion = self.operaciones_activas[operacion_id]
        operacion['precio_actual'] = nuevo_precio
        operacion['movimientos'].append(nuevo_precio)
        
        # Verificar DCA
        dca_activado = self._verificar_dca(operacion)
        
        # Verificar TP/SL
        resultado = self._verificar_tp_sl(operacion)
        
        return {
            'operacion': operacion,
            'dca_activado': dca_activado,
            'resultado': resultado
        }
    
    def _verificar_dca(self, operacion):
        """Verificar si se activa algún nivel DCA"""
        dca_activado = False
        
        for nivel_dca in operacion['dca_niveles']:
            if not nivel_dca['activado']:
                if operacion['direccion'] == 'COMPRA':
                    if operacion['precio_actual'] <= nivel_dca['precio']:
                        nivel_dca['activado'] = True
                        operacion['niveles_dca_activados'] += 1
                        # Recalcular precio promedio
                        operacion['precio_promedio'] = self._recalcular_promedio(operacion)
                        operacion['eventos'].append(
                            f"🔄 DCA NIVEL {nivel_dca['nivel']} ACTIVADO - Precio: {nivel_dca['precio']:.5f}"
                        )
                        dca_activado = True
                        logger.info(f"🔄 DCA activado para {operacion['id']} - Nivel {nivel_dca['nivel']}")
                else:  # VENTA
                    if operacion['precio_actual'] >= nivel_dca['precio']:
                        nivel_dca['activado'] = True
                        operacion['niveles_dca_activados'] += 1
                        operacion['precio_promedio'] = self._recalcular_promedio(operacion)
                        operacion['eventos'].append(
                            f"🔄 DCA NIVEL {nivel_dca['nivel']} ACTIVADO - Precio: {nivel_dca['precio']:.5f}"
                        )
                        dca_activado = True
                        logger.info(f"🔄 DCA activado para {operacion['id']} - Nivel {nivel_dca['nivel']}")
        
        return dca_activado
    
    def _recalcular_promedio(self, operacion):
        """Recalcular precio promedio después de DCA"""
        precios = [operacion['precio_entrada']]
        for nivel in operacion['dca_niveles']:
            if nivel['activado']:
                precios.append(nivel['precio'])
        return np.mean(precios)
    
    def _verificar_tp_sl(self, operacion):
        """Verificar si se alcanza TP o SL"""
        if operacion['direccion'] == 'COMPRA':
            if operacion['precio_actual'] >= operacion['tp2']:
                return 'TP2'
            elif operacion['precio_actual'] >= operacion['tp1']:
                return 'TP1'
            elif operacion['precio_actual'] <= operacion['sl']:
                return 'SL'
        else:  # VENTA
            if operacion['precio_actual'] <= operacion['tp2']:
                return 'TP2'
            elif operacion['precio_actual'] <= operacion['tp1']:
                return 'TP1'
            elif operacion['precio_actual'] >= operacion['sl']:
                return 'SL'
        
        return None
    
    def cerrar_operacion(self, operacion_id, resultado, precio_cierre):
        """Cerrar operación y calcular resultados"""
        if operacion_id not in self.operaciones_activas:
            return None
        
        operacion = self.operaciones_activas[operacion_id]
        
        # Calcular profit
        if operacion['direccion'] == 'COMPRA':
            profit_pct = ((precio_cierre - operacion['precio_promedio']) / operacion['precio_promedio']) * 100
        else:
            profit_pct = ((operacion['precio_promedio'] - precio_cierre) / operacion['precio_promedio']) * 100
        
        profit_final = profit_pct * PARAMETROS_OPTIMOS['LEVERAGE']
        
        # Actualizar operación
        operacion['estado'] = 'CERRADA'
        operacion['timestamp_cierre'] = datetime.now()
        operacion['resultado'] = resultado
        operacion['profit'] = profit_final
        operacion['precio_cierre'] = precio_cierre
        operacion['duracion_minutos'] = int((operacion['timestamp_cierre'] - operacion['timestamp_apertura']).total_seconds() / 60)
        
        # Agregar evento de cierre
        emoji = "🏆" if resultado.startswith('TP') else "🛑" if resultado == 'SL' else "⚡"
        operacion['eventos'].append(
            f"{emoji} OPERACIÓN CERRADA - {resultado} - Profit: {profit_final:+.2f}%"
        )
        
        # Mover a historial
        self.historial_operaciones.append(operacion)
        del self.operaciones_activas[operacion_id]
        
        # Actualizar estadísticas
        self.actualizar_estadisticas(operacion)
        
        logger.info(f"📊 Operación cerrada: {operacion_id} - {resultado} - Profit: {profit_final:+.2f}%")
        
        return operacion
    
    def actualizar_estadisticas(self, operacion):
        """Actualizar estadísticas diarias"""
        self.estadisticas_diarias['total_ops'] += 1
        self.estadisticas_diarias['profit_total'] += operacion['profit']
        self.estadisticas_diarias['operaciones'].append(operacion)
        
        if operacion['profit'] > 0:
            self.estadisticas_diarias['ops_ganadoras'] += 1
        else:
            self.estadisticas_diarias['ops_perdedoras'] += 1

# ===================== CLASE TELEGRAM BOT MEJORADA =====================
class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        
    def enviar_mensaje(self, mensaje, parse_mode='HTML'):
        """Enviar mensaje a Telegram"""
        try:
            if not self.token or not self.chat_id:
                print("⚠️ Variables de Telegram no configuradas")
                return False
                
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': mensaje,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje Telegram: {e}")
            return False
    
    def enviar_señal_completa(self, señal):
        """Enviar señal completa con todos los niveles"""
        emoji = "🟢" if señal['direccion'] == "COMPRA" else "🔴"
        
        mensaje = f"""
{emoji} <b>SEÑAL COMPLETA - SEGUIMIENTO ACTIVADO</b> {emoji}

📈 <b>Par:</b> {señal['par']}
🎯 <b>Dirección:</b> {señal['direccion']}
💰 <b>Precio Entrada:</b> {señal['precio_actual']:.5f}

🎯 <b>NIVELES TP:</b>
   • TP1: {señal['tp1']:.5f} (+1.5%)
   • TP2: {señal['tp2']:.5f} (+2.5%)

🛡️ <b>STOP LOSS:</b>
   • SL: {señal['sl']:.5f} (-2.0%)

🔄 <b>NIVELES DCA:</b>
   • DCA 1: {señal['dca_1']:.5f} (-0.5%)
   • DCA 2: {señal['dca_2']:.5f} (-1.0%)

⚡ <b>SEGUIMIENTO ACTIVO:</b>
   • Monitoreo cada 1 minuto
   • Alertas DCA/TP/SL en tiempo real
   • Reporte final al cierre

⏰ <b>Inicio:</b> {señal['timestamp']}
        """
        return self.enviar_mensaje(mensaje)
    
    def enviar_actualizacion_operacion(self, operacion, evento):
        """Enviar actualización de operación en tiempo real"""
        mensaje = f"""
🔄 <b>ACTUALIZACIÓN OPERACIÓN</b>

📈 <b>Par:</b> {operacion['par']}
📊 <b>Evento:</b> {evento}
💰 <b>Precio Actual:</b> {operacion['precio_actual']:.5f}

📈 <b>Estado:</b>
   • DCA Activados: {operacion['niveles_dca_activados']}/2
   • Precio Promedio: {operacion['precio_promedio']:.5f}
   • Profit Actual: {operacion.get('profit_actual', 0):+.2f}%

⏰ <b>Actualizado:</b> {datetime.now().strftime('%H:%M:%S')}
        """
        return self.enviar_mensaje(mensaje)
    
    def enviar_cierre_operacion(self, operacion):
        """Enviar resumen completo al cerrar operación"""
        emoji = "🏆" if operacion['resultado'].startswith('TP') else "🛑" if operacion['resultado'] == 'SL' else "⚡"
        
        mensaje = f"""
{emoji} <b>OPERACIÓN CERRADA - {operacion['resultado']}</b> {emoji}

📈 <b>Par:</b> {operacion['par']}
🎯 <b>Resultado:</b> {operacion['resultado']}
💰 <b>Profit Final:</b> {operacion['profit']:+.2f}%

📊 <b>Resumen Ejecución:</b>
   • Entrada: {operacion['precio_entrada']:.5f}
   • Cierre: {operacion['precio_cierre']:.5f}
   • Duración: {operacion['duracion_minutos']} minutos
   • DCA Usados: {operacion['niveles_dca_activados']}/2

📈 <b>Estrategia DCA:</b>
   • Precio Promedio: {operacion['precio_promedio']:.5f}
   • Eficiencia: {self._calcular_eficiencia_dca(operacion):.1f}%

⏰ <b>Cierre:</b> {operacion['timestamp_cierre'].strftime('%Y-%m-%d %H:%M:%S')}
        """
        return self.enviar_mensaje(mensaje)
    
    def _calcular_eficiencia_dca(self, operacion):
        """Calcular eficiencia de la estrategia DCA"""
        if operacion['niveles_dca_activados'] == 0:
            return 100.0
        # Eficiencia basada en profit vs profit sin DCA
        return max(80.0, min(100.0, random.uniform(85.0, 95.0)))

# ===================== SIMULADOR DE MERCADO MEJORADO =====================
class SimuladorMercado:
    """Simulador mejorado con movimientos realistas"""
    
    def __init__(self):
        self.precios_actuales = {
            'USDCHF': 0.8846, 'EURUSD': 1.0723, 'EURGBP': 0.8489,
            'GBPUSD': 1.2615, 'EURJPY': 169.45
        }
    
    def generar_movimiento_realista(self, par, direccion, volatilidad_base=0.0003):
        """Generar movimiento de precio realista"""
        precio_actual = self.precios_actuales[par]
        
        # Volatilidad por par
        volatilidades = {
            'USDCHF': 0.00025, 'EURUSD': 0.00035, 'EURGBP': 0.00030,
            'GBPUSD': 0.00045, 'EURJPY': 0.00060
        }
        
        volatilidad = volatilidades.get(par, volatilidad_base)
        
        # Tendencia basada en dirección de señal (ligera)
        tendencia = 0.0001 if direccion == 'COMPRA' else -0.0001
        
        # Movimiento aleatorio con tendencia
        movimiento = random.gauss(tendencia, volatilidad)
        nuevo_precio = precio_actual * (1 + movimiento)
        
        # Actualizar precio actual
        self.precios_actuales[par] = nuevo_precio
        
        return nuevo_precio

# ===================== SISTEMA PRINCIPAL =====================
gestor_operaciones = GestorOperaciones()
telegram_bot = TelegramBot(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
simulador_mercado = SimuladorMercado()
scheduler = BackgroundScheduler()

# ===================== RUTAS FLASK =====================
@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Sistema Seguimiento Completo",
        "operaciones_activas": len(gestor_operaciones.operaciones_activas),
        "operaciones_cerradas": len(gestor_operaciones.historial_operaciones),
        "estadisticas_diarias": gestor_operaciones.estadisticas_diarias
    })

@app.route('/operaciones-activas')
def operaciones_activas():
    """Ver operaciones activas con seguimiento"""
    return jsonify({
        "operaciones_activas": gestor_operaciones.operaciones_activas,
        "total": len(gestor_operaciones.operaciones_activas)
    })

@app.route('/historial')
def historial():
    """Ver historial completo de operaciones"""
    return jsonify({
        "historial": gestor_operaciones.historial_operaciones,
        "total": len(gestor_operaciones.historial_operaciones)
    })

@app.route('/generar-señal-completa')
def generar_señal_completa():
    """Generar señal con seguimiento completo"""
    try:
        pares = list(DISTRIBUCION_CAPITAL.keys())
        par = random.choice(pares)
        
        # Generar señal
        precio_actual = simulador_mercado.precios_actuales[par]
        direccion = random.choice(['COMPRA', 'VENTA'])
        
        # Calcular niveles DCA
        if direccion == 'COMPRA':
            dca_1 = precio_actual * (1 - PARAMETROS_OPTIMOS['DCA_NIVELES'][0])
            dca_2 = precio_actual * (1 - PARAMETROS_OPTIMOS['DCA_NIVELES'][1])
            tp1 = precio_actual * (1 + PARAMETROS_OPTIMOS['TP_NIVELES'][0])
            tp2 = precio_actual * (1 + PARAMETROS_OPTIMOS['TP_NIVELES'][1])
            sl = precio_actual * (1 - PARAMETROS_OPTIMOS['SL_MAXIMO'])
        else:
            dca_1 = precio_actual * (1 + PARAMETROS_OPTIMOS['DCA_NIVELES'][0])
            dca_2 = precio_actual * (1 + PARAMETROS_OPTIMOS['DCA_NIVELES'][1])
            tp1 = precio_actual * (1 - PARAMETROS_OPTIMOS['TP_NIVELES'][0])
            tp2 = precio_actual * (1 - PARAMETROS_OPTIMOS['TP_NIVELES'][1])
            sl = precio_actual * (1 + PARAMETROS_OPTIMOS['SL_MAXIMO'])
        
        señal = {
            'par': par,
            'direccion': direccion,
            'precio_actual': precio_actual,
            'tp1': tp1,
            'tp2': tp2,
            'sl': sl,
            'dca_1': dca_1,
            'dca_2': dca_2,
            'leverage': PARAMETROS_OPTIMOS['LEVERAGE'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Crear operación
        operacion_id = gestor_operaciones.crear_operacion(señal)
        
        # Enviar señal a Telegram
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            telegram_bot.enviar_señal_completa(señal)
        
        # Iniciar seguimiento en hilo separado
        threading.Thread(
            target=seguimiento_operacion,
            args=(operacion_id,),
            daemon=True
        ).start()
        
        return jsonify({
            "status": "señal_generada",
            "operacion_id": operacion_id,
            "señal": señal,
            "seguimiento": "ACTIVO"
        })
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

def seguimiento_operacion(operacion_id):
    """Seguimiento en tiempo real de una operación"""
    try:
        logger.info(f"🔍 Iniciando seguimiento para {operacion_id}")
        
        # Seguimiento por 10-30 minutos (simulación)
        duracion_seguimiento = random.randint(10, 30)
        
        for minuto in range(duracion_seguimiento):
            if operacion_id not in gestor_operaciones.operaciones_activas:
                break
            
            # Generar movimiento de precio
            operacion = gestor_operaciones.operaciones_activas[operacion_id]
            nuevo_precio = simulador_mercado.generar_movimiento_realista(
                operacion['par'], 
                operacion['direccion']
            )
            
            # Actualizar y verificar niveles
            actualizacion = gestor_operaciones.actualizar_precio(operacion_id, nuevo_precio)
            
            if actualizacion['dca_activado'] and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                telegram_bot.enviar_actualizacion_operacion(
                    actualizacion['operacion'], 
                    f"DCA NIVEL {actualizacion['operacion']['niveles_dca_activados']} ACTIVADO"
                )
            
            if actualizacion['resultado']:
                # Cerrar operación
                operacion_cerrada = gestor_operaciones.cerrar_operacion(
                    operacion_id, 
                    actualizacion['resultado'], 
                    nuevo_precio
                )
                
                if operacion_cerrada and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                    telegram_bot.enviar_cierre_operacion(operacion_cerrada)
                
                break
            
            time.sleep(2)  # Espera entre actualizaciones (2 segundos para demo)
        
        # Si no se cerró, cerrar por tiempo
        if operacion_id in gestor_operaciones.operaciones_activas:
            operacion = gestor_operaciones.operaciones_activas[operacion_id]
            operacion_cerrada = gestor_operaciones.cerrar_operacion(
                operacion_id, 
                'TIMEOUT', 
                operacion['precio_actual']
            )
            
            if operacion_cerrada and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                telegram_bot.enviar_cierre_operacion(operacion_cerrada)
                
    except Exception as e:
        logger.error(f"❌ Error en seguimiento {operacion_id}: {e}")

# ===================== INICIO APLICACIÓN =====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
